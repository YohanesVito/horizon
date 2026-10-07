// Runs only on the Next.js server. Never expose backend credentials to the browser.
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function proxy(request: Request) {
  try {
    const base = new URL(process.env.BACKEND_URL ?? "http://127.0.0.1:8000");
    const local = ["localhost", "127.0.0.1", "[::1]"].includes(base.hostname);
    const key = process.env.HORIZON_API_KEY;
    if (base.username || base.password || (!local && (base.protocol !== "https:" || !key))) {
      return Response.json({ detail: "Konfigurasi backend belum siap." }, { status: 503 });
    }
    const incoming = new URL(request.url);
    const target = new URL(base.origin);
    target.pathname = incoming.pathname;
    target.search = incoming.search;
    const headers = new Headers({ Accept: "application/json" });
    if (key) headers.set("Authorization", `Bearer ${key}`);
    const contentType = request.headers.get("content-type");
    if (contentType) headers.set("Content-Type", contentType);
    let body: ArrayBuffer | undefined;
    if (!["GET", "HEAD"].includes(request.method)) {
      if (Number(request.headers.get("content-length") ?? 0) > 65_536) {
        return Response.json({ detail: "Request terlalu besar." }, { status: 413 });
      }
      body = await request.arrayBuffer();
      if (body.byteLength > 65_536) {
        return Response.json({ detail: "Request terlalu besar." }, { status: 413 });
      }
    }
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body,
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(30_000),
    });
    // Do not relay redirects (or credentials) to another host.
    if (upstream.status >= 300 && upstream.status < 400) {
      return Response.json({ detail: "Alamat backend perlu diperiksa." }, { status: 502 });
    }
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": upstream.headers.get("content-type") ?? "application/json",
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return Response.json({ detail: "Backend tidak dapat dihubungi. Coba lagi." }, { status: 502 });
  }
}

export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE, proxy as HEAD };
