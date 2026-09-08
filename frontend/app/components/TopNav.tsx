import Link from "next/link";

export function TopNav() {
  return (
    <header className="topnav">
      <Link href="/" className="brand">
        <span className="mark">PL</span>
        Prospector de Leads
      </Link>
      <nav>
        <Link href="/">Dashboard</Link>
        <Link href="/buscas">Histórico</Link>
      </nav>
      <Link href="/buscar" className="cta">
        Nova busca
      </Link>
    </header>
  );
}
