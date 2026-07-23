"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";
import { t, getLang } from "../../../lib/i18n";
import Wordmark from "../../components/Wordmark";
import AgentMark from "../../components/AgentMark";

export default function ArchiveChat() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [lang, setLang] = useState("en");
  const [turns, setTurns] = useState([]);
  const [texto, setTexto] = useState("");
  const [busy, setBusy] = useState(false);
  const [ofrecer, setOfrecer] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    const u = getUsuario();
    if (!u) { router.push("/login"); return; }
    const l = getLang();
    setUser(u); setLang(l);
    setTurns([["archive", t("archive_opening", l)]]);
  }, [router]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [turns, busy]);

  const tr = (k) => t(k, lang);

  async function enviar() {
    const msg = texto.trim();
    if (!msg || busy) return;
    const nuevos = [...turns, ["user", msg]];
    setTurns(nuevos); setTexto(""); setOfrecer(false); setBusy(true);
    try {
      const r = await api(`/api/usuarios/${user.id_usuario}/archive/mensaje`, { method: "POST", body: { turns: nuevos } });
      setTurns([...nuevos, ["archive", r.respuesta]]);
      setOfrecer(r.ofrecer_ficha);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  async function generarFicha() {
    setBusy(true);
    try {
      const ficha = await api(`/api/usuarios/${user.id_usuario}/archive/ficha`, { method: "POST", body: { turns } });
      localStorage.setItem("climb_ficha", JSON.stringify({ ...ficha, _recien_generado: true }));
      router.push("/archive/ficha");
    } catch (err) { setError(err.message); setBusy(false); }
  }

  if (!user) return null;

  return (
    <main>
      <div className="topbar"><Wordmark href="/dashboard" /><Link className="link" href="/archive">{tr("back_archive")}</Link></div>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 8 }}>
        <AgentMark name="Archive" size={40} />
        <h1 style={{ margin: 0 }}>Archive</h1>
      </div>
      <div style={{ margin: "16px 0" }}>
        {turns.map(([who, text], i) => (
          <div key={i} style={{ margin: "12px 0" }}>
            <div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{who === "user" ? tr("you") : "Archive"}</div>
            <div>{text}</div>
          </div>
        ))}
        {busy && <p className="muted">{tr("archive_typing")}</p>}
        <div ref={endRef} />
      </div>
      {error && <p className="error">{error}</p>}
      {ofrecer ? (
        <div className="row">
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={generarFicha}>{tr("yes_generate")}</button>
          <button className="link" onClick={() => setOfrecer(false)}>{tr("change_something")}</button>
        </div>
      ) : (
        <div className="row">
          <input value={texto} onChange={(e) => setTexto(e.target.value)} onKeyDown={(e) => e.key === "Enter" && enviar()} placeholder={tr("archive_placeholder")} />
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={enviar}>{tr("send")}</button>
        </div>
      )}
    </main>
  );
}
