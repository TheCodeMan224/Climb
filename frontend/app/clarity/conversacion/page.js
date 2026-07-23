"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";

export default function ClarityConversacion() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [turns, setTurns] = useState([]);
  const [texto, setTexto] = useState("");
  const [busy, setBusy] = useState(false);
  const [listo, setListo] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);
  const arrancado = useRef(false);

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    if (arrancado.current) return;
    arrancado.current = true;
    const inicial = localStorage.getItem("climb_clarity_inicial");
    if (inicial) {
      enviar(u, inicial, true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [turns, busy]);

  async function enviar(u, mensaje, primero) {
    const msg = (mensaje ?? texto).trim();
    if (!msg || busy) return;
    const nuevos = [...turns, ["user", msg]];
    setTurns(nuevos);
    setTexto("");
    setBusy(true);
    setError("");
    try {
      const r = await api(`/api/usuarios/${u.id_usuario}/clarity/mensaje`, {
        method: "POST",
        body: { turns: nuevos, primer_turno: !!primero },
      });
      const conRef = r.referencia ? `${r.mensaje}\n\n“${r.referencia.cita}” — ${r.referencia.agente} · ${r.referencia.fecha}` : r.mensaje;
      setTurns([...nuevos, ["clarity", conRef]]);
      setListo(r.listo);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function cerrar() {
    localStorage.setItem("climb_clarity_turns", JSON.stringify(turns));
    router.push("/clarity/puertas");
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/clarity">← Clarity</Link>
      <div style={{ margin: "16px 0" }}>
        {turns.map(([who, text], i) => (
          <div key={i} style={{ margin: "12px 0", whiteSpace: "pre-wrap" }}>
            <div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{who === "user" ? "You" : "Clarity"}</div>
            <div>{text}</div>
          </div>
        ))}
        {busy && <p className="muted">Clarity is thinking…</p>}
        <div ref={endRef} />
      </div>

      {error && <p className="error">{error}</p>}

      <div className="row">
        <input value={texto} onChange={(e) => setTexto(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && enviar(user)}
               placeholder="Keep thinking out loud..." />
        <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={() => enviar(user)}>Send</button>
      </div>

      {(listo || turns.filter((t) => t[0] === "user").length >= 2) && (
        <button className="link" onClick={cerrar} style={{ background: "none", border: "none", cursor: "pointer", marginTop: 16 }}>
          I saw what I needed →
        </button>
      )}
    </main>
  );
}
