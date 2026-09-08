"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { criarBusca } from "@/lib/api";

const ESPECIALIDADES = [
  { value: "dentista", label: "Dentista" },
  { value: "medico", label: "Médico" },
  { value: "esteticista", label: "Esteticista" },
  { value: "biomedico", label: "Biomédico" },
  { value: "clinica_geral", label: "Clínica geral" },
];

export default function BuscarPage() {
  const router = useRouter();
  const [cidade, setCidade] = useState("");
  const [termo, setTermo] = useState(ESPECIALIDADES[0].value);
  const [quantidade, setQuantidade] = useState(50);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setEnviando(true);
    try {
      const busca = await criarBusca({ cidade, termo, quantidade_alvo: quantidade });
      router.push(`/buscas/${busca.id}`);
    } catch (err) {
      setErro("Não foi possível concluir a busca. Tente novamente.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main>
      <h1>Nova busca</h1>
      <p className="subtitle">
        Busque profissionais por cidade e especialidade usando a Google Places API.
      </p>
      <form onSubmit={handleSubmit} className="card">
        <label>
          Cidade
          <input
            value={cidade}
            onChange={(e) => setCidade(e.target.value)}
            placeholder="São Paulo"
            required
          />
        </label>

        <label>
          Especialidade
          <select value={termo} onChange={(e) => setTermo(e.target.value)}>
            {ESPECIALIDADES.map((e) => (
              <option key={e.value} value={e.value}>
                {e.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Quantidade de contatos
          <input
            type="number"
            min={1}
            max={200}
            value={quantidade}
            onChange={(e) => setQuantidade(Number(e.target.value))}
            required
          />
        </label>

        {erro && <div className="error-banner">{erro}</div>}

        <button type="submit" disabled={enviando}>
          {enviando ? "Buscando..." : "Buscar"}
        </button>
      </form>
    </main>
  );
}
