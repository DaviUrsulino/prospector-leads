// No servidor (Server Components, rodando dentro do container) fala direto
// com o backend pela rede interna do Docker. No navegador, fala só com o
// próprio Next (mesma origem), que repassa pro backend via rewrite — assim
// não importa qual domínio/porta pública o app está usando, e a autenticação
// do middleware cobre essas chamadas também.
const API_URL =
  typeof window === "undefined"
    ? process.env.API_URL ?? "http://backend:8000"
    : "/api/backend";

export type Lead = {
  id: string;
  nome: string;
  telefone: string | null;
  endereco: string | null;
  especialidade: string;
  place_id: string | null;
  link_perfil: string | null;
  favorito: boolean;
  website: string | null;
  instagram: string | null;
  linkedin: string | null;
  facebook: string | null;
  email: string | null;
  whatsapp_direto: string | null;
  fonte: string;
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
  // Sempre relativo: é um link clicado pelo navegador, então precisa passar
  // pelo proxy do Next independente de onde essa função foi chamada.
  return `/api/backend/buscas/${id}/export`;
}

export async function excluirBusca(id: string): Promise<void> {
  const resp = await fetch(`${API_URL}/buscas/${id}`, { method: "DELETE" });
  if (!resp.ok) {
    throw new Error(`Falha ao excluir busca: ${resp.status}`);
  }
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

export function formatarEspecialidade(termo: string): string {
  return termo
    .split(" ")
    .map((palavra) => palavra.charAt(0).toUpperCase() + palavra.slice(1))
    .join(" ");
}
