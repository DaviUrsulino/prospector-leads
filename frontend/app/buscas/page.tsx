import { listarBuscas } from "@/lib/api";
import { HistoricoTable } from "./HistoricoTable";

export default async function BuscasPage() {
  const buscas = await listarBuscas();

  return (
    <main>
      <h1>Histórico de buscas</h1>
      <p className="subtitle">Todas as buscas já realizadas, mais recentes primeiro.</p>

      <div className="card">
        <HistoricoTable buscasIniciais={buscas} />
      </div>
    </main>
  );
}
