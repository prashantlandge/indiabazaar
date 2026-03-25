import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/lib/providers";

export const metadata: Metadata = {
  title: "TradeRadar — AI-Powered B2B Supplier Intelligence",
  description:
    "Find the right supplier. Describe what you need. TradeRadar uses procurement intelligence to match you with trusted B2B suppliers.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
