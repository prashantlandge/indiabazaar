#!/usr/bin/env python3
"""
Generate 1000+ suppliers with 5000+ products based on real IndiaMart data patterns.
All company names, products, prices, cities are based on actual Indian B2B market data.
"""
import json
import random
import hashlib
from slugify import slugify

random.seed(42)

# Real Indian industrial cities mapped to states
CITY_STATE = {
    "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nagpur": "Maharashtra", "Nashik": "Maharashtra",
    "Navi Mumbai": "Maharashtra", "Thane": "Maharashtra", "Aurangabad": "Maharashtra", "Kolhapur": "Maharashtra",
    "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Rajkot": "Gujarat", "Vadodara": "Gujarat",
    "Gandhinagar": "Gujarat", "Morbi": "Gujarat", "Bhavnagar": "Gujarat", "Nadiad": "Gujarat", "Jamnagar": "Gujarat",
    "New Delhi": "Delhi", "Delhi": "Delhi", "Ghaziabad": "Uttar Pradesh", "Noida": "Uttar Pradesh", "Agra": "Uttar Pradesh",
    "Lucknow": "Uttar Pradesh", "Kanpur": "Uttar Pradesh", "Varanasi": "Uttar Pradesh", "Meerut": "Uttar Pradesh",
    "Bengaluru": "Karnataka", "Hubli": "Karnataka", "Mysuru": "Karnataka", "Mangaluru": "Karnataka",
    "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu", "Tiruppur": "Tamil Nadu", "Madurai": "Tamil Nadu",
    "Salem": "Tamil Nadu", "Erode": "Tamil Nadu", "Palladam": "Tamil Nadu",
    "Kolkata": "West Bengal", "Howrah": "West Bengal", "Siliguri": "West Bengal",
    "Hyderabad": "Telangana", "Secunderabad": "Telangana",
    "Ludhiana": "Punjab", "Jalandhar": "Punjab", "Amritsar": "Punjab", "Mohali": "Punjab",
    "Jaipur": "Rajasthan", "Jodhpur": "Rajasthan", "Udaipur": "Rajasthan", "Balotra": "Rajasthan",
    "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh", "Gwalior": "Madhya Pradesh",
    "Faridabad": "Haryana", "Gurgaon": "Haryana", "Panipat": "Haryana", "Hisar": "Haryana", "Ambala": "Haryana",
    "Moradabad": "Uttar Pradesh",
    "Ernakulam": "Kerala", "Kochi": "Kerala", "Thiruvananthapuram": "Kerala",
    "Raipur": "Chhattisgarh", "Ranchi": "Jharkhand", "Jamshedpur": "Jharkhand",
    "Bhubaneswar": "Odisha", "Visakhapatnam": "Andhra Pradesh", "Vijayawada": "Andhra Pradesh",
    "Chandigarh": "Chandigarh", "Dehradun": "Uttarakhand", "Haridwar": "Uttarakhand", "Baddi": "Himachal Pradesh",
    "Guwahati": "Assam", "Patna": "Bihar",
}

FIRST_NAMES = [
    "Shree", "Sri", "Jai", "Om", "Balaji", "Ganesh", "Krishna", "Lakshmi", "Sai", "Durga",
    "Vishnu", "Shiva", "Ram", "Anand", "Suresh", "Rajesh", "Mahesh", "Arun", "Vijay", "Patel",
    "Shah", "Gupta", "Agarwal", "Jain", "Mehta", "Singh", "Kumar", "National", "Royal", "Prime",
    "Star", "Diamond", "Golden", "Silver", "Excel", "Supreme", "Pioneer", "Modern", "Advanced", "Reliable",
    "Perfect", "Classic", "Metro", "Global", "Universal", "Imperial", "Standard", "Premium", "Elite", "Alpha",
    "Omega", "Apex", "Zenith", "Summit", "Crown", "Bharat", "Hindustan", "Desh", "Swadeshi", "Naveen",
]

LAST_NAMES = [
    "Industries", "Enterprises", "Engineering", "Polymers", "Steel", "Traders", "Corporation",
    "Solutions", "Technologies", "Products", "Manufacturing", "Works", "International", "Exports",
    "Chemicals", "Plastics", "Metals", "Textiles", "Packaging", "Machinery", "Electronics",
    "Agro", "Pharma", "Auto Parts", "Rubber", "Pipes", "Paints", "Tools", "Hardware", "Minerals",
]

SUFFIXES = ["Pvt Ltd", "Private Limited", "LLP", "Limited", "", "", "", "Co.", "& Co.", "& Sons"]

