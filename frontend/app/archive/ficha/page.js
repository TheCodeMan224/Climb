"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getUsuario } from "../../../lib/api";
import { t, getLang } from "../../../lib/i18n";
import Wordmark from "../../components/Wordmark";

export default function ArchiveFicha() {
  const router = useRouter();
  const [lang, setLang] = useState("en");
  const [ficha, setFicha] = useState(null);

  useEffect(() => {
    setLang(getLang());
    let f = null;
    try { f = JSON.parse(localStorage.getItem("climb_ficha")); } catch { f = null; }
    if (!f) router.push("/archive");
    else setFicha(f);
  }, [router]);

  const tr = (k) => t(k, lang);
  if (!ficha) return null;

  const tags = ficha.tags || [];
  const metrics = ficha.metrics || [];

  return (
    <main>
      <div className="topbar"><Wordmark /><Link className="back" href="/archive">{tr("back_archive")}</Link></div>
      <div className="eyebrow" style={{ marginBottom: 12 }}>{ficha._recien_generado ? tr("win_archived") : tr("from_archive_eyebrow")}</div>
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
      <h2>{tr("context")}</h2>
      <p>{ficha.contexto}</p>
      {ficha.mi_rol && (<><h2>{tr("my_role")}</h2><p>{ficha.mi_rol}</p></>)}
      {ficha.aprendizaje && (<><h2>{tr("takeaway")}</h2><p>{ficha.aprendizaje}</p></>)}
      {tags.length > 0 && <p className="muted" style={{ marginTop: 16 }}>{tags.map((t2) => `#${t2}`).join("  ")}</p>}
      <button className="btn" onClick={redactarEnEditor}>{tr("write_editor")}</button>
    </main>
  );

  function redactarEnEditor() {
    const partes = [
      ficha.titulo, ficha.contexto,
      ficha.mi_rol ? `My role: ${ficha.mi_rol}` : "",
      ficha.aprendizaje ? `Takeaway: ${ficha.aprendizaje}` : "",
      metrics.length ? `Metrics: ${metrics.map((m) => `${m.value} ${m.label}`).join(", ")}` : "",
    ].filter(Boolean);
    localStorage.setItem("climb_editor_contexto", JSON.stringify({ titulo: ficha.titulo, texto: partes.join(". ") }));
    router.push("/editor/estudio");
  }
}
