"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { criarBusca } from "@/lib/api";

const CIDADES = [
  "Brasília",
  "São Paulo",
  "Rio de Janeiro",
  "Belo Horizonte",
  "Salvador",
  "Fortaleza",
  "Recife",
  "Porto Alegre",
  "Curitiba",
  "Manaus",
  "Goiânia",
  "Belém",
  "Campinas",
  "São Luís",
  "Natal",
  "Campo Grande",
  "João Pessoa",
  "Teresina",
  "Maceió",
  "Cuiabá",
  "Florianópolis",
  "Vitória",
];

const SEGMENTOS: Record<string, string[]> = {
  Dentista: [
    "Ortodontia",
    "Odontopediatria",
    "Endodontia",
    "Periodontia",
    "Prótese Dentária",
    "Implantodontia",
    "Cirurgia e Traumatologia Bucomaxilofacial",
    "Dentística / Estética Dental",
    "Radiologia Odontológica",
    "Odontogeriatria",
    "Odontologia do Trabalho",
    "Odontologia Legal",
    "Odontologia para Pacientes com Necessidades Especiais",
    "Patologia Oral / Estomatologia",
    "Disfunção Temporomandibular e Dor Orofacial (DTM)",
    "Saúde Coletiva",
  ],
  Médico: [
    "Clínica Médica",
    "Cardiologia",
    "Dermatologia",
    "Ginecologia e Obstetrícia",
    "Ortopedia e Traumatologia",
    "Pediatria",
    "Urologia",
    "Psiquiatria",
    "Neurologia",
    "Endocrinologia e Metabologia",
    "Oftalmologia",
    "Otorrinolaringologia",
    "Gastroenterologia",
    "Pneumologia",
    "Nefrologia",
    "Hematologia",
    "Oncologia",
    "Reumatologia",
    "Infectologia",
    "Anestesiologia",
    "Cirurgia Geral",
    "Cirurgia Plástica",
    "Cirurgia Cardiovascular",
    "Cirurgia Vascular",
    "Cirurgia Pediátrica",
    "Neurocirurgia",
    "Radiologia e Diagnóstico por Imagem",
    "Medicina de Família e Comunidade",
    "Medicina do Trabalho",
    "Medicina Esportiva",
    "Medicina Legal",
    "Medicina Nuclear",
    "Medicina Física e Reabilitação",
    "Geriatria",
    "Genética Médica",
    "Patologia Clínica",
    "Alergia e Imunologia",
    "Angiologia",
    "Coloproctologia",
    "Mastologia",
    "Nutrologia",
    "Medicina Intensiva",
    "Medicina de Emergência",
  ],
  Esteticista: [
    "Design de Sobrancelha",
    "Limpeza de Pele",
    "Micropigmentação",
    "Depilação a Laser",
    "Estética Corporal",
    "Massagem Estética",
    "Microagulhamento",
    "Peeling Químico",
    "Drenagem Linfática",
    "Extensão de Cílios",
    "Podologia Estética",
    "Toxina Botulínica (Botox)",
    "Preenchimento Facial",
    "Radiofrequência Estética",
    "Criolipólise",
    "Skincare Profissional",
    "Maquiagem Definitiva",
  ],
};

export default function BuscarPage() {
  const router = useRouter();
  const [cidade, setCidade] = useState("Brasília");
  const [segmento, setSegmento] = useState<keyof typeof SEGMENTOS>("Dentista");
  const [termosSelecionados, setTermosSelecionados] = useState<string[]>([]);
  const [termoCustom, setTermoCustom] = useState("");
  const [quantidadeTexto, setQuantidadeTexto] = useState("20");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const sugestoes = useMemo(() => SEGMENTOS[segmento], [segmento]);

  function alternarTermo(termo: string) {
    setTermosSelecionados((prev) =>
      prev.includes(termo) ? prev.filter((t) => t !== termo) : [...prev, termo]
    );
  }

  // Só letras (com acento), espaços e uns poucos separadores comuns em nome
  // de especialidade ("Cirurgia e Traumatologia Bucomaxilofacial", "Dentística
  // / Estética Dental"). Barra número solto, emoji, símbolo aleatório etc.
  // Não impede alguém de digitar uma palavra qualquer que "pareça" válida
  // (ex: "banana") — isso exigiria checar contra uma lista real de
  // especialidades médicas, o que não temos.
  const TERMO_VALIDO = /^[\p{L}\s/()-]+$/u;

  function adicionarTermoCustom() {
    const valor = termoCustom.trim();
    if (!valor || termosSelecionados.includes(valor)) return;
    if (valor.length < 3 || !TERMO_VALIDO.test(valor)) {
      setErro('Especialidade inválida — use só letras (ex: "Reumatologia"), sem número ou símbolo.');
      return;
    }
    setErro(null);
    setTermosSelecionados((prev) => [...prev, valor]);
    setTermoCustom("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);

    if (termosSelecionados.length === 0) {
      setErro("Marque ao menos uma especialidade.");
      return;
    }

    const quantidade = Number(quantidadeTexto);
    if (!Number.isInteger(quantidade) || quantidade < 1 || quantidade > 200) {
      setErro("Quantidade de contatos precisa ser um número entre 1 e 200.");
      return;
    }

    setEnviando(true);
    try {
      const busca = await criarBusca({
        cidade,
        termos: termosSelecionados,
        quantidade_alvo: quantidade,
      });
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
            list="sugestoes-cidade"
            value={cidade}
            onChange={(e) => setCidade(e.target.value)}
            placeholder="Digite ou escolha uma cidade"
            required
          />
          <datalist id="sugestoes-cidade">
            {CIDADES.map((c) => (
              <option key={c} value={c} />
            ))}
          </datalist>
        </label>

        <label>
          Segmento
          <select
            value={segmento}
            onChange={(e) => {
              setSegmento(e.target.value);
              setTermosSelecionados([]);
            }}
          >
            {Object.keys(SEGMENTOS).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <div>
          <label>Especialidades (marque uma ou mais)</label>
          <div className="checkbox-grid">
            {sugestoes.map((s) => (
              <label key={s} className="checkbox-label checkbox-label--block">
                <input
                  type="checkbox"
                  checked={termosSelecionados.includes(s)}
                  onChange={() => alternarTermo(s)}
                />
                {s}
              </label>
            ))}
          </div>

          <div className="custom-termo-row">
            <input
              value={termoCustom}
              onChange={(e) => setTermoCustom(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  adicionarTermoCustom();
                }
              }}
              placeholder="Outra especialidade..."
            />
            <button type="button" onClick={adicionarTermoCustom}>
              Adicionar
            </button>
          </div>

          {termosSelecionados.length > 0 && (
            <div className="chips-row">
              {termosSelecionados.map((t) => (
                <span key={t} className="badge chip">
                  {t}
                  <button type="button" onClick={() => alternarTermo(t)} aria-label={`Remover ${t}`}>
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        <label>
          Quantidade de contatos
          <input
            type="number"
            min={1}
            max={200}
            value={quantidadeTexto}
            onChange={(e) => setQuantidadeTexto(e.target.value)}
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