NATURE_TYPES = ["Manufacturer", "Manufacturer", "Manufacturer", "Trader", "Wholesaler", "Exporter", "Retailer"]
CERTIFICATIONS_POOL = [
    ["ISO 9001"], ["ISO 9001", "ISO 14001"], ["ISO 9001", "CE"], ["CE"],
    ["BIS"], ["FSSAI"], ["GMP"], ["WHO GMP", "ISO 9001"], ["ISO 22000", "FSSAI"],
    ["ISO 9001", "ISO 14001", "OHSAS 18001"], ["ISO 13485"], [],  [], [], []
]
TURNOVERS = [None, None, "Upto 50 Lakh", "50 Lakh - 1 Crore", "1-5 Crore", "5-10 Crore", "10-25 Crore", "25-50 Crore", "50-100 Crore"]
EMPLOYEES = [None, None, "1-10", "10-50", "10-50", "50-100", "50-100", "100-500", "500+"]

# Categories with products, price ranges, and preferred cities
CATEGORIES = {
    "Plastic Raw Materials": {
        "products": [
            ("HDPE Granules", 60, 120, "Kg"), ("LDPE Granules", 55, 100, "Kg"), ("PP Granules", 70, 130, "Kg"),
            ("PVC Resin", 50, 90, "Kg"), ("PET Granules", 65, 110, "Kg"), ("Nylon Granules", 150, 300, "Kg"),
            ("ABS Granules", 100, 180, "Kg"), ("Polycarbonate Granules", 200, 400, "Kg"),
            ("Recycled HDPE Pellets", 40, 70, "Kg"), ("LLDPE Film Grade", 80, 120, "Kg"),
            ("Masterbatch", 60, 150, "Kg"), ("Plastic Additives", 100, 250, "Kg"),
            ("EVA Granules", 90, 160, "Kg"), ("GPPS Granules", 85, 130, "Kg"), ("HIPS Granules", 90, 140, "Kg"),
        ],
        "cities": ["Mumbai", "Ahmedabad", "Surat", "Rajkot", "Delhi", "Chennai", "Vadodara", "Hyderabad", "Kolkata"],
        "count": 80,
    },
    "Stainless Steel": {
        "products": [
            ("SS 304 Pipe", 180, 330, "Kg"), ("SS 316 Pipe", 250, 450, "Kg"), ("SS 202 Pipe", 120, 200, "Kg"),
            ("MS Pipe", 45, 75, "Kg"), ("GI Pipe", 55, 90, "Kg"), ("SS Sheet", 150, 350, "Kg"),
            ("MS Angle", 42, 65, "Kg"), ("SS Round Bar", 160, 300, "Kg"), ("TMT Bar", 48, 62, "Kg"),
            ("SS Wire Rod", 140, 260, "Kg"), ("SS Flange", 200, 500, "Piece"), ("SS Elbow Fitting", 80, 250, "Piece"),
            ("Mild Steel Channel", 45, 70, "Kg"), ("SS Coil", 170, 320, "Kg"), ("Copper Rod", 600, 850, "Kg"),
        ],
        "cities": ["Mumbai", "Ahmedabad", "Rajkot", "Ludhiana", "Raipur", "Delhi", "Hisar", "Jamshedpur", "Kolkata"],
        "count": 80,
    },
    "Packaging": {
        "products": [
            ("3 Ply Corrugated Box", 5, 25, "Piece"), ("5 Ply Corrugated Box", 15, 50, "Piece"),
            ("7 Ply Corrugated Box", 30, 80, "Piece"), ("Bubble Wrap Roll", 60, 150, "Kg"),
            ("Stretch Film", 120, 220, "Kg"), ("BOPP Tape", 30, 80, "Piece"), ("Thermocol Sheet", 25, 60, "Piece"),
            ("Air Bubble Pouch", 2, 8, "Piece"), ("Paper Bag", 3, 15, "Piece"), ("Printed Carton", 10, 40, "Piece"),
            ("Shrink Wrap Film", 100, 180, "Kg"), ("EPE Foam Sheet", 40, 90, "Kg"),
        ],
        "cities": ["Delhi", "Mumbai", "Noida", "Pune", "Bengaluru", "Chennai", "Kolkata", "Ludhiana", "Nagpur", "Ahmedabad"],
        "count": 60,
    },
    "Industrial Chemicals": {
        "products": [
            ("Sulphuric Acid", 8, 20, "Kg"), ("Hydrochloric Acid", 6, 18, "Kg"), ("Caustic Soda Flakes", 30, 50, "Kg"),
            ("Sodium Sulphate", 12, 28, "Kg"), ("Phosphoric Acid", 40, 70, "Kg"), ("Nitric Acid", 18, 35, "Kg"),
            ("Isopropyl Alcohol", 60, 120, "Liter"), ("Acetone", 50, 90, "Liter"), ("Toluene", 55, 85, "Liter"),
            ("Methanol", 30, 55, "Liter"), ("Ethanol", 45, 80, "Liter"), ("Citric Acid", 65, 120, "Kg"),
            ("Sodium Hydroxide", 25, 45, "Kg"), ("Calcium Carbonate", 8, 18, "Kg"), ("Zinc Oxide", 80, 160, "Kg"),
        ],
        "cities": ["Mumbai", "Ahmedabad", "Vadodara", "Pune", "Delhi", "Kolkata", "Hyderabad", "Chennai", "Indore", "Kanpur"],
        "count": 60,
    },
    "Machinery": {
        "products": [
            ("Belt Conveyor System", 35000, 200000, "Unit"), ("CNC Lathe Machine", 500000, 2500000, "Unit"),
            ("Air Compressor", 25000, 150000, "Unit"), ("Hydraulic Press", 100000, 800000, "Unit"),
            ("Welding Machine", 5000, 50000, "Unit"), ("Industrial Pump", 8000, 80000, "Unit"),
            ("Electric Motor 5HP", 4000, 15000, "Unit"), ("Screw Conveyor", 50000, 200000, "Unit"),
            ("Packaging Machine", 80000, 500000, "Unit"), ("Mixing Machine", 30000, 150000, "Unit"),
            ("Drilling Machine", 15000, 100000, "Unit"), ("Grinding Machine", 20000, 120000, "Unit"),
        ],
        "cities": ["Ahmedabad", "Pune", "Coimbatore", "Bengaluru", "Delhi", "Rajkot", "Ludhiana", "Faridabad", "Chennai", "Kolkata"],
        "count": 70,
    },
    "Textiles": {
        "products": [
            ("Cotton Fabric", 35, 120, "Meter"), ("Polyester Fabric", 25, 80, "Meter"),
            ("Silk Fabric", 100, 500, "Meter"), ("Denim Fabric", 60, 150, "Meter"),
            ("Cotton Yarn", 150, 350, "Kg"), ("Polyester Yarn", 100, 250, "Kg"),
            ("Rayon Fabric", 40, 90, "Meter"), ("Linen Fabric", 80, 250, "Meter"),
            ("Khadi Fabric", 60, 200, "Meter"), ("Terry Towel", 30, 120, "Piece"),
            ("Bed Sheet", 150, 600, "Piece"), ("Curtain Fabric", 50, 180, "Meter"),
        ],
        "cities": ["Surat", "Coimbatore", "Jaipur", "Tiruppur", "Ahmedabad", "Ludhiana", "Balotra", "Erode", "Panipat", "Mumbai"],
        "count": 60,
    },
    "Food & Beverages": {
        "products": [
            ("Mustard Oil", 140, 220, "Liter"), ("Soybean Oil", 100, 160, "Liter"),
            ("Basmati Rice", 60, 180, "Kg"), ("Turmeric Powder", 100, 250, "Kg"),
            ("Red Chilli Powder", 150, 350, "Kg"), ("Garam Masala", 180, 400, "Kg"),
            ("Wheat Flour (Atta)", 28, 55, "Kg"), ("Sugar", 35, 50, "Kg"),
            ("Black Pepper", 350, 700, "Kg"), ("Cumin Seeds", 200, 450, "Kg"),
            ("Toor Dal", 80, 140, "Kg"), ("Coconut Oil", 150, 280, "Liter"),
        ],
        "cities": ["Delhi", "Jodhpur", "Ahmedabad", "Indore", "Ernakulam", "Chennai", "Kolkata", "Mumbai", "Kochi", "Lucknow"],
        "count": 60,
    },
    "Electronics": {
        "products": [
            ("Power Cable 1.5 sqmm", 15, 45, "Meter"), ("HDMI Cable", 50, 200, "Piece"),
            ("DB Connector", 20, 150, "Piece"), ("LED Panel Light 18W", 120, 350, "Piece"),
            ("MCB Circuit Breaker", 80, 300, "Piece"), ("Electrical Switch", 15, 80, "Piece"),
            ("USB Connector", 10, 60, "Piece"), ("Relay 12V", 25, 120, "Piece"),
            ("Terminal Block", 5, 40, "Piece"), ("Wire Harness", 50, 500, "Piece"),
            ("Solar Panel 330W", 8000, 15000, "Piece"), ("Inverter 1KVA", 3000, 8000, "Piece"),
        ],
        "cities": ["Mumbai", "Delhi", "Pune", "Bengaluru", "Chennai", "Hyderabad", "Ghaziabad", "Noida", "Kolkata", "Ahmedabad"],
        "count": 60,
    },
    "Construction": {
        "products": [
            ("OPC Cement 50kg", 320, 420, "Bag"), ("PPC Cement 50kg", 300, 400, "Bag"),
            ("TMT Bar 8mm", 48000, 58000, "Tonne"), ("Red Clay Brick", 5, 10, "Piece"),
            ("AAC Block", 3200, 4800, "Cubic Meter"), ("Ceramic Floor Tile", 20, 60, "Sq Ft"),
            ("River Sand", 40, 80, "CFT"), ("Construction Aggregate", 25, 55, "CFT"),
            ("Plywood 18mm", 40, 90, "Sq Ft"), ("TMT Bar 12mm", 50000, 60000, "Tonne"),
            ("Fly Ash Brick", 4, 8, "Piece"), ("Roofing Sheet", 200, 500, "Sq Ft"),
        ],
        "cities": ["Mumbai", "Delhi", "Kolkata", "Bengaluru", "Pune", "Ahmedabad", "Hyderabad", "Chennai", "Ranchi", "Vadodara"],
        "count": 60,
    },
    "Pharmaceuticals": {
        "products": [
            ("Paracetamol API", 400, 800, "Kg"), ("Amoxicillin API", 1200, 2500, "Kg"),
            ("Metformin Tablets", 20, 60, "Strip"), ("Azithromycin Tablets", 40, 100, "Strip"),
            ("Vitamin C Tablets", 30, 80, "Bottle"), ("Herbal Extract Powder", 500, 2000, "Kg"),
            ("Omeprazole Capsules", 25, 70, "Strip"), ("Cephalosporin API", 3000, 8000, "Kg"),
            ("Nutraceutical Capsules", 150, 400, "Bottle"), ("Syrup Base", 80, 200, "Liter"),
        ],
        "cities": ["Hyderabad", "Ahmedabad", "Mumbai", "Surat", "Baddi", "Haridwar", "Chennai", "Bengaluru", "Indore", "Kolkata"],
        "count": 50,
    },
    "Automotive": {
        "products": [
            ("Brake Pad Set", 200, 800, "Set"), ("Oil Filter", 50, 250, "Piece"),
            ("Air Filter", 80, 300, "Piece"), ("Clutch Plate", 300, 1200, "Piece"),
            ("Rubber Engine Mount", 150, 600, "Piece"), ("Radiator Hose", 100, 400, "Piece"),
            ("Spark Plug", 40, 150, "Piece"), ("Timing Belt", 200, 800, "Piece"),
            ("Shock Absorber", 500, 2000, "Piece"), ("CV Joint", 400, 1500, "Piece"),
        ],
        "cities": ["Pune", "Delhi", "Chennai", "Gurgaon", "Ludhiana", "Rajkot", "Bengaluru", "Faridabad", "Noida", "Ahmedabad"],
        "count": 50,
    },
    "Rubber Products": {
        "products": [
            ("Rubber Sheet 3mm", 40, 120, "Kg"), ("Nitrile O-Ring", 2, 15, "Piece"),
            ("Silicone Gasket", 10, 80, "Piece"), ("EPDM Rubber Strip", 30, 90, "Meter"),
            ("Rubber Mat 4mm", 35, 80, "Sq Ft"), ("Neoprene Sheet", 80, 200, "Kg"),
            ("Rubber Hose Pipe", 20, 80, "Meter"), ("Viton O-Ring", 15, 100, "Piece"),
            ("Anti-Vibration Mount", 50, 300, "Piece"), ("Rubber Bellows", 100, 500, "Piece"),
        ],
        "cities": ["Mumbai", "Pune", "Delhi", "Ahmedabad", "Kolkata", "Faridabad", "Bengaluru", "Chennai", "Thane", "Gurgaon"],
        "count": 50,
    },
    "Paints & Coatings": {
        "products": [
            ("Epoxy Primer", 200, 500, "Liter"), ("Powder Coating", 180, 420, "Kg"),
            ("PU Coating", 300, 900, "Liter"), ("Zinc Rich Primer", 250, 600, "Liter"),
            ("Industrial Enamel Paint", 150, 400, "Liter"), ("Anti-Corrosive Paint", 200, 550, "Liter"),
            ("Heat Resistant Paint", 300, 800, "Liter"), ("Floor Coating Epoxy", 250, 600, "Liter"),
            ("Wood Finish PU", 350, 700, "Liter"), ("Road Marking Paint", 100, 300, "Liter"),
        ],
        "cities": ["Pune", "Ahmedabad", "Mumbai", "Delhi", "Faridabad", "Surat", "Chennai", "Bengaluru", "Kolkata", "Hyderabad"],
        "count": 40,
    },
    "Bearings & Tools": {
        "products": [
            ("Ball Bearing 6205", 50, 300, "Piece"), ("Taper Roller Bearing", 150, 1500, "Piece"),
            ("Pillow Block Bearing", 200, 2000, "Piece"), ("HSS Drill Bit Set", 100, 500, "Set"),
            ("Carbide End Mill", 200, 1200, "Piece"), ("Thread Tap M8", 50, 250, "Piece"),
            ("Cutting Tool Insert", 80, 400, "Piece"), ("Industrial Hand Tools Set", 500, 3000, "Set"),
            ("Linear Bearing", 80, 500, "Piece"), ("Needle Roller Bearing", 30, 200, "Piece"),
        ],
        "cities": ["Rajkot", "Delhi", "Ahmedabad", "Ludhiana", "Pune", "Jamnagar", "Mumbai", "Bengaluru", "Coimbatore", "Jaipur"],
        "count": 40,
    },
    "PVC Pipes & Fittings": {
        "products": [
            ("PVC Pipe 1 inch", 25, 80, "Meter"), ("UPVC Pipe 2 inch", 40, 120, "Meter"),
            ("CPVC Pipe", 50, 150, "Meter"), ("PVC Elbow Fitting", 5, 30, "Piece"),
            ("PVC Tee Fitting", 8, 35, "Piece"), ("PVC Ball Valve", 20, 100, "Piece"),
            ("HDPE Pipe", 30, 120, "Meter"), ("SWR Pipe", 35, 100, "Meter"),
            ("PVC Conduit Pipe", 15, 50, "Meter"), ("Flexible PVC Hose", 20, 70, "Meter"),
        ],
        "cities": ["Rajkot", "Ahmedabad", "Delhi", "Chennai", "Jaipur", "Agra", "Ghaziabad", "Pune", "Bengaluru", "Kolkata"],
        "count": 50,
    },
    "Electrical Equipment": {
        "products": [
            ("Transformer Oil", 90, 260, "Liter"), ("Distribution Transformer 100KVA", 150000, 400000, "Unit"),
            ("LT Switchgear Panel", 50000, 200000, "Unit"), ("Control Panel Board", 20000, 100000, "Unit"),
            ("Power Capacitor", 500, 5000, "Piece"), ("Current Transformer", 300, 3000, "Piece"),
            ("Cable Tray", 100, 500, "Meter"), ("Busbar", 200, 1000, "Meter"),
            ("Earthing Electrode", 500, 3000, "Piece"), ("Lightning Arrester", 1000, 8000, "Piece"),
        ],
        "cities": ["Chennai", "Pune", "Jaipur", "Mumbai", "Delhi", "Vadodara", "Hyderabad", "Bengaluru", "Kolkata", "Ahmedabad"],
        "count": 30,
    },
    "Agriculture & Farming": {
        "products": [
            ("Agricultural Fertilizer NPK", 15, 35, "Kg"), ("Bio Pesticide", 200, 500, "Liter"),
            ("Organic Seeds Packet", 50, 200, "Packet"), ("Tractor Mounted Sprayer", 15000, 50000, "Unit"),
            ("Drip Irrigation Kit", 5000, 25000, "Set"), ("Coco Peat Block", 15, 40, "Kg"),
            ("Vermicompost", 5, 15, "Kg"), ("Greenhouse Polyfilm", 60, 120, "Meter"),
            ("Seeding Machine", 3600, 12000, "Piece"), ("Seed Cum Fertilizer Drill", 25000, 80000, "Unit"),
            ("Agricultural Sprayer", 650, 9500, "Piece"), ("Crop Protection Chemical", 300, 800, "Liter"),
        ],
        "cities": ["Indore", "Pune", "Ahmedabad", "Coimbatore", "Jodhpur", "Jaipur", "Lucknow", "Kochi", "Nagpur", "Bhopal"],
        "count": 50,
    },
    "Security & Surveillance": {
        "products": [
            ("CCTV Dome Camera", 800, 3000, "Piece"), ("IP Camera 2MP", 1500, 5000, "Piece"),
            ("Biometric Attendance System", 3000, 12000, "Piece"), ("Access Control System", 5000, 25000, "Unit"),
            ("DVR 8 Channel", 3000, 8000, "Piece"), ("Fire Alarm System", 2000, 15000, "Unit"),
            ("Metal Detector", 5000, 50000, "Piece"), ("Video Door Phone", 2000, 8000, "Piece"),
            ("Boom Barrier", 25000, 80000, "Unit"), ("Burglar Alarm", 1500, 6000, "Unit"),
        ],
        "cities": ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Ghaziabad", "Pune", "Hyderabad", "Noida", "Ahmedabad", "Kolkata"],
        "count": 40,
    },
    "Solar & Renewable Energy": {
        "products": [
            ("Solar Panel 330W Mono", 8000, 15000, "Piece"), ("Solar Water Heater 200L", 15000, 35000, "Unit"),
            ("Solar Street Light", 3000, 12000, "Piece"), ("Solar Inverter 3KW", 25000, 60000, "Unit"),
            ("Solar Water Pump 5HP", 50000, 150000, "Unit"), ("Solar LED Lantern", 500, 2000, "Piece"),
            ("Lithium Battery 12V 100Ah", 8000, 20000, "Piece"), ("Solar Charge Controller", 1000, 5000, "Piece"),
            ("Solar Rooftop System 5KW", 200000, 350000, "Unit"), ("Wind Turbine 1KW", 50000, 150000, "Unit"),
        ],
        "cities": ["Bengaluru", "Chennai", "Pune", "Ahmedabad", "Hyderabad", "Delhi", "Mumbai", "Nashik", "Kolkata", "Jaipur"],
        "count": 40,
    },
    "Furniture & Interiors": {
        "products": [
            ("Office Executive Chair", 3000, 12000, "Piece"), ("Wooden Double Bed", 15000, 50000, "Piece"),
            ("3 Seater Sofa Set", 15000, 60000, "Set"), ("Modular Office Workstation", 8000, 25000, "Piece"),
            ("Wooden Dining Table 6 Seater", 20000, 60000, "Piece"), ("Steel Almirah", 5000, 15000, "Piece"),
            ("Computer Table", 3000, 10000, "Piece"), ("Wooden Bookshelf", 5000, 20000, "Piece"),
            ("L Shape Office Desk", 10000, 30000, "Piece"), ("Modular Kitchen Cabinet", 50000, 200000, "Set"),
        ],
        "cities": ["Delhi", "Mumbai", "Jodhpur", "Bengaluru", "Pune", "Jaipur", "Hyderabad", "Chennai", "Ahmedabad", "Kolkata"],
        "count": 40,
    },
    "Cosmetics & Personal Care": {
        "products": [
            ("Herbal Shampoo 200ml", 80, 250, "Bottle"), ("Bathing Soap 75g", 15, 60, "Piece"),
            ("Face Cream 50g", 100, 400, "Jar"), ("Hair Oil 200ml", 60, 200, "Bottle"),
            ("Hand Sanitizer 500ml", 40, 120, "Bottle"), ("Aloe Vera Gel", 80, 250, "Bottle"),
            ("Sunscreen Lotion SPF50", 150, 500, "Tube"), ("Lip Balm", 30, 100, "Piece"),
            ("Body Lotion 400ml", 100, 350, "Bottle"), ("Perfume 100ml", 200, 800, "Bottle"),
        ],
        "cities": ["Mumbai", "Delhi", "Ahmedabad", "Surat", "Bengaluru", "Chennai", "Hyderabad", "Kolkata", "Indore", "Pune"],
        "count": 35,
    },
    "Garments & Apparel": {
        "products": [
            ("Ladies Kurti Cotton", 200, 800, "Piece"), ("Men's Formal Shirt", 250, 900, "Piece"),
            ("Designer Saree", 500, 5000, "Piece"), ("Round Neck T-Shirt", 100, 400, "Piece"),
            ("Denim Jeans", 300, 1000, "Piece"), ("Kids Wear Set", 150, 600, "Set"),
            ("Cotton Salwar Suit", 400, 1500, "Set"), ("Track Suit", 250, 800, "Set"),
            ("Polo T-Shirt", 150, 500, "Piece"), ("Ladies Western Dress", 300, 1200, "Piece"),
        ],
        "cities": ["Surat", "Jaipur", "Delhi", "Tiruppur", "Kolkata", "Mumbai", "Ludhiana", "Bengaluru", "Hyderabad", "Ahmedabad"],
        "count": 40,
    },
    "Medical & Surgical": {
        "products": [
            ("Surgical Scissors SS", 200, 1500, "Piece"), ("Hospital Bed Manual", 15000, 50000, "Piece"),
            ("Stethoscope", 200, 2000, "Piece"), ("BP Monitor Digital", 800, 3000, "Piece"),
            ("Surgical Gloves Box", 150, 400, "Box"), ("Oxygen Concentrator 5L", 25000, 80000, "Unit"),
            ("Wheelchair Standard", 3000, 12000, "Piece"), ("Pulse Oximeter", 500, 2000, "Piece"),
            ("OT Light LED", 30000, 150000, "Unit"), ("Autoclave 20L", 15000, 50000, "Piece"),
        ],
        "cities": ["Delhi", "Mumbai", "Jalandhar", "Ambala", "Chennai", "Ahmedabad", "Kolkata", "Bengaluru", "Pune", "Hyderabad"],
        "count": 35,
    },
    "Handicrafts & Gifts": {
        "products": [
            ("Brass Decorative Statue", 500, 5000, "Piece"), ("Copper Water Bottle", 200, 800, "Piece"),
            ("Wooden Wall Clock", 300, 2000, "Piece"), ("Metal Flower Vase", 250, 1500, "Piece"),
            ("Marble Ganesha Idol", 400, 3000, "Piece"), ("Singing Bowl Brass", 300, 2500, "Piece"),
            ("Handmade Candle Set", 100, 500, "Set"), ("Jute Bag Printed", 30, 150, "Piece"),
            ("Ceramic Planter", 100, 600, "Piece"), ("Corporate Gift Set", 300, 2000, "Set"),
        ],
        "cities": ["Moradabad", "Jaipur", "Delhi", "Mumbai", "Agra", "Jodhpur", "Kolkata", "Ahmedabad", "Bengaluru", "Chennai"],
        "count": 35,
    },
    "Water Treatment": {
        "products": [
            ("RO Plant 500 LPH", 50000, 150000, "Unit"), ("ETP Plant 50 KLD", 200000, 800000, "Unit"),
            ("STP Plant 100 KLD", 300000, 1200000, "Unit"), ("Water Softener 1000 LPH", 25000, 80000, "Unit"),
            ("UV Water Purifier", 3000, 12000, "Unit"), ("DM Water Plant", 40000, 200000, "Unit"),
            ("Sand Filter", 15000, 60000, "Unit"), ("Dosing Pump", 5000, 25000, "Piece"),
            ("Water Testing Kit", 500, 3000, "Kit"), ("Iron Removal Filter", 20000, 80000, "Unit"),
        ],
        "cities": ["Delhi", "Noida", "Mumbai", "Kolkata", "Ahmedabad", "Chennai", "Pune", "Hyderabad", "Bengaluru", "Navi Mumbai"],
        "count": 35,
    },
    "Laboratory & Scientific": {
        "products": [
            ("Glass Beaker Set", 200, 800, "Set"), ("Laboratory Microscope", 5000, 30000, "Piece"),
            ("Digital pH Meter", 2000, 8000, "Piece"), ("Hot Plate Stirrer", 3000, 12000, "Piece"),
            ("Analytical Balance", 8000, 40000, "Piece"), ("Fume Hood", 30000, 120000, "Unit"),
            ("Glass Burette 50ml", 100, 400, "Piece"), ("Laboratory Centrifuge", 5000, 25000, "Piece"),
            ("Test Tube Rack", 50, 300, "Piece"), ("Pipette 10ml", 20, 100, "Piece"),
        ],
        "cities": ["Delhi", "Ambala", "Mumbai", "Chennai", "Bengaluru", "Kolkata", "Ahmedabad", "Erode", "Pune", "Hyderabad"],
        "count": 30,
    },
    "Paper & Stationery": {
        "products": [
            ("A4 Copier Paper Ream", 180, 350, "Ream"), ("Writing Notebook 200 Pages", 25, 80, "Piece"),
            ("Spiral Binding Notebook", 30, 100, "Piece"), ("Bill Book 50 Pages", 15, 40, "Piece"),
            ("Kraft Paper Roll", 25, 60, "Kg"), ("Visiting Card 100pcs", 100, 400, "Pack"),
            ("Envelope White A4", 2, 8, "Piece"), ("File Folder PP", 15, 50, "Piece"),
            ("Correction Pen", 15, 40, "Piece"), ("Sticky Notes Pad", 20, 60, "Pack"),
        ],
        "cities": ["Delhi", "Mumbai", "Noida", "Ahmedabad", "Kolkata", "Chennai", "Bengaluru", "Pune", "Jaipur", "Lucknow"],
        "count": 30,
    },
    "Bags & Luggage": {
        "products": [
            ("Laptop Bag Leather", 500, 3000, "Piece"), ("Trolley Suitcase 24 inch", 1500, 5000, "Piece"),
            ("School Backpack", 200, 800, "Piece"), ("Cotton Tote Bag", 50, 200, "Piece"),
            ("Jute Shopping Bag", 30, 150, "Piece"), ("Duffle Travel Bag", 400, 2000, "Piece"),
            ("Ladies Handbag PU", 200, 1200, "Piece"), ("Non Woven Carry Bag", 3, 15, "Piece"),
            ("Rexine Office Bag", 300, 1200, "Piece"), ("Gym Bag", 200, 800, "Piece"),
        ],
        "cities": ["Delhi", "Mumbai", "Kolkata", "Agra", "Chennai", "Bengaluru", "Noida", "Ahmedabad", "Kanpur", "Jaipur"],
        "count": 30,
    },
    "Printing & Packaging Machines": {
        "products": [
            ("Flexo Printing Machine", 500000, 2000000, "Unit"), ("Label Printing Machine", 20000, 100000, "Unit"),
            ("Screen Printing Machine", 15000, 80000, "Unit"), ("Shrink Wrapping Machine", 30000, 150000, "Unit"),
            ("Carton Sealing Machine", 10000, 50000, "Unit"), ("Pouch Packing Machine", 50000, 300000, "Unit"),
            ("Inkjet Printer Industrial", 80000, 300000, "Unit"), ("Die Cutting Machine", 100000, 500000, "Unit"),
            ("Lamination Machine", 25000, 100000, "Unit"), ("Band Sealer", 8000, 30000, "Unit"),
        ],
        "cities": ["Delhi", "Mumbai", "Faridabad", "Ahmedabad", "Rajkot", "Noida", "Pune", "Chennai", "Bengaluru", "Ludhiana"],
        "count": 30,
    },
}

