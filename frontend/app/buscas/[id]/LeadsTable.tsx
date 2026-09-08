"use client";

import { useMemo, useState } from "react";
import { alternarFavorito, type Lead } from "@/lib/api";

export function LeadsTable({ buscaId, leadsIniciais }: { buscaId: string; leadsIniciais: Lead[] }) {
  const [leads, setLeads] = useState(leadsIniciais);
  const [filtro, setFiltro] = useState("");
  const [soFavoritos, setSoFavoritos] = useState(false);

  const leadsFiltrados = useMemo(() => {
    const termo = filtro.trim().toLowerCase();
    return leads.filter((lead) => {
      if (soFavoritos && !lead.favorito) return false;
      if (!termo) return true;
      return (
        lead.nome.toLowerCase().includes(termo) ||
        (lead.endereco ?? "").toLowerCase().includes(termo)
      );
    });
  }, [leads, filtro, soFavoritos]);

  async function toggleFavorito(leadId: string) {
    setLeads((prev) =>
      prev.map((l) => (l.id === leadId ? { ...l, favorito: !l.favorito } : l))
    );
    try {
      await alternarFavorito(buscaId, leadId);
    } catch {
      setLeads((prev) =>
        prev.map((l) => (l.id === leadId ? { ...l, favorito: !l.favorito } : l))
      );
    }
  }

  return (
    <div className="card">
      <div className="table-controls">
        <input
          className="filter-input"
          placeholder="Filtrar por nome ou endereço..."
          value={filtro}
          onChange={(e) => setFiltro(e.target.value)}
        />
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={soFavoritos}
            onChange={(e) => setSoFavoritos(e.target.checked)}
          />
          Só favoritos
        </label>
      </div>

      {leadsFiltrados.length === 0 ? (
        <div className="empty-state">Nenhum lead corresponde ao filtro.</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th></th>
              <th>Nome</th>
              <th>Telefone</th>
              <th>Endereço</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {leadsFiltrados.map((lead) => (
              <tr key={lead.id}>
                <td>
                  <button
                    className="favorite-btn"
                    onClick={() => toggleFavorito(lead.id)}
                    aria-label={lead.favorito ? "Remover favorito" : "Favoritar"}
                    title={lead.favorito ? "Remover favorito" : "Favoritar"}
                  >
                    {lead.favorito ? "★" : "☆"}
                  </button>
                </td>
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
  );
}
