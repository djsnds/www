import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { CartProvider } from "@/context/CartContext";
import { Toaster } from "sonner";
import { Marquee } from "@/components/Marquee";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Shop - Your one-stop destination for fashion",
  description: "Discover the latest trends in men's and women's clothing and sneakers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <CartProvider>
          <div className="flex flex-col min-h-screen">
            <Marquee />
            <Header />
            <main className="flex-grow">
              {children}
            </main>
            <Footer />
          </div>
          <Toaster />
        </CartProvider>
      </body>
    </html>
  );
} 