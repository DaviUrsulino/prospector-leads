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
  Advogado: [
    "Direito Civil",
    "Direito Trabalhista",
    "Direito Penal",
    "Direito Tributário",
    "Direito Empresarial",
    "Direito de Família e Sucessões",
    "Direito Imobiliário",
    "Direito do Consumidor",
    "Direito Previdenciário",
    "Direito Administrativo",
    "Direito Ambiental",
    "Direito Digital",
    "Direito Internacional",
    "Direito Contratual",
    "Direito Bancário",
    "Direito da Propriedade Intelectual",
    "Direito Condominial",
    "Direito Eleitoral",
    "Direito Constitucional",
    "Direito do Trabalho e Processo do Trabalho",
  ],
  Contador: [
    "Contabilidade Geral",
    "Contabilidade Tributária",
    "Contabilidade Gerencial",
    "Contabilidade de Custos",
    "Auditoria Contábil",
    "Perícia Contábil",
    "Contabilidade Pública",
    "Contabilidade Internacional",
    "Planejamento Tributário",
    "Gestão Fiscal",
    "Folha de Pagamento e DP",
    "Abertura e Encerramento de Empresas",
    "Imposto de Renda Pessoa Física",
    "Imposto de Renda Pessoa Jurídica",
    "Recuperação de Créditos Tributários",
    "Contabilidade para MEI e Simples Nacional",
  ],
  "Consultor Financeiro": [
    "Planejamento Financeiro Pessoal",
    "Planejamento Patrimonial",
    "Gestão de Investimentos",
    "Análise de Risco Financeiro",
    "Consultoria para Startups",
    "Estruturação de Capital",
    "Fusões e Aquisições",
    "Valuation de Empresas",
    "Gestão de Fluxo de Caixa",
    "Finanças Corporativas",
    "Crédito e Captação de Recursos",
    "Reestruturação Financeira",
    "Educação Financeira Empresarial",
  ],
  "BPO Financeiro": [
    "Contas a Pagar e Receber",
    "Conciliação Bancária",
    "Gestão de Fluxo de Caixa",
    "Emissão de Notas Fiscais",
    "Folha de Pagamento Terceirizada",
    "Controle de Custos e Despesas",
    "Relatórios Financeiros Gerenciais",
    "Automação de Processos Financeiros",
    "Gestão Tributária Terceirizada",
    "Auditoria Interna Financeira",
  ],
  Escola: [
    "Educação Infantil",
    "Ensino Fundamental",
    "Ensino Médio",
    "Escola Técnica",
    "Curso de Idiomas",
    "Curso Pré-Vestibular",
    "Escola de Música",
    "Escola de Artes",
    "Escola de Esportes",
    "Escola de Programação",
    "Escola Montessori",
    "Escola Bilíngue",
    "Reforço Escolar",
    "Escola de Negócios",
    "Escola de Culinária",
  ],
  "Construção Civil": [
    "Construtora Residencial",
    "Construtora Comercial",
    "Reforma e Reforço Estrutural",
    "Alvenaria e Acabamentos",
    "Impermeabilização",
    "Instalações Hidráulicas",
    "Instalações Elétricas",
    "Gesso e Drywall",
    "Pintura e Revestimento",
    "Cobertura e Telhado",
    "Piso e Forro",
    "Paisagismo e Jardinagem",
    "Orçamento e Planejamento de Obras",
    "Gerenciamento de Obras",
  ],
  Engenharia: [
    "Engenharia Civil",
    "Engenharia Elétrica",
    "Engenharia Mecânica",
    "Engenharia de Produção",
    "Engenharia Ambiental",
    "Engenharia de Segurança do Trabalho",
    "Engenharia de Telecomunicações",
    "Engenharia Química",
    "Engenharia de Software",
    "Engenharia Estrutural",
    "Engenharia Sanitária",
    "Engenharia Agrônoma",
    "Topografia e Georreferenciamento",
    "Perícia e Laudo Técnico",
    "Fiscalização de Obras",
  ],
  Arquitetura: [
    "Arquitetura Residencial",
    "Arquitetura Comercial",
    "Arquitetura de Interiores",
    "Arquitetura Corporativa",
    "Arquitetura Hospitalar",
    "Arquitetura Escolar",
    "Arquitetura Paisagística",
    "Arquitetura Sustentável",
    "Urbanismo e Planejamento Urbano",
    "Design de Ambientes",
    "Reforma e Retrofit",
    "Projetos de Iluminação",
    "Compatibilização de Projetos (BIM)",
  ],
  "Curso Online": [
    "Curso de Idiomas Online",
    "Curso de Tecnologia e Programação",
    "Curso de Design e Criatividade",
    "Curso de Marketing Digital",
    "Curso de Negócios e Empreendedorismo",
    "Curso de Finanças e Investimentos",
    "Curso de Saúde e Bem-Estar",
    "Curso de Gastronomia",
    "Curso de Música Online",
    "Curso Preparatório para Concursos",
    "Curso de Fotografia e Vídeo",
    "Curso de Coaching e Desenvolvimento Pessoal",
    "Curso de RH e Gestão de Pessoas",
    "Plataforma EAD",
  ],
  "Consultoria em Gestão": [
    "Gestão Estratégica",
    "Gestão de Processos",
    "Gestão de Projetos",
    "Transformação Digital",
    "Consultoria em Marketing",
    "Consultoria Comercial e Vendas",
    "Governança Corporativa",
    "Gestão de Mudanças",
    "Planejamento Estratégico",
    "Melhoria Contínua / Lean",
    "Consultoria para Startups e Inovação",
    "Gestão de Contratos",
  ],
  "Recursos Humanos": [
    "Recrutamento e Seleção",
    "Treinamento e Desenvolvimento",
    "Gestão de Pessoas",
    "Departamento Pessoal",
    "Benefícios e Remuneração",
    "Cultura Organizacional",
    "Employer Branding",
    "Avaliação de Desempenho",
    "Coaching Executivo",
    "Saúde Ocupacional e SST",
    "Consultoria de RH para PMEs",
    "Outplacement",
  ],
  "Serviços Automotivos": [
    "Oficina Mecânica",
    "Funilaria e Pintura",
    "Elétrica Automotiva",
    "Ar-Condicionado Automotivo",
    "Troca de Óleo e Revisão",
    "Alinhamento e Balanceamento",
    "Pneus e Rodas",
    "Som Automotivo",
    "Vidros e Blindagem",
    "Estética Automotiva / Detailing",
    "Implementos e Acessórios",
    "Concessionária",
    "Autoescola",
  ],
  Veterinária: [
    "Clínica Veterinária Geral",
    "Cirurgia Veterinária",
    "Dermatologia Veterinária",
    "Ortopedia Veterinária",
    "Cardiologia Veterinária",
    "Oncologia Veterinária",
    "Oftalmologia Veterinária",
    "Odontologia Veterinária",
    "Nutrição Animal",
    "Acupuntura Veterinária",
    "Medicina de Animais Silvestres",
    "Pet Shop",
    "Hotel e Day Care para Pets",
    "Banho e Tosa",
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
