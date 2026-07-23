"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function ArchiveFicha() {
  const router = useRouter();
  const [ficha, setFicha] = useState(null);

  useEffect(() => {
    let f = null;
    try {
      f = JSON.parse(localStorage.getItem("climb_ficha"));
    } catch {
      f = null;
    }
    if (!f) router.push("/archive");
    else setFicha(f);
  }, [router]);

  if (!ficha) return null;

  const tags = ficha.tags || [];
  const metrics = ficha.metrics || [];

  return (
    <main>
      <Link className="link" href="/archive">← Back to the archive</Link>
      <p className="muted" style={{ marginTop: 16 }}>
        {ficha._recien_generado ? "Win archived" : "From the archive"}
      </p>
      <h1>{ficha.titulo}</h1>
      <p className="muted">{ficha.tipo}{ficha.fecha_corta ? ` · ${ficha.fecha_corta}` : ""}</p>

      {metrics.length > 0 && (
        <div className="row" style={{ gap: 24, marginTop: 8 }}>
          {metrics.map((m, i) => (
            <div key={i}>
              <div style={{ fontSize: 22, fontWeight: 700, color: "var(--amber)" }}>{m.value}</div>
              <div className="muted">{m.label}</div>
            </div>
          ))}
        </div>
      )}

      <h2>Context</h2>
      <p>{ficha.contexto}</p>
      {ficha.mi_rol && (<><h2>My specific role</h2><p>{ficha.mi_rol}</p></>)}
      {ficha.aprendizaje && (<><h2>Takeaway</h2><p>{ficha.aprendizaje}</p></>)}
      {tags.length > 0 && (
        <p className="muted" style={{ marginTop: 16 }}>{tags.map((t) => `#${t}`).join("  ")}</p>
      )}

      <button className="btn" onClick={redactarEnEditor}>Write with Editor →</button>
    </main>
  );

  function redactarEnEditor() {
    const partes = [
      ficha.titulo,
      ficha.contexto,
      ficha.mi_rol ? `My role: ${ficha.mi_rol}` : "",
      ficha.aprendizaje ? `Takeaway: ${ficha.aprendizaje}` : "",
      metrics.length ? `Metrics: ${metrics.map((m) => `${m.value} ${m.label}`).join(", ")}` : "",
    ].filter(Boolean);
    localStorage.setItem("climb_editor_contexto", JSON.stringify({ titulo: ficha.titulo, texto: partes.join(". ") }));
    router.push("/editor/estudio");
  }
}
