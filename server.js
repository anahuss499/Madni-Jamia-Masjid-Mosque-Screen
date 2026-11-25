// Madni Jamia Masjid screen server – no dependencies, Node 18+
const http = require("http"),
  fs = require("fs"),
  path = require("path");
const PORT = process.env.PORT || 3000,
  PASS = process.env.ADMIN_PASSWORD || "changeme",
  AIKEY = process.env.ANTHROPIC_API_KEY || "";
const D = path.join(__dirname, "data"),
  U = path.join(D, "uploads"),
  F = path.join(D, "settings.json"),
  PUB = path.join(__dirname, "public");
fs.mkdirSync(U, { recursive: true });
const MIME = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
};
const send = (res, code, obj) => {
  res.writeHead(code, {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  });
  res.end(JSON.stringify(obj));
};
const body = (req) =>
  new Promise((ok, no) => {
    let n = 0,
      c = [];
    req.on("data", (d) => {
      n += d.length;
      if (n > 25e6) {
        no(new Error("File too large"));
        req.destroy();
      } else c.push(d);
    });
    req.on("end", () => ok(Buffer.concat(c).toString()));
    req.on("error", no);
  });
const authed = (req) => req.headers["x-admin-key"] === PASS;
function file(res, dir, rel) {
  const p = path.join(dir, path.normalize(rel).replace(/^(\.\.[\/\\])+/, ""));
  if (!p.startsWith(dir) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) {
    res.writeHead(404);
    return res.end("Not found");
  }
  res.writeHead(200, {
    "Content-Type":
      MIME[path.extname(p).toLowerCase()] || "application/octet-stream",
  });
  fs.createReadStream(p).pipe(res);
}

http
  .createServer(async (req, res) => {
    const u = new URL(req.url, "http://x"),
      p = u.pathname;
    try {
      if (p === "/api/settings" && req.method === "GET") {
        return send(
          res,
          200,
          fs.existsSync(F) ? JSON.parse(fs.readFileSync(F, "utf8")) : {},
        );
      }
      if (p.startsWith("/api/") && !authed(req))
        return send(res, 401, { error: "Wrong password" });
      if (p === "/api/auth") return send(res, 200, { ok: true, ai: !!AIKEY });
      if (p === "/api/settings" && req.method === "PUT") {
        const s = JSON.parse(await body(req));
        s.ver = Date.now();
        fs.writeFileSync(F, JSON.stringify(s));
        return send(res, 200, { ok: true, ver: s.ver });
      }
      if (p === "/api/upload" && req.method === "POST") {
        const { name, data } = JSON.parse(await body(req));
        const m = /^data:image\/(png|jpe?g|webp|gif);base64,(.+)$/.exec(
          data || "",
        );
        if (!m)
          return send(res, 400, {
            error: "Upload a PNG, JPG, WebP or GIF image",
          });
        const fn =
          Date.now() +
          "-" +
          String(name || "image")
            .replace(/[^\w.-]/g, "_")
            .replace(/\.[^.]*$/, "") +
          "." +
          m[1].replace("jpeg", "jpg");
        fs.writeFileSync(path.join(U, fn), Buffer.from(m[2], "base64"));
        return send(res, 200, { name: fn });
      }
      if (p === "/api/upload" && req.method === "DELETE") {
        fs.rmSync(
          path.join(U, path.basename(u.searchParams.get("name") || "")),
          { force: true },
        );
        return send(res, 200, { ok: true });
      }
      if (p === "/api/extract" && req.method === "POST") {
        if (!AIKEY)
          return send(res, 501, {
            error: "Set ANTHROPIC_API_KEY on the server to use AI reading",
          });
        const { name, keys } = JSON.parse(await body(req)),
          fp = path.join(U, path.basename(name || "")),
          ext = path.extname(fp).slice(1).replace("jpg", "jpeg");
        const img = fs.readFileSync(fp).toString("base64");
        const r = await fetch("https://api.anthropic.com/v1/messages", {
          method: "POST",
          headers: {
            "x-api-key": AIKEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
          },
          body: JSON.stringify({
            model: "claude-sonnet-5-5",
            max_tokens: 8000,
            messages: [
              {
                role: "user",
                content: [
                  {
                    type: "image",
                    source: {
                      type: "base64",
                      media_type: "image/" + ext,
                      data: img,
                    },
                  },
                  {
                    type: "text",
                    text:
                      'This is a monthly mosque prayer timetable. Return ONLY a JSON array with one object per day: {"day":<1-31>, ' +
                      keys.map((k) => '"' + k + '":"HH:MM"').join(", ") +
                      "}. Columns are in this order: " +
                      keys.join(", ") +
                      ". Use 24-hour HH:MM (convert pm times). Use null for unreadable cells. No other text.",
                  },
                ],
              },
            ],
          }),
        });
        const j = await r.json();
        if (!r.ok)
          return send(res, 502, {
            error: (j.error && j.error.message) || "AI request failed",
          });
        const t = (j.content || [])
          .map((c) => c.text || "")
          .join("")
          .replace(/```json|```/g, "")
          .trim();
        return send(res, 200, { rows: JSON.parse(t) });
      }
      if (p.startsWith("/uploads/"))
        return file(res, U, decodeURIComponent(p.slice(9)));
      file(
        res,
        PUB,
        p === "/" ? "index.html" : p === "/admin" ? "admin.html" : p.slice(1),
      );
    } catch (e) {
      send(res, 500, { error: e.message });
    }
  })
  .listen(PORT, () =>
    console.log(
      "Screen: http://localhost:" +
        PORT +
        "   Admin: http://localhost:" +
        PORT +
        "/admin" +
        (PASS === "changeme"
          ? "   (set ADMIN_PASSWORD – default is 'changeme')"
          : ""),
    ),
  );