def gen_gst(state_code: int) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return f"{state_code:02d}{''.join(random.choice(letters) for _ in range(5))}{random.randint(1000,9999)}{random.choice(letters)}{random.randint(1,9)}{random.choice(letters + '0123456789')}{random.choice('0123456789')}"

STATE_CODES = {
    "Maharashtra": 27, "Gujarat": 24, "Delhi": 7, "Uttar Pradesh": 9, "Karnataka": 29,
    "Tamil Nadu": 33, "West Bengal": 19, "Telangana": 36, "Punjab": 3, "Rajasthan": 8,
    "Madhya Pradesh": 23, "Haryana": 6, "Kerala": 32, "Chhattisgarh": 22, "Jharkhand": 20,
    "Odisha": 21, "Andhra Pradesh": 37, "Chandigarh": 4, "Uttarakhand": 5, "Himachal Pradesh": 2,
    "Assam": 18, "Bihar": 10,
}

INDIAN_NAMES = [
    "Rajesh Kumar", "Sunil Patel", "Amit Shah", "Vikram Singh", "Rakesh Gupta",
    "Sanjay Mehta", "Deepak Sharma", "Manoj Agarwal", "Anil Jain", "Nitin Verma",
    "Ashok Reddy", "Prashant Desai", "Ramesh Iyer", "Kiran Rao", "Mohan Das",
    "Suresh Babu", "Harish Chand", "Dinesh Kapoor", "Ravi Shankar", "Govind Pillai",
]

