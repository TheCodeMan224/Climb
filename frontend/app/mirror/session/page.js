"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";
import { t, getLang } from "../../../lib/i18n";

export default function MirrorSession() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [patron, setPatron] = useState(null);
  const [turns, setTurns] = useState([]);
  const [pregunta, setPregunta] = useState("");
  const [respuesta, setRespuesta] = useState("");
  const [boundary, setBoundary] = useState(false);
  const [listo, setListo] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    setUser(u); setLang(getLang());
    let p = null;
    try { p = JSON.parse(localStorage.getItem("climb_mirror_patron")); } catch { p = null; }
    if (!p) { router.push("/mirror"); return; }
    setPatron(p);
    const iniciales = p.sesion?.turns || [];
    setTurns(iniciales);
    fetchPregunta(u, p.quote, iniciales, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  const tr = (k) => t(k, lang);

  async function fetchPregunta(u, quote, tn, reanclar) {
    setBusy(true);
    try {
      const r = await api(`/api/usuarios/${u.id_usuario}/mirror/pregunta`, { method: "POST", body: { quote, turns: tn, reanclar } });
      setPregunta(r.pregunta); setListo(r.listo);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  async function responder() {
    const ans = respuesta.trim();
    if (!ans || busy) return;
    const nuevos = [...turns, ["mirror", pregunta], ["user", ans]];
    setTurns(nuevos); setRespuesta(""); setBusy(true); setError("");
    try {
      const b = await api(`/api/usuarios/${user.id_usuario}/mirror/boundary`, { method: "POST", body: { texto: ans } });
      if (b.boundary) { setBoundary(true); setBusy(false); return; }
      await fetchPregunta(user, patron.quote, nuevos, false);
    } catch (err) { setError(err.message); setBusy(false); }
  }

  async function verEspejo() {
    setBusy(true);
    try {
      const reframe = await api(`/api/usuarios/${user.id_usuario}/mirror/reframe`, { method: "POST", body: { quote: patron.quote, turns } });
      localStorage.setItem("climb_mirror_reframe", JSON.stringify(reframe));
      router.push("/mirror/espejo");
    } catch (err) { setError(err.message); setBusy(false); }
  }

  async function dejar() {
    try {
      await api(`/api/usuarios/${user.id_usuario}/mirror/dejar`, {
        method: "POST", body: { id: patron.id, quote: patron.quote, source: patron.source, scout_ref: patron.scout_ref, turns },
      });
    } catch { /* */ }
    router.push("/mirror");
  }

  if (!user || !patron) return null;

  const respondidas = turns.filter((tn) => tn[0] === "user").length;
  const puedeCerrar = listo || respondidas >= 3;

  if (boundary) {
    return (
      <main>
        <h2>{tr("mirror_responds")}</h2>
        <p>{tr("boundary1")}</p>
        <p className="muted">{tr("boundary2")}</p>
        <div className="row">
          <button className="btn" style={{ marginTop: 0 }} onClick={() => router.push("/mirror")}>{tr("end_session")}</button>
          <button className="link" onClick={() => { setBoundary(false); fetchPregunta(user, patron.quote, turns, true); }}>{tr("back_to_pattern")}</button>
        </div>
      </main>
    );
  }

  return (
    <main>
      <Link className="link" href="/mirror">← Mirror</Link>
      <p className="muted" style={{ marginTop: 16 }}>{tr("pattern_label")} {patron.quote}</p>
      <h1>{tr("onb_progress")} {respondidas + 1}</h1>
      <p className="pivote">{busy && !pregunta ? tr("mirror_preparing") : pregunta}</p>
      {error && <p className="error">{error}</p>}
      <div className="row">
        <input value={respuesta} onChange={(e) => setRespuesta(e.target.value)} onKeyDown={(e) => e.key === "Enter" && responder()} placeholder={tr("mirror_placeholder2")} />
        <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={responder}>{tr("send")}</button>
      </div>
      <div className="row" style={{ marginTop: 20 }}>
        {puedeCerrar && <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={verEspejo}>{tr("see_mirror")}</button>}
        <button className="link" onClick={dejar}>{tr("leave_later")}</button>
      </div>
    </main>
  );
}
