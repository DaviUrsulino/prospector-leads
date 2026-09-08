const BACKEND_URL = process.env.API_URL ?? "http://backend:8000";

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // O navegador só fala com o próprio Next (mesma origem, sem CORS, sem
    // precisar saber o host interno do Docker); o Next repassa pro backend.
    return [
      {
        source: "/api/backend/:path*",
        destination: `${BACKEND_URL}/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // Impede que o site seja carregado dentro de um <iframe> de outro
          // domínio (clickjacking).
          { key: "X-Frame-Options", value: "DENY" },
          // Navegador não tenta "adivinhar" tipo de conteúdo diferente do
          // Content-Type declarado (evita alguns vetores de XSS).
          { key: "X-Content-Type-Options", value: "nosniff" },
          // Força HTTPS por 1 ano em produção (Easypanel já serve com TLS).
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains",
          },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
