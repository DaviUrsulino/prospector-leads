import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.API_URL ?? "http://backend:8000";

export async function POST(request: NextRequest) {
  const body = await request.json();

  const resp = await fetch(`${BACKEND_URL}/buscas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(300_000), // 5 minutos
  });

  const data = await resp.json();
  return NextResponse.json(data, { status: resp.status });
}
