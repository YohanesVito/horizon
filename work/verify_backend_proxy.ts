import assert from "node:assert/strict";
import { GET, POST } from "../src/app/api/[...path]/route";

const originalUrl = process.env.BACKEND_URL;
const originalKey = process.env.HORIZON_API_KEY;
const key = "deployment-proxy-test-key-not-a-real-secret";
let calls = 0;
const server = Bun.serve({
  hostname: "127.0.0.1", port: 0,
  async fetch(request) {
    calls++;
    const url = new URL(request.url);
    assert.equal(request.headers.get("authorization"), `Bearer ${key}`);
    if (url.searchParams.has("redirect")) return Response.redirect("https://example.com");
    return Response.json({ path: url.pathname, query: url.searchParams.get("preview"),
      body: request.method === "POST" ? await request.json() : null },
      { status: request.method === "POST" ? 202 : 200 });
  },
});
try {
  process.env.BACKEND_URL = `http://127.0.0.1:${server.port}`;
  process.env.HORIZON_API_KEY = key;
  const result = await GET(new Request("http://frontend.local/api/timeline/LPPF?preview=true", {
    headers: { Authorization: "Bearer untrusted-browser-value" },
  }));
  assert.equal(result.status, 200);
  assert.equal(result.headers.get("cache-control"), "no-store");
  assert.deepEqual(await result.json(), { path: "/api/timeline/LPPF", query: "true", body: null });
  const post = await POST(new Request("http://frontend.local/api/simulations", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ capital: 100000 }),
  }));
  assert.equal(post.status, 202);
  assert.equal((await post.json()).body.capital, 100000);
  assert.equal((await GET(new Request("http://frontend.local/api/catalog?redirect=1"))).status, 502);
  const before = calls;
  process.env.BACKEND_URL = "http://example.com";
  assert.equal((await GET(new Request("http://frontend.local/api/catalog"))).status, 503);
  process.env.BACKEND_URL = "https://example.com";
  delete process.env.HORIZON_API_KEY;
  assert.equal((await GET(new Request("http://frontend.local/api/catalog"))).status, 503);
  assert.equal(calls, before);
  console.log(JSON.stringify({ status: "passed", checks: ["server key overrides browser header", "path and query preserved",
    "JSON body and status preserved", "no caching", "redirect not followed", "remote HTTP rejected", "missing remote key rejected"] }));
} finally {
  server.stop(true);
  if (originalUrl === undefined) delete process.env.BACKEND_URL; else process.env.BACKEND_URL = originalUrl;
  if (originalKey === undefined) delete process.env.HORIZON_API_KEY; else process.env.HORIZON_API_KEY = originalKey;
}
