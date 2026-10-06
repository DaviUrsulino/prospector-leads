"use client";

import { useMemo, useState } from "react";
import { alternarContatado, alternarFavorito, type Lead } from "@/lib/api";

export function LeadsTable({ buscaId, leadsIniciais }: { buscaId: string; leadsIniciais: Lead[] }) {
  const [leads, setLeads] = useState(leadsIniciais);
  const [filtro, setFiltro] = useState("");
  const [soFavoritos, setSoFavoritos] = useState(false);
  const [soNaoContatados, setSoNaoContatados] = useState(false);

  const totalContatados = leads.filter((l) => l.contatado).length;

  function urlWhatsapp(telefone: string): string {
    const digitos = telefone.replace(/\D/g, "");
    return `https://wa.me/${digitos}`;
  }

  function urlWhatsappDireto(numero: string): string {
    return `https://wa.me/${numero}`;
  }

  const leadsFiltrados = useMemo(() => {
    const termo = filtro.trim().toLowerCase();
    return leads.filter((lead) => {
      if (soFavoritos && !lead.favorito) return false;
      if (soNaoContatados && lead.contatado) return false;
      if (!termo) return true;
      return (
        lead.nome.toLowerCase().includes(termo) ||
        (lead.endereco ?? "").toLowerCase().includes(termo)
      );
    });
  }, [leads, filtro, soFavoritos, soNaoContatados]);

  async function toggleContatado(leadId: string, novoValor: boolean) {
    setLeads((prev) =>
      prev.map((l) => (l.id === leadId ? { ...l, contatado: novoValor } : l))
    );
    try {
      await alternarContatado(buscaId, leadId, novoValor);
    } catch {
      setLeads((prev) =>
        prev.map((l) => (l.id === leadId ? { ...l, contatado: !novoValor } : l))
      );
    }
  }

  async function toggleFavorito(leadId: string, novoValor: boolean) {
    setLeads((prev) =>
      prev.map((l) => (l.id === leadId ? { ...l, favorito: novoValor } : l))
    );
    try {
      await alternarFavorito(buscaId, leadId, novoValor);
    } catch {
      setLeads((prev) =>
        prev.map((l) => (l.id === leadId ? { ...l, favorito: !novoValor } : l))
      );
    }
  }

  return (
    <div className="card">
      <div style={{ marginBottom: "0.75rem", fontSize: "0.875rem", color: "var(--color-text-muted, #9ca3af)" }}>
        {totalContatados} de {leads.length} contatados
      </div>
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
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={soNaoContatados}
            onChange={(e) => setSoNaoContatados(e.target.checked)}
          />
          Só não contatados
        </label>
      </div>

      {leadsFiltrados.length === 0 ? (
        <div className="empty-state">Nenhum lead corresponde ao filtro.</div>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
            <tr>
              <th></th>
              <th>Contatado</th>
              <th>Nome</th>
              <th>Telefone</th>
              <th>WhatsApp direto</th>
              <th>Endereço</th>
              <th>E-mail</th>
              <th>Instagram</th>
              <th>Facebook</th>
              <th>Maps</th>
              <th>LinkedIn</th>
            </tr>
          </thead>
          <tbody>
            {leadsFiltrados.map((lead) => (
              <tr key={lead.id} style={lead.contatado ? { background: "rgba(234, 179, 8, 0.15)" } : undefined}>
                <td style={{ textAlign: "center" }}>
                  <input
                    type="checkbox"
                    checked={lead.contatado}
                    onChange={(e) => toggleContatado(lead.id, e.target.checked)}
                    title={lead.contatado ? "Desmarcar contatado" : "Marcar como contatado"}
                    style={{ width: "1rem", height: "1rem", cursor: "pointer", accentColor: "#ca8a04" }}
                  />
                </td>
                <td>
                  <button
                    className="favorite-btn"
                    onClick={() => toggleFavorito(lead.id, !lead.favorito)}
                    aria-label={lead.favorito ? "Remover favorito" : "Favoritar"}
                    title={lead.favorito ? "Remover favorito" : "Favoritar"}
                  >
                    {lead.favorito ? "★" : "☆"}
                  </button>
                </td>
                <td>
                  {lead.nome}
                  {lead.fonte !== "google_places" && (
                    <span className="badge" title="Encontrado via fonte alternativa (OpenStreetMap)">
                      {lead.fonte.toUpperCase()}
                    </span>
                  )}
                </td>
                <td>
                  {lead.telefone ? (
                    <a
                      href={urlWhatsapp(lead.telefone)}
                      target="_blank"
                      rel="noreferrer"
                      className="whatsapp-link"
                    >
                      {lead.telefone}
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {lead.whatsapp_direto ? (
                    <a
                      href={urlWhatsappDireto(lead.whatsapp_direto)}
                      target="_blank"
                      rel="noreferrer"
                      className="whatsapp-link"
                    >
                      abrir
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
                <td>{lead.endereco ?? "—"}</td>
                <td>
                  {lead.email ? (
                    <a href={`mailto:${lead.email}`}>{lead.email}</a>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {lead.instagram ? (
                    <a href={lead.instagram} target="_blank" rel="noreferrer">
                      abrir
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {lead.facebook ? (
                    <a href={lead.facebook} target="_blank" rel="noreferrer">
                      abrir
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {lead.link_perfil ? (
                    <a href={lead.link_perfil} target="_blank" rel="noreferrer">
                      abrir
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {lead.linkedin ? (
                    <a href={lead.linkedin} target="_blank" rel="noreferrer">
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
        </div>
      )}
    </div>
  );
}
