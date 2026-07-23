"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

export default function MirrorHub() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [hub, setHub] = useState(null);
  const [quote, setQuote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    (async () => {
      try { setHub(await api(`/api/usuarios/${u.id_usuario}/mirror/hub`)); }
      catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

  function abrir(patron) {
    localStorage.setItem("climb_mirror_patron", JSON.stringify(patron));
    router.push("/mirror/session");
  }

  async function nuevoPatron() {
    const q = quote.trim();
    if (!q || busy) return;
    setBusy(true);
    try {
      const r = await api(`/api/usuarios/${user.id_usuario}/mirror/patron`, { method: "POST", body: { quote: q } });
      abrir({ id: r.id, quote: q, source: "user", status: "pending", sesion: null });
    } catch (err) { setError(err.message); setBusy(false); }
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/dashboard">{tr("back_dashboard")}</Link>
      <h1 style={{ marginTop: 16 }}>{tr("mirror")}</h1>
      <p className="sub">{tr("mirror_intro")}</p>
      {error && <p className="error">{error}</p>}
      {hub && (
        <>
          <h2>{tr("pending_patterns")}</h2>
          {hub.pendientes.length === 0 && <p className="muted">{tr("no_patterns_now")}</p>}
          {hub.pendientes.map((p) => (
            <div className="card" key={p.id} onClick={() => abrir(p)} style={{ cursor: "pointer" }}>
              <strong>{p.quote}</strong>
              <p className="muted" style={{ margin: "6px 0 0" }}>
                {p.detected_meta}{p.en_progreso ? ` · ${tr("in_progress")} (${p.respuestas_en_progreso} ${tr("answered")})` : ""}
              </p>
            </div>
          ))}
          <h2>{tr("under_observation")}</h2>
          {hub.observando.length === 0 && <p className="muted">{tr("nothing_processed")}</p>}
          {hub.observando.map((p) => (
            <div className="card" key={p.id}>
              <p className="muted" style={{ textDecoration: "line-through", margin: 0 }}>{p.reframe?.old_quote || p.quote}</p>
              <strong style={{ color: "var(--amber)" }}>{p.reframe?.new_quote}</strong>
              <p className="muted" style={{ margin: "6px 0 0" }}>{p.observed_meta}</p>
            </div>
          ))}
          <h2>{tr("work_own_pattern")}</h2>
          <textarea value={quote} onChange={(e) => setQuote(e.target.value)} placeholder={tr("mirror_placeholder")} />
          <button className="btn" disabled={busy} onClick={nuevoPatron}>{busy ? tr("starting") : tr("start_session")}</button>
        </>
      )}
    </main>
  );
}
