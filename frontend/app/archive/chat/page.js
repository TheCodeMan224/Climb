"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";

const APERTURA = "Tell me what happened this week that's worth saving. It doesn't have to be huge.";

export default function ArchiveChat() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [turns, setTurns] = useState([["archive", APERTURA]]);
  const [texto, setTexto] = useState("");
  const [busy, setBusy] = useState(false);
  const [ofrecer, setOfrecer] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    const u = getUsuario();
    if (!u) router.push("/login");
    else setUser(u);
  }, [router]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, busy]);

  async function enviar() {
    const msg = texto.trim();
    if (!msg || busy) return;
    const nuevos = [...turns, ["user", msg]];
    setTurns(nuevos);
    setTexto("");
    setOfrecer(false);
    setBusy(true);
    try {
      const r = await api(`/api/usuarios/${user.id_usuario}/archive/mensaje`, { method: "POST", body: { turns: nuevos } });
      setTurns([...nuevos, ["archive", r.respuesta]]);
      setOfrecer(r.ofrecer_ficha);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function generarFicha() {
    setBusy(true);
    try {
      const ficha = await api(`/api/usuarios/${user.id_usuario}/archive/ficha`, { method: "POST", body: { turns } });
      localStorage.setItem("climb_ficha", JSON.stringify({ ...ficha, _recien_generado: true }));
      router.push("/archive/ficha");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/archive">← Back to the archive</Link>
      <h1 style={{ marginTop: 16 }}>Archive</h1>
      <div style={{ margin: "16px 0" }}>
        {turns.map(([who, text], i) => (
          <div key={i} style={{ margin: "12px 0" }}>
            <div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{who === "user" ? "You" : "Archive"}</div>
            <div>{text}</div>
          </div>
        ))}
        {busy && <p className="muted">Archive is typing…</p>}
        <div ref={endRef} />
      </div>

      {error && <p className="error">{error}</p>}

      {ofrecer ? (
        <div className="row">
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={generarFicha}>Yes, generate the entry</button>
          <button className="link" onClick={() => setOfrecer(false)}>I want to change something</button>
        </div>
      ) : (
        <div className="row">
          <input value={texto} onChange={(e) => setTexto(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && enviar()}
                 placeholder="Write whatever you want to share..." />
          <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={enviar}>Send</button>
        </div>
      )}
    </main>
  );
}
