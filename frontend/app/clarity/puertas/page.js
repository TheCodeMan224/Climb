"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../../lib/api";
import { t, getLang } from "../../../lib/i18n";
import Wordmark from "../../components/Wordmark";

export default function ClarityPuertas() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [cierre, setCierre] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    let turns = [];
    try { turns = JSON.parse(localStorage.getItem("climb_clarity_turns")) || []; } catch { turns = []; }
    (async () => {
      try { setCierre(await api(`/api/usuarios/${u.id_usuario}/clarity/cierre`, { method: "POST", body: { turns } })); }
      catch (err) { setError(err.message); }
    })();
  }, [router]);

  const tr = (k) => t(k, lang);

  function puertaMirror() {
    const patron = { id: "clarity:patron", quote: cierre.patron_quote, source: "user", scout_ref: null, sesion: null };
    localStorage.setItem("climb_mirror_patron", JSON.stringify(patron));
    router.push("/mirror/session");
  }

  if (!user) return null;
  if (error) return <main><p className="error">{error}</p></main>;
  if (!cierre) return <main><p className="muted">{tr("closing_conv")}</p></main>;

  const rec = cierre.puerta_recomendada;
  const Puerta = ({ n, tag, titulo, desc, onClick }) => (
    <div className="card" onClick={onClick} style={{ cursor: "pointer", borderColor: rec === n ? "var(--amber)" : "var(--border)" }}>
      <div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{tag}{rec === n ? ` · ${tr("recommended")}` : ""}</div>
      <strong>{titulo}</strong>
      <p className="muted" style={{ margin: "6px 0 0" }}>{desc}</p>
    </div>
  );

  return (
    <main>
      <div className="topbar"><Wordmark /><button className="back" onClick={() => router.push("/clarity")}>← Clarity</button></div>
      <h1>{tr("next_up_to_you")}</h1>
      <p className="pivote">{cierre.sintesis}</p>
      <p className="sub">{cierre.pregunta}</p>

      <Puerta n={1} tag={tr("door1_tag")} titulo={tr("door1_title")} desc={tr("door1_desc")} onClick={() => router.push("/dashboard")} />
      {cierre.hay_patron && (
        <Puerta n={2} tag={tr("door2_tag")} titulo={tr("door2_title")} desc={`"${cierre.patron_quote}"`} onClick={puertaMirror} />
      )}
      {cierre.hay_accion && (
        <Puerta n={3} tag={tr("door3_tag")} titulo={tr("door3_title")} desc={`"${cierre.accion_texto}"`} onClick={() => router.push("/pacer")} />
      )}
      <button className="link" onClick={() => router.push("/clarity/conversacion")} style={{ background: "none", border: "none", cursor: "pointer", marginTop: 16 }}>{tr("keep_talking")}</button>
    </main>
  );
}
