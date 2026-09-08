import Link from "next/link";
import { ESPECIALIDADE_LABELS, obterBusca, urlExportBusca } from "@/lib/api";

export default async function BuscaDetalhePage({ params }: { params: { id: string } }) {
  const busca = await obterBusca(params.id);
  const especialidade = ESPECIALIDADE_LABELS[busca.termo] ?? busca.termo;

  return (
    <main>
      <Link className="link-quiet" href="/buscas">
        ← Histórico
      </Link>
      <h1 style={{ marginTop: "0.6rem" }}>
        {especialidade} em {busca.cidade}
      </h1>

      <div className="result-summary">
        <span className="badge">{especialidade}</span>
        <span>
          {busca.leads.length} de {busca.quantidade_alvo} contatos encontrados
        </span>
        <span>·</span>
        <a href={urlExportBusca(busca.id)}>Exportar CSV</a>
      </div>

      <div className="card">
        {busca.leads.length === 0 ? (
          <div className="empty-state">Nenhum lead encontrado nessa busca.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Telefone</th>
                <th>Endereço</th>
                <th>Link</th>
              </tr>
            </thead>
            <tbody>
              {busca.leads.map((lead) => (
                <tr key={lead.id}>
                  <td>{lead.nome}</td>
                  <td>{lead.telefone ?? "—"}</td>
                  <td>{lead.endereco ?? "—"}</td>
                  <td>
                    {lead.link_perfil ? (
                      <a href={lead.link_perfil} target="_blank" rel="noreferrer">
                        abrir
                      </a>
                    ) : (
                      "—"
                    )}
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
