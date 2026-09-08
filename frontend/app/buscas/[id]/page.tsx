import Link from "next/link";
import { formatarEspecialidade, obterBusca, urlExportBusca } from "@/lib/api";
import { LeadsTable } from "./LeadsTable";

export default async function BuscaDetalhePage({ params }: { params: { id: string } }) {
  const busca = await obterBusca(params.id);
  const especialidade = formatarEspecialidade(busca.termo);

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

      {busca.leads.length === 0 ? (
        <div className="card">
          <div className="empty-state">Nenhum lead encontrado nessa busca.</div>
        </div>
      ) : (
        <LeadsTable buscaId={busca.id} leadsIniciais={busca.leads} />
      )}
    </main>
  );
}
