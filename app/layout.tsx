import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CineMatch - Film Öneri Sistemi",
  description: "MongoDB ve AI destekli film öneri platformu",
  icons: { clapperboard: "/clapperboard.png" },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body className={inter.className}>
        <Header />
        {children}
      </body>
    </html>
  );
}
