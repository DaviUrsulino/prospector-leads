"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { excluirBusca, formatarEspecialidade, type Busca } from "@/lib/api";

export function HistoricoTable({ buscasIniciais }: { buscasIniciais: Busca[] }) {
  const router = useRouter();
  const [buscas, setBuscas] = useState(buscasIniciais);

  async function handleExcluir(id: string) {
    if (!confirm("Excluir essa busca e todos os leads dela?")) return;
    setBuscas((prev) => prev.filter((b) => b.id !== id));
    try {
      await excluirBusca(id);
      router.refresh();
    } catch {
      alert("Não foi possível excluir. Tente novamente.");
      setBuscas(buscasIniciais);
    }
  }

  if (buscas.length === 0) {
    return (
      <div className="empty-state">
        Nenhuma busca ainda. <Link href="/buscar">Faça a primeira busca</Link>.
      </div>
    );
  }

  return (
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
              <span className="badge">{formatarEspecialidade(b.termo)}</span>
            </td>
            <td>{b.quantidade_alvo}</td>
            <td>{new Date(b.criada_em).toLocaleString("pt-BR")}</td>
            <td className="row-actions">
              <Link className="link-quiet" href={`/buscas/${b.id}`}>
                ver →
              </Link>
              <button className="delete-btn" onClick={() => handleExcluir(b.id)}>
                🗑 Excluir
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
