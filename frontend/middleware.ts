import { NextRequest, NextResponse } from "next/server";

// Ativa a autenticação só quando essas envs existirem (ex: em produção, via
// Easypanel). Em dev local sem elas configuradas, o app continua aberto,
// sem fricção nenhuma.
const USUARIO = process.env.BASIC_AUTH_USER;
const SENHA = process.env.BASIC_AUTH_PASSWORD;

// Placeholder do exemplo no docker-compose.yml — se alguém só descomentar
// sem trocar o valor, é pior que não ter senha nenhuma (falsa sensação de
// segurança). Recusa subir autenticado com ele, igual ao fail-closed do
// podcasthub pra segredo de produção esquecido no valor de dev.
const SENHA_PLACEHOLDER = "troque-isso";

// Comparação em tempo constante — comparar string com "===" vaza, por
// diferença de tempo de resposta, quantos caracteres do início bateram
// (timing attack). Mesma prática usada no podcasthub pra segredo de webhook.
function comparacaoSegura(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diferenca = 0;
  for (let i = 0; i < a.length; i++) {
    diferenca |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diferenca === 0;
}

export function middleware(request: NextRequest) {
  if (!USUARIO || !SENHA) {
    return NextResponse.next();
  }

  if (SENHA === SENHA_PLACEHOLDER) {
    return new NextResponse(
      "BASIC_AUTH_PASSWORD ainda está no valor de exemplo do docker-compose.yml — troque antes de subir.",
      { status: 500 }
    );
  }

  const header = request.headers.get("authorization");
  if (header) {
    const [scheme, encoded] = header.split(" ");
    if (scheme === "Basic" && encoded) {
      const [usuario, senha] = atob(encoded).split(":");
      if (comparacaoSegura(usuario ?? "", USUARIO) && comparacaoSegura(senha ?? "", SENHA)) {
        return NextResponse.next();
      }
    }
  }

  return new NextResponse("Autenticação necessária", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Prospector de Leads"' },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
