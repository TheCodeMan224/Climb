"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";
import Wordmark from "../components/Wordmark";

export default function Caminos() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [caminos, setCaminos] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    let diagnostico = null;
    try { diagnostico = JSON.parse(localStorage.getItem("climb_diagnostico")); } catch { diagnostico = null; }
    (async () => {
      try {
        const r = await api(`/api/usuarios/${u.id_usuario}/caminos`, { method: "POST", body: { diagnostico } });
        setCaminos(r.caminos || []);
      } catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

  async function elegir(camino) {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const alternativos = caminos.filter((c) => c !== camino);
      await api(`/api/usuarios/${user.id_usuario}/camino-elegido`, {
        method: "POST",
        body: {
          nombre_camino: camino.nombre || "",
          descripcion_camino: camino.descripcion || "",
          tradeoff_principal: camino.tradeoff_principal || "",
          riesgo_principal: camino.riesgo_principal || "",
          tiempo_estimado_semanal: camino.tiempo_estimado_semanal || "",
          patron_que_rompe: camino.patron_que_rompe || "",
          caminos_alternativos: alternativos,
        },
      });
      await api(`/api/usuarios/${user.id_usuario}/mision`, { method: "POST" });
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!user) return null;
  if (error) return <main><p className="error">{error}</p></main>;
  if (!caminos) return <main><p className="muted">{tr("preparing_paths")}</p></main>;

  return (
    <main style={{ maxWidth: 900 }}>
      <div className="topbar">
        <Wordmark href="/dashboard" />
        <span className="eyebrow">{tr("from_pacer")}</span>
      </div>
      <h1>{tr("caminos_title")}</h1>
      <p className="sub">{tr("caminos_sub")}</p>

      {caminos.map((c, i) => {
        const campos = [
          [tr("tradeoff"), c.tradeoff_principal],
          [tr("risk"), c.riesgo_principal],
          [tr("time_week"), c.tiempo_estimado_semanal],
          [tr("pattern_breaks"), c.patron_que_rompe],
        ];
        return (
          <div key={i} style={{ background: "var(--surface)", border: "1px solid var(--border)", borderTop: "3px solid var(--navy)", borderRadius: "0 0 8px 8px", padding: "clamp(28px,4vw,48px)", marginBottom: 24 }}>
            <div className="eyebrow" style={{ color: "var(--muted)", marginBottom: 18 }}>{tr("path_word")} {String(i + 1).padStart(2, "0")}</div>
            <h2 style={{ margin: "0 0 20px", fontSize: "clamp(24px,3.6vw,34px)" }}>{c.nombre}</h2>
            <p style={{ fontSize: 17, lineHeight: 1.65, margin: "0 0 28px", maxWidth: 720 }}>{c.descripcion}</p>

            {c.por_que_encaja && (
              <div className="pivote-rule" style={{ marginBottom: 32, maxWidth: 720 }}>
                <div className="eyebrow" style={{ marginBottom: 8 }}>{tr("why_fits")}</div>
                <p className="pivote" style={{ margin: 0 }}>{c.por_que_encaja}</p>
              </div>
            )}

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", borderTop: "1px solid var(--border)", borderLeft: "1px solid var(--border)", marginBottom: 32 }}>
              {campos.map(([lab, val], j) => (
                <div key={j} style={{ padding: "20px 24px", borderRight: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
                  <div className="eyebrow" style={{ color: "var(--muted)", fontSize: 11, marginBottom: 10 }}>{lab}</div>
                  <p style={{ fontSize: 15, lineHeight: 1.5, margin: 0 }}>{val}</p>
                </div>
              ))}
            </div>

            <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={() => elegir(c)}>
              {busy ? tr("preparing_mission") : tr("take_path")}
            </button>
          </div>
        );
      })}
    </main>
  );
}
