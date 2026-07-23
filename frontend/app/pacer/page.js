"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

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
        <Link className="link" href="/dashboard">{tr("back_dashboard")}</Link>
        <h1 style={{ marginTop: 16 }}>{tr("pacer_week")}</h1>
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

  return (
    <main>
      <Link className="link" href="/dashboard">{tr("back_dashboard")}</Link>
      <h2 style={{ marginTop: 16 }}>Pacer · {hechas} {tr("actions_of")} {total} {tr("actions_word")}</h2>
      <h1>{m.nombre_mision}</h1>
      <p className="sub">{m.descripcion}</p>
      <div className="card">
        {(m.acciones || []).map((a, i) => (
          <label key={i} style={{ display: "flex", gap: 10, margin: "10px 0", cursor: "pointer" }}>
            <input type="checkbox" checked={!!estado.progreso[i]} onChange={() => toggle(i)} style={{ width: "auto" }} />
            <span style={{ textDecoration: estado.progreso[i] ? "line-through" : "none" }}>{a}</span>
          </label>
        ))}
      </div>
      {m.conexion_camino && (
        <div className="card" style={{ background: "var(--navy)", color: "var(--offwhite)" }}>
          <strong>{tr("connection_path")}</strong>
          <p style={{ margin: "6px 0 0" }}>{m.conexion_camino}</p>
        </div>
      )}
      {error && <p className="error">{error}</p>}
      {allDone && <button className="btn" disabled={busy} onClick={completar}>{busy ? tr("closing") : tr("complete_mission")}</button>}
    </main>
  );
}
