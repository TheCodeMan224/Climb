"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

const COLOR = { verde: "#4a9d6a", ambar: "#BA7517", rojo: "#712B13" };

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

  return (
    <main style={{ maxWidth: 640 }}>
      <p className="muted" style={{ textTransform: "uppercase", fontSize: 12 }}>{tr("diag_sub")}</p>
      <h1>{tr("diag_saludo")}{d.nombre_usuario ? `, ${d.nombre_usuario}` : ""}</h1>

      {d.frase_pivote && <p className="pivote">{d.frase_pivote}</p>}
      {d.parrafo_narrativo && <p>{d.parrafo_narrativo}</p>}

      {retrato.lo_que_eres && (<div className="card"><div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{tr("what_you_are")}</div><p style={{ margin: "6px 0 0" }}>{retrato.lo_que_eres}</p></div>)}
      {retrato.lo_que_te_frena && (<div className="card"><div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{tr("what_holds")}</div><p style={{ margin: "6px 0 0" }}>{retrato.lo_que_te_frena}</p></div>)}
      {retrato.donde_esta_la_brecha && (<div className="card"><div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{tr("where_gap")}</div><p style={{ margin: "6px 0 0" }}>{retrato.donde_esta_la_brecha}</p></div>)}

      {(d.visibilidad || []).length > 0 && (
        <>
          <h2>{tr("visibility_h")}</h2>
          {d.visibilidad.map((v, i) => (
            <div key={i} style={{ margin: "10px 0" }}>
              <span style={{ display: "inline-block", width: 10, height: 10, borderRadius: 5, background: COLOR[v.estado] || "#ccc", marginRight: 8 }} />
              <strong>{v.dimension}</strong>
              <p className="muted" style={{ margin: "2px 0 0 18px" }}>{v.descripcion}</p>
            </div>
          ))}
        </>
      )}

      {(d.patrones || []).length > 0 && (
        <>
          <h2>{tr("patterns_h")}</h2>
          {d.patrones.map((p, i) => (
            <div className="card" key={i}><strong>{p.nombre}</strong><p className="muted" style={{ margin: "6px 0 0" }}>{p.descripcion}</p></div>
          ))}
        </>
      )}

      {(creencia.cita || creencia.reformulacion) && (
        <>
          <h2>{tr("limiting_belief")}</h2>
          <div className="card">
            {creencia.cita && <p style={{ fontStyle: "italic", margin: 0 }}>“{creencia.cita}”</p>}
            {creencia.reformulacion && <p style={{ color: "var(--amber)", margin: "8px 0 0" }}>{creencia.reformulacion}</p>}
          </div>
        </>
      )}

      {(estanc.categoria || estanc.subtitulo) && (
        <>
          <h2>{estanc.categoria}</h2>
          <p className="muted">{estanc.subtitulo}</p>
        </>
      )}

      {d.proximo_paso?.parrafo && (<><h2>{tr("next_step_h")}</h2><p>{d.proximo_paso.parrafo}</p></>)}

      <button className="btn" onClick={() => router.push("/caminos")}>{tr("see_plan")}</button>
    </main>
  );
}
