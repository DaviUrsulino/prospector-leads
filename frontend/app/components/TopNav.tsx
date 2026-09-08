import Image from "next/image";
import Link from "next/link";

export function TopNav() {
  return (
    <header className="topnav">
      <Link href="/" className="brand">
        <Image
          src="/brand/vivavoz-logo.png"
          alt="Viva Voz Podcast"
          width={1024}
          height={261}
          priority
          className="brand-logo"
        />
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
