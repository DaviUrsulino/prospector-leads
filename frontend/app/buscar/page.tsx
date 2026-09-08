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
  const [termo, setTermo] = useState("");
  const [quantidadeTexto, setQuantidadeTexto] = useState("50");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const sugestoes = useMemo(() => SEGMENTOS[segmento], [segmento]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);

    const quantidade = Number(quantidadeTexto);
    if (!Number.isInteger(quantidade) || quantidade < 1 || quantidade > 200) {
      setErro("Quantidade de contatos precisa ser um número entre 1 e 200.");
      return;
    }

    setEnviando(true);
    try {
      const busca = await criarBusca({
        cidade,
        termo: termo.trim(),
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
              setTermo("");
            }}
          >
            {Object.keys(SEGMENTOS).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label>
          Especialidade
          <input
            list="sugestoes-especialidade"
            value={termo}
            onChange={(e) => setTermo(e.target.value)}
            placeholder="Digite ou escolha uma sugestão"
            required
          />
          <datalist id="sugestoes-especialidade">
            {sugestoes.map((s) => (
              <option key={s} value={s} />
            ))}
          </datalist>
        </label>

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
