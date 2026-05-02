const test = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");

process.env.AUTH_SECRET = "test-secret-do-not-use";
process.env.APP_PASSWORD_DASH = "letmein";
process.env.APP_TITLE_DASH = "Dashboard";
process.env.NO_AUTH_APPS = "openapp";

const { buildApp, _internals } = require("./server");
const {
  isValidSlug,
  safeNext,
  escapeHtml,
  safeEqual,
  cookieName,
  makeSessionToken,
} = _internals;

// ── Pure-function tests ──────────────────────────────────────────────────────

test("isValidSlug accepts simple slugs", () => {
  for (const slug of ["app", "my-app", "a", "ab", "a1", "abc-def-123"]) {
    assert.equal(isValidSlug(slug), true, slug);
  }
});

test("isValidSlug rejects shell, path, and HTML metacharacters", () => {
  const bad = [
    "",
    "-app",
    "app-",
    "App",
    "../etc",
    "a/b",
    "a b",
    "a.b",
    "<script>",
    "x".repeat(33),
    "a;b",
    "a%20b",
    null,
    undefined,
    123,
  ];
  for (const slug of bad) {
    assert.equal(isValidSlug(slug), false, JSON.stringify(slug));
  }
});

test("escapeHtml neutralizes the standard XSS vectors", () => {
  assert.equal(
    escapeHtml(`<img src=x onerror="alert(1)">&'"`),
    "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;&amp;&#39;&quot;"
  );
});

test("safeNext keeps the redirect inside the app's path", () => {
  assert.equal(safeNext("dash", "/dash/page?x=1"), "/dash/page?x=1");
  assert.equal(safeNext("dash", "/dash/"), "/dash/");
});

test("safeNext blocks open redirects and traversal", () => {
  const cases = [
    "//evil.com/x",
    "https://evil.com/x",
    "/other-app/page",
    "/dash", // missing trailing slash
    "/dash/../other",
    "/dash/foo/../../etc",
    "/dash/%2e%2e/etc",
    "/dash/%2E%2E/etc",
    "javascript:alert(1)",
    "",
    null,
    undefined,
  ];
  for (const next of cases) {
    assert.equal(safeNext("dash", next), "/dash/", JSON.stringify(next));
  }
});

test("safeEqual is constant-time on equal-length inputs", () => {
  assert.equal(safeEqual("abcd", "abcd"), true);
  assert.equal(safeEqual("abcd", "abce"), false);
  assert.equal(safeEqual("abc", "abcd"), false);
  assert.equal(safeEqual(undefined, "abcd"), false);
  assert.equal(safeEqual("abcd", null), false);
});

test("cookieName is stable and unique across valid slugs", () => {
  assert.equal(cookieName("my-app"), "oc_auth_my_app");
  assert.equal(cookieName("dash"), "oc_auth_dash");
  // Underscores are not in the slug alphabet, so distinct valid slugs cannot
  // collide via the dash→underscore rewrite.
  assert.notEqual(cookieName("a-b"), cookieName("ab"));
});

test("makeSessionToken depends on slug, password, and secret", () => {
  const t1 = makeSessionToken("a", "pw");
  const t2 = makeSessionToken("a", "pw");
  const t3 = makeSessionToken("b", "pw");
  const t4 = makeSessionToken("a", "px");
  assert.equal(t1, t2, "deterministic");
  assert.notEqual(t1, t3, "slug-scoped");
  assert.notEqual(t1, t4, "password-scoped");
});

// ── HTTP-level integration tests ─────────────────────────────────────────────

const startServer = () =>
  new Promise((resolve) => {
    const app = buildApp();
    const server = app.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve({ server, base: `http://127.0.0.1:${port}` });
    });
  });

const fetchManual = (url, init = {}) =>
  fetch(url, { redirect: "manual", ...init });

const sameOriginPost = (base, path, body) => {
  const host = new URL(base).host;
  return fetchManual(`${base}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      Origin: `http://${host}`,
    },
    body,
  });
};

