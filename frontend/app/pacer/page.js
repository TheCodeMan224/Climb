"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";
import Wordmark from "../components/Wordmark";

export default function Pacer() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [estado, setEstado] = useState(null);
  const [sinMision, setSinMision] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    (async () => {
      try { setEstado(await api(`/api/usuarios/${u.id_usuario}/mision`)); }
      catch { setSinMision(true); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

  async function toggle(i) {
    const progreso = estado.progreso.slice();
    progreso[i] = !progreso[i];
    setEstado({ ...estado, progreso });
    try { await api(`/api/misiones/${estado.id_mision}/progreso`, { method: "PATCH", body: { progreso } }); }
    catch (err) { setError(err.message); }
  }

  async function generar() {
    setBusy(true); setError("");
    try {
      await api(`/api/usuarios/${user.id_usuario}/mision`, { method: "POST" });
      setSinMision(false);
      setEstado(await api(`/api/usuarios/${user.id_usuario}/mision`));
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  async function completar() {
    setBusy(true);
    try {
      await api(`/api/misiones/${estado.id_mision}/completar`, { method: "POST" });
      router.push("/pacer/completada");
    } catch (err) { setError(err.message); setBusy(false); }
  }

  if (!user) return null;

  if (sinMision) {
    return (
      <main>
        <div className="topbar"><Wordmark /><Link className="back" href="/dashboard">{tr("back_dashboard")}</Link></div>
        <h1>{tr("pacer_week")}</h1>
        <p className="sub">{tr("no_active_mission")}</p>
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy} onClick={generar}>{busy ? tr("generating") : tr("generate_mission")}</button>
      </main>
    );
  }
  if (!estado) return <main><p className="muted">{tr("loading_mission")}</p></main>;

  const m = estado.mision;
  const total = (m.acciones || []).length;
  const hechas = estado.progreso.filter(Boolean).length;
  const allDone = total > 0 && hechas === total;
  const pct = total ? Math.round((hechas / total) * 100) : 0;

  return (
    <main style={{ maxWidth: 820 }}>
      <div className="topbar">
        <Wordmark />
        <Link className="back" href="/dashboard">{tr("back_dashboard")}</Link>
      </div>

      <div className="eyebrow" style={{ marginBottom: 10 }}>Pacer</div>
      <h1>{m.nombre_mision}</h1>
      <p className="sub">{m.descripcion}</p>

      {/* progress */}
      <div style={{ margin: "8px 0 28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
          <span className="muted" style={{ fontWeight: 600, letterSpacing: "0.16em", textTransform: "uppercase", fontSize: 12 }}>
            {hechas} {tr("actions_of")} {total} {tr("actions_word")}
          </span>
        </div>
        <div style={{ height: 2, background: "var(--border)", borderRadius: 1 }}>
          <div style={{ height: 2, width: `${pct}%`, background: "var(--gold)", borderRadius: 1, transition: "width .3s ease" }} />
        </div>
      </div>

      {/* checklist */}
      <div style={{ borderTop: "1px solid var(--border)" }}>
        {(m.acciones || []).map((a, i) => {
          const done = !!estado.progreso[i];
          return (
            <div key={i} onClick={() => toggle(i)} style={{ display: "flex", gap: 20, alignItems: "flex-start", padding: "22px 0", borderBottom: "1px solid var(--border)", cursor: "pointer" }}>
              <span style={{ fontFamily: "var(--syne)", fontWeight: 700, fontSize: 14, color: "var(--gold)", width: 22, flexShrink: 0, paddingTop: 3 }}>{String(i + 1).padStart(2, "0")}</span>
              <span style={{ width: 26, height: 26, borderRadius: 6, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", border: done ? "1.5px solid var(--green)" : "1.5px solid #C9C7C0", background: done ? "var(--green)" : "var(--surface)" }}>
                {done && (
                  <svg viewBox="0 0 24 24" width="15" height="15" fill="none"><path d="M5 12.5 L10 17 L19 7" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" /></svg>
                )}
              </span>
              <p style={{ fontSize: 16, lineHeight: 1.55, margin: 0, color: done ? "#9A988F" : "var(--navy)", textDecoration: done ? "line-through" : "none", textDecorationColor: "rgba(46,125,82,0.5)" }}>{a}</p>
            </div>
          );
        })}
      </div>

      {m.conexion_camino && (
        <div className="card" style={{ background: "var(--navy)", color: "var(--offwhite)", marginTop: 28, border: "none" }}>
          <div className="eyebrow" style={{ marginBottom: 10 }}>{tr("connection_path")}</div>
          <p style={{ margin: 0 }}>{m.conexion_camino}</p>
        </div>
      )}
      {error && <p className="error">{error}</p>}
      {allDone && <button className="btn" disabled={busy} onClick={completar}>{busy ? tr("closing") : tr("complete_mission")}</button>}
    </main>
  );
}
