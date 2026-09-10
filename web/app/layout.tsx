import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SolGeo Change Evidence",
  description: "A reproducible remote-sensing research case study for Abu Dhabi urban-edge change.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body>{children}</body>
    </html>
  );
}
