import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "AI Paper Marking Dashboard",
  description: "Intelligent paper marking and analytics platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="flex h-screen bg-gray-50 text-gray-900 font-sans antialiased selection:bg-blue-200">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </body>
    </html>
  );
}
