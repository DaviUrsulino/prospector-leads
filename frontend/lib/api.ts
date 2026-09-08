// No servidor (Server Components, dentro do container) usa a URL interna do
// Docker; no navegador usa a URL pública, que aponta pra porta exposta no host.
const API_URL =
  typeof window === "undefined"
    ? process.env.API_URL ?? "http://backend:8000"
    : process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Lead = {
  id: string;
  nome: string;
  telefone: string | null;
  endereco: string | null;
  especialidade: string;
  place_id: string | null;
  link_perfil: string | null;
  favorito: boolean;
};

export type Busca = {
  id: string;
  cidade: string;
  termo: string;
  quantidade_alvo: number;
  criada_em: string;
};

export type BuscaComLeads = Busca & { leads: Lead[] };

export async function criarBusca(input: {
  cidade: string;
  termo: string;
  quantidade_alvo: number;
}): Promise<BuscaComLeads> {
  const resp = await fetch(`${API_URL}/buscas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!resp.ok) {
    throw new Error(`Falha ao criar busca: ${resp.status}`);
  }
  return resp.json();
}

export async function listarBuscas(): Promise<Busca[]> {
  const resp = await fetch(`${API_URL}/buscas`, { cache: "no-store" });
  if (!resp.ok) {
    throw new Error(`Falha ao listar buscas: ${resp.status}`);
  }
  return resp.json();
}

export async function obterBusca(id: string): Promise<BuscaComLeads> {
  const resp = await fetch(`${API_URL}/buscas/${id}`, { cache: "no-store" });
  if (!resp.ok) {
    throw new Error(`Falha ao obter busca: ${resp.status}`);
  }
  return resp.json();
}

export function urlExportBusca(id: string): string {
  return `${API_URL}/buscas/${id}/export`;
}

export async function alternarFavorito(buscaId: string, leadId: string): Promise<Lead> {
  const resp = await fetch(`${API_URL}/buscas/${buscaId}/leads/${leadId}/favorito`, {
    method: "PATCH",
  });
  if (!resp.ok) {
    throw new Error(`Falha ao favoritar lead: ${resp.status}`);
  }
  return resp.json();
}

export type Estatisticas = {
  total_buscas: number;
  total_leads: number;
  pct_leads_com_telefone: number;
  total_favoritos: number;
  ultimas_buscas: Busca[];
};

export async function obterEstatisticas(): Promise<Estatisticas> {
  const resp = await fetch(`${API_URL}/buscas/estatisticas`, { cache: "no-store" });
  if (!resp.ok) {
    throw new Error(`Falha ao obter estatísticas: ${resp.status}`);
  }
  return resp.json();
}

export const ESPECIALIDADE_LABELS: Record<string, string> = {
  dentista: "Dentista",
  medico: "Médico",
  esteticista: "Esteticista",
  biomedico: "Biomédico",
  clinica_geral: "Clínica geral",
};
