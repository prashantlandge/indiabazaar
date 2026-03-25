import logging

import numpy as np

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            import os
            # Skip model download if HF hub is unreachable
            if os.environ.get("SKIP_MODEL_DOWNLOAD"):
                return None
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Sentence-transformers model unavailable, using fallback: {e}")
            return None
    return _model


def generate_embedding(text: str) -> list[float] | None:
    """Generate a 384-dimensional embedding for the given text."""
    model = _get_model()
    if model is not None:
        try:
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")

    # Fallback: deterministic hash-based embedding when model unavailable
    return _fallback_embedding(text)


def _fallback_embedding(text: str) -> list[float]:
    """Generate a deterministic 384-dim embedding using hashing.
    Not as good as a real model but enables vector search to function."""
    import hashlib
    tokens = text.lower().split()
    vec = np.zeros(384, dtype=np.float32)
    for i, token in enumerate(tokens):
        h = hashlib.sha256(token.encode()).digest()
        for j in range(0, min(len(h), 32)):
            idx = (j * 12 + i) % 384
            vec[idx] += (h[j] - 128) / 128.0
    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def generate_embeddings_batch(texts: list[str]) -> list[list[float] | None]:
    """Generate embeddings for a batch of texts."""
    model = _get_model()
    if model is not None:
        try:
            embeddings = model.encode(texts, normalize_embeddings=True, batch_size=64)
            return [e.tolist() for e in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
    return [_fallback_embedding(t) for t in texts]


def build_supplier_text(supplier_data: dict) -> str:
    """Build embedding input text from supplier data."""
    parts = [
        supplier_data.get("company_name", ""),
        supplier_data.get("city", ""),
        supplier_data.get("nature_of_business", ""),
    ]
    certs = supplier_data.get("certifications")
    if certs and isinstance(certs, list):
        parts.append(" ".join(certs))

    products = supplier_data.get("products", [])
    if products:
        product_names = [p.get("name", "") for p in products[:5]]
        parts.extend(product_names)
        for p in products[:3]:
            if p.get("description"):
                parts.append(p["description"][:200])

    return " ".join(filter(None, parts))


def build_product_text(product_data: dict) -> str:
    """Build embedding input text from product data."""
    parts = [
        product_data.get("name", ""),
        product_data.get("description", ""),
        product_data.get("category", ""),
        product_data.get("subcategory", ""),
    ]
    specs = product_data.get("specs", {})
    if isinstance(specs, dict):
        parts.extend(str(v) for v in specs.values())

    return " ".join(filter(None, parts))
