import type { Metadata } from "next";
import "./globals.css";
import { TopNav } from "./components/TopNav";

export const metadata: Metadata = {
  title: "Prospector de Leads",
  description: "Busca de profissionais de saúde e estética por região",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="shell">
          <TopNav />
          {children}
        </div>
      </body>
    </html>
  );
}
