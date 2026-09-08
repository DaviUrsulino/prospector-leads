import Link from "next/link";
import { ESPECIALIDADE_LABELS, obterEstatisticas } from "@/lib/api";

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
      </div>

      <div className="card">
        <h2>Buscas recentes</h2>
        {stats.ultimas_buscas.length === 0 ? (
          <div className="empty-state">
            Nenhuma busca ainda. <Link href="/buscar">Faça a primeira busca</Link>.
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Cidade</th>
                <th>Especialidade</th>
                <th>Alvo</th>
                <th>Data</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {stats.ultimas_buscas.map((b) => (
                <tr key={b.id}>
                  <td>{b.cidade}</td>
                  <td>
                    <span className="badge">
                      {ESPECIALIDADE_LABELS[b.termo] ?? b.termo}
                    </span>
                  </td>
                  <td>{b.quantidade_alvo}</td>
                  <td>{new Date(b.criada_em).toLocaleString("pt-BR")}</td>
                  <td>
                    <Link className="link-quiet" href={`/buscas/${b.id}`}>
                      ver →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