test("verify rejects bad slugs and missing cookies", async () => {
  const { server, base } = await startServer();
  try {
    let r = await fetch(`${base}/auth/verify?app=../etc`);
    assert.equal(r.status, 400);

    r = await fetch(`${base}/auth/verify?app=dash`);
    assert.equal(r.status, 401);

    r = await fetch(`${base}/auth/verify?app=openapp`); // NO_AUTH_APPS bypass
    assert.equal(r.status, 200);
  } finally {
    server.close();
  }
});

test("login GET for an open app skips the form and redirects through", async () => {
  const { server, base } = await startServer();
  try {
    const r = await fetchManual(
      `${base}/auth/login?app=openapp&next=/openapp/page`
    );
    assert.equal(r.status, 303);
    assert.equal(r.headers.get("location"), "/openapp/page");
  } finally {
    server.close();
  }
});

test("login GET escapes injected slug-like values via 400, not raw HTML", async () => {
  const { server, base } = await startServer();
  try {
    const r = await fetch(
      `${base}/auth/login?app=${encodeURIComponent("<script>alert(1)</script>")}`
    );
    assert.equal(r.status, 400);
    const body = await r.text();
    assert.equal(body.includes("<script>"), false);
  } finally {
    server.close();
  }
});

test("login POST without same-origin Origin/Referer is rejected", async () => {
  const { server, base } = await startServer();
  try {
    // No Origin header at all.
    let r = await fetchManual(`${base}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: "app=dash&password=letmein",
    });
    assert.equal(r.status, 403);

    // Origin from a different host.
    r = await fetchManual(`${base}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Origin: "https://evil.example",
      },
      body: "app=dash&password=letmein",
    });
    assert.equal(r.status, 403);
  } finally {
    server.close();
  }
});

test("login POST with correct password issues a path-scoped, httpOnly, Secure cookie", async () => {
  const { server, base } = await startServer();
  try {
    const r = await sameOriginPost(
      base,
      "/auth/login",
      "app=dash&next=/dash/inner&password=letmein"
    );
    assert.equal(r.status, 303);
    assert.equal(r.headers.get("location"), "/dash/inner");
    const setCookie = r.headers.get("set-cookie") || "";
    assert.match(setCookie, /HttpOnly/i);
    assert.match(setCookie, /Secure/i);
    assert.match(setCookie, /SameSite=Lax/i);
    assert.match(setCookie, /Path=\/dash\//);
  } finally {
    server.close();
  }
});

test("login POST with wrong password redirects with error and sets no cookie", async () => {
  const { server, base } = await startServer();
  try {
    const r = await sameOriginPost(
      base,
      "/auth/login",
      "app=dash&next=/dash/&password=nope"
    );
    assert.equal(r.status, 303);
    assert.match(r.headers.get("location") || "", /error=1/);
    assert.equal(r.headers.get("set-cookie"), null);
  } finally {
    server.close();
  }
});

test("login POST for unconfigured app does NOT mint a cookie (M-1)", async () => {
  const { server, base } = await startServer();
  try {
    // No APP_PASSWORD_GHOST set anywhere.
    const r = await sameOriginPost(
      base,
      "/auth/login",
      "app=ghost&password=anything"
    );
    assert.equal(r.status, 303);
    assert.equal(r.headers.get("set-cookie"), null);
    assert.equal(r.headers.get("location"), "/ghost/");
  } finally {
    server.close();
  }
});

test("login POST for NO_AUTH_APPS slug short-circuits without a cookie", async () => {
  const { server, base } = await startServer();
  try {
    const r = await sameOriginPost(
      base,
      "/auth/login",
      "app=openapp&password=anything"
    );
    assert.equal(r.status, 303);
    assert.equal(r.headers.get("set-cookie"), null);
  } finally {
    server.close();
  }
});

test("end-to-end: correct password → cookie → verify=200", async () => {
  const { server, base } = await startServer();
  try {
    const login = await sameOriginPost(
      base,
      "/auth/login",
      "app=dash&next=/dash/&password=letmein"
    );
    const cookie = (login.headers.get("set-cookie") || "").split(";")[0];
    const verify = await fetch(`${base}/auth/verify?app=dash`, {
      headers: { Cookie: cookie },
    });
    assert.equal(verify.status, 200);
  } finally {
    server.close();
  }
});
