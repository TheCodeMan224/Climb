"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";
import Wordmark from "../components/Wordmark";

const COLOR = { verde: "var(--green)", ambar: "var(--func-amber)", rojo: "var(--red)" };

export default function Diagnostico() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [d, setD] = useState(null);

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    try {
      const diag = JSON.parse(localStorage.getItem("climb_diagnostico"));
      if (!diag) router.push("/dashboard");
      else setD(diag);
    } catch { router.push("/dashboard"); }
  }, [router]);

  const tr = (k) => t(k, lang);
  if (!user || !d) return null;

  const retrato = d.retrato || {};
  const creencia = d.creencia_limitante || {};
  const estanc = d.tipo_estancamiento || {};

  const Retrato = ({ eyebrow, color, texto }) =>
    texto ? (
      <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderTop: `3px solid ${color}`, borderRadius: "0 0 8px 8px", padding: "28px 26px" }}>
        <div className="eyebrow" style={{ color, letterSpacing: "0.16em", marginBottom: 16 }}>{eyebrow}</div>
        <p style={{ fontSize: 15, lineHeight: 1.6, margin: 0 }}>{texto}</p>
      </div>
    ) : null;

  return (
    <main style={{ maxWidth: 900 }}>
      <div className="topbar"><Wordmark href="/dashboard" /></div>

      <div className="eyebrow" style={{ marginBottom: 20 }}>{tr("diag_sub")}</div>
      <h1>{tr("diag_saludo")}{d.nombre_usuario ? `, ${d.nombre_usuario}` : ""}</h1>

      {d.frase_pivote && (
        <div className="pivote-rule" style={{ margin: "12px 0 40px" }}>
          <blockquote style={{ margin: 0, fontFamily: "var(--syne)", fontWeight: 600, fontSize: "clamp(28px,4.6vw,44px)", lineHeight: 1.18, letterSpacing: "-0.02em" }}>
            {d.frase_pivote}
          </blockquote>
        </div>
      )}
      {d.parrafo_narrativo && <p style={{ fontSize: 18, lineHeight: 1.7, maxWidth: 720 }}>{d.parrafo_narrativo}</p>}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 24, marginTop: 48 }}>
        <Retrato eyebrow={tr("what_you_are")} color="var(--navy)" texto={retrato.lo_que_eres} />
        <Retrato eyebrow={tr("what_holds")} color="var(--red)" texto={retrato.lo_que_te_frena} />
        <Retrato eyebrow={tr("where_gap")} color="var(--gold)" texto={retrato.donde_esta_la_brecha} />
      </div>

      {(d.visibilidad || []).length > 0 && (
        <>
          <h2>{tr("visibility_h")}</h2>
          <div style={{ borderTop: "1px solid var(--gold)" }}>
            {d.visibilidad.map((v, i) => (
              <div key={i} style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 16, alignItems: "start", padding: "20px 0", borderBottom: "1px solid var(--border)" }}>
                <span style={{ width: 10, height: 10, borderRadius: 5, background: COLOR[v.estado] || "#ccc", marginTop: 7 }} />
                <div>
                  <strong style={{ fontFamily: "var(--syne)", fontWeight: 600, fontSize: 17 }}>{v.dimension}</strong>
                  <p className="muted" style={{ margin: "4px 0 0", lineHeight: 1.55 }}>{v.descripcion}</p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {(d.patrones || []).length > 0 && (
        <>
          <h2>{tr("patterns_h")}</h2>
          {d.patrones.map((p, i) => (
            <div className="card" key={i}><strong>{p.nombre}</strong><p className="muted" style={{ margin: "8px 0 0" }}>{p.descripcion}</p></div>
          ))}
        </>
      )}

      {(creencia.cita || creencia.reformulacion) && (
        <>
          <h2>{tr("limiting_belief")}</h2>
          <div className="card">
            {creencia.cita && <p className="pivote" style={{ margin: 0 }}>“{creencia.cita}”</p>}
            {creencia.reformulacion && <p style={{ color: "var(--gold)", fontWeight: 600, margin: "10px 0 0" }}>{creencia.reformulacion}</p>}
          </div>
        </>
      )}

      {(estanc.categoria || estanc.subtitulo) && (
        <>
          <h2>{estanc.categoria}</h2>
          <p className="muted">{estanc.subtitulo}</p>
        </>
      )}

      {d.proximo_paso?.parrafo && (<><h2>{tr("next_step_h")}</h2><p style={{ fontSize: 17, lineHeight: 1.7 }}>{d.proximo_paso.parrafo}</p></>)}

      <button className="btn" onClick={() => router.push("/caminos")}>{tr("see_plan")}</button>
    </main>
  );
}
