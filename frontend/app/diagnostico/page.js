"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUsuario } from "../../lib/api";

const COLOR = { verde: "#4a9d6a", ambar: "#d99a3a", rojo: "#e06a5a" };

export default function Diagnostico() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [d, setD] = useState(null);

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    try {
      const diag = JSON.parse(localStorage.getItem("climb_diagnostico"));
      if (!diag) router.push("/dashboard");
      else setD(diag);
    } catch {
      router.push("/dashboard");
    }
  }, [router]);

  if (!user || !d) return null;

  const retrato = d.retrato || {};
  const creencia = d.creencia_limitante || {};
  const estanc = d.tipo_estancamiento || {};

  return (
    <main style={{ maxWidth: 640 }}>
      <p className="muted" style={{ textTransform: "uppercase", fontSize: 12 }}>Your qualitative diagnosis</p>
      <h1>This is what I saw in you{d.nombre_usuario ? `, ${d.nombre_usuario}` : ""}</h1>

      {d.frase_pivote && <p className="pivote">{d.frase_pivote}</p>}
      {d.parrafo_narrativo && <p>{d.parrafo_narrativo}</p>}

      {(retrato.lo_que_eres || retrato.lo_que_te_frena || retrato.donde_esta_la_brecha) && (
        <>
          {retrato.lo_que_eres && (<div className="card"><div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>What you are</div><p style={{ margin: "6px 0 0" }}>{retrato.lo_que_eres}</p></div>)}
          {retrato.lo_que_te_frena && (<div className="card"><div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>What holds you back</div><p style={{ margin: "6px 0 0" }}>{retrato.lo_que_te_frena}</p></div>)}
          {retrato.donde_esta_la_brecha && (<div className="card"><div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>Where the gap is</div><p style={{ margin: "6px 0 0" }}>{retrato.donde_esta_la_brecha}</p></div>)}
        </>
      )}

      {(d.visibilidad || []).length > 0 && (
        <>
          <h2>Your strategic visibility today</h2>
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
          <h2>The patterns Scout detected</h2>
          {d.patrones.map((p, i) => (
            <div className="card" key={i}><strong>{p.nombre}</strong><p className="muted" style={{ margin: "6px 0 0" }}>{p.descripcion}</p></div>
          ))}
        </>
      )}

      {(creencia.cita || creencia.reformulacion) && (
        <>
          <h2>A limiting belief</h2>
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

      {d.proximo_paso?.parrafo && (<><h2>Your next step</h2><p>{d.proximo_paso.parrafo}</p></>)}

      <button className="btn" onClick={() => router.push("/caminos")}>See my plan for the next 30 days →</button>
    </main>
  );
}
