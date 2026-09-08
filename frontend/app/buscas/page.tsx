import Link from "next/link";
import { ESPECIALIDADE_LABELS, listarBuscas } from "@/lib/api";

export default async function BuscasPage() {
  const buscas = await listarBuscas();

  return (
    <main>
      <h1>Histórico de buscas</h1>
      <p className="subtitle">Todas as buscas já realizadas, mais recentes primeiro.</p>

      <div className="card">
        {buscas.length === 0 ? (
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
              {buscas.map((b) => (
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
