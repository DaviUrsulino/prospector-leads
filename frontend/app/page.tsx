import Link from "next/link";
import { obterEstatisticas } from "@/lib/api";
import { HistoricoTable } from "./buscas/HistoricoTable";

export default async function HomePage() {
  const stats = await obterEstatisticas();

  return (
    <main>
      <h1>Dashboard</h1>
      <p className="subtitle">
        Visão geral das buscas de profissionais de saúde e estética.
      </p>

      <div className="stats-row">
        <div className="stat-tile">
          <div className="label">Buscas realizadas</div>
          <div className="value">{stats.total_buscas}</div>
        </div>
        <div className="stat-tile">
          <div className="label">Leads encontrados</div>
          <div className="value">{stats.total_leads}</div>
        </div>
        <div className="stat-tile">
          <div className="label">Com telefone</div>
          <div className="value">{stats.pct_leads_com_telefone}%</div>
        </div>
        <div className="stat-tile">
          <div className="label">Favoritados</div>
          <div className="value">{stats.total_favoritos}</div>
        </div>
      </div>

      <div className="card">
        <h2>Buscas recentes</h2>
        {stats.ultimas_buscas.length === 0 ? (
          <div className="empty-state">
            Nenhuma busca ainda. <Link href="/buscar">Faça a primeira busca</Link>.
          </div>
        ) : (
          <HistoricoTable buscasIniciais={stats.ultimas_buscas} />
        )}
      </div>
    </main>
  );
}