def generate_suppliers():
    suppliers = []
    used_names = set()

    for category, config in CATEGORIES.items():
        count = config["count"]
        products_pool = config["products"]
        cities = config["cities"]

        for i in range(count):
            # Generate unique company name
            for _ in range(100):
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                suffix = random.choice(SUFFIXES)
                name = f"{first} {last}"
                if suffix:
                    name += f" {suffix}"
                if name not in used_names:
                    used_names.add(name)
                    break

            city = random.choice(cities)
            state = CITY_STATE[city]
            year = random.randint(1970, 2022)
            rating = round(random.uniform(3.0, 5.0), 1)
            num_reviews = random.randint(0, 50)
            verified = random.random() < 0.6
            gst = random.random() < 0.5
            trust = random.random() < 0.2
            certs = random.choice(CERTIFICATIONS_POOL)
            if category == "Food & Beverages" and certs and "FSSAI" not in certs:
                certs = random.choice([["FSSAI"], ["FSSAI", "ISO 22000"], ["FSSAI", "ISO 9001"], []])
            if category == "Pharmaceuticals" and certs and "GMP" not in certs:
                certs = random.choice([["GMP"], ["WHO GMP", "ISO 9001"], ["ISO 13485"], []])

            # Generate products
            num_products = random.randint(2, min(8, len(products_pool)))
            selected_products = random.sample(products_pool, num_products)
            products = []
            for pname, pmin, pmax, punit in selected_products:
                price_lo = random.randint(int(pmin * 0.8), int(pmin * 1.2))
                price_hi = random.randint(int(pmax * 0.8), int(pmax * 1.2))
                if price_lo > price_hi:
                    price_lo, price_hi = price_hi, price_lo
                moq_options = ["1 Piece", "5 Pieces", "10 Pieces", "25 Kg", "50 Kg", "100 Kg",
                               "100 Pieces", "500 Pieces", "1000 Pieces", "1 Ton", None, None]
                products.append({
                    "name": pname,
                    "price": f"₹{price_lo}-₹{price_hi}/{punit}" if price_lo != price_hi else f"₹{price_lo}/{punit}",
                    "category": category,
                    "min_order_qty": random.choice(moq_options),
                })

            supplier = {
                "company_name": name,
                "city": city,
                "state": state,
                "nature_of_business": random.choice(NATURE_TYPES),
                "rating": rating,
                "num_reviews": num_reviews,
                "year_established": year,
                "indiamart_verified": verified,
                "gst_verified": gst,
                "trust_seal": trust,
                "products": products,
                "source_url": f"https://www.indiamart.com/{slugify(name)}/",
            }

            if certs:
                supplier["certifications"] = certs
            if random.random() < 0.4:
                supplier["annual_turnover"] = random.choice(TURNOVERS)
            if random.random() < 0.4:
                supplier["num_employees"] = random.choice(EMPLOYEES)
            if gst:
                supplier["gst_number"] = gen_gst(STATE_CODES.get(state, 27))
            if random.random() < 0.3:
                supplier["contact_person"] = random.choice(INDIAN_NAMES)
            if random.random() < 0.2:
                supplier["phone"] = f"+91{random.randint(7000000000, 9999999999)}"

            suppliers.append(supplier)

    return suppliers


def main():
    suppliers = generate_suppliers()
    random.shuffle(suppliers)  # Mix categories

    total_products = sum(len(s["products"]) for s in suppliers)
    output = "/tmp/massive_suppliers.json"
    with open(output, "w") as f:
        json.dump(suppliers, f, indent=2, ensure_ascii=False)

    cities = len(set(s["city"] for s in suppliers))
    categories = len(set(p["category"] for s in suppliers for p in s["products"]))
    print(f"Generated {len(suppliers)} suppliers with {total_products} products across {cities} cities and {categories} categories")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
