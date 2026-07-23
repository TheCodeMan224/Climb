"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getUsuario } from "../../../lib/api";

export default function ClarityPuertas() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [cierre, setCierre] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    let turns = [];
    try { turns = JSON.parse(localStorage.getItem("climb_clarity_turns")) || []; } catch { turns = []; }
    (async () => {
      try {
        setCierre(await api(`/api/usuarios/${u.id_usuario}/clarity/cierre`, { method: "POST", body: { turns } }));
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [router]);

  function puertaMirror() {
    const patron = { id: "clarity:patron", quote: cierre.patron_quote, source: "user", scout_ref: null, sesion: null };
    localStorage.setItem("climb_mirror_patron", JSON.stringify(patron));
    router.push("/mirror/session");
  }

  if (!user) return null;
  if (error) return <main><p className="error">{error}</p></main>;
  if (!cierre) return <main><p className="muted">Closing the conversation…</p></main>;

  const rec = cierre.puerta_recomendada;
  const Puerta = ({ n, tag, titulo, desc, onClick }) => (
    <div className="card" onClick={onClick}
         style={{ cursor: "pointer", borderColor: rec === n ? "var(--amber)" : "var(--border)" }}>
      <div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{tag}{rec === n ? " · Recommended" : ""}</div>
      <strong>{titulo}</strong>
      <p className="muted" style={{ margin: "6px 0 0" }}>{desc}</p>
    </div>
  );

  return (
    <main>
      <h1>What comes next is up to you</h1>
      <p className="pivote">{cierre.sintesis}</p>
      <p className="sub">{cierre.pregunta}</p>

      <Puerta n={1} tag="End the session" titulo="Keep the clarity I got"
              desc="The system saves this conversation. You go back to the dashboard."
              onClick={() => router.push("/dashboard")} />

      {cierre.hay_patron && (
        <Puerta n={2} tag="Work the pattern" titulo="Take this to a session with Mirror"
                desc={`The reflection of "${cierre.patron_quote}" deserves its own session.`}
                onClick={puertaMirror} />
      )}

      {cierre.hay_accion && (
        <Puerta n={3} tag="Add to your mission" titulo="Turn it into a Pacer action"
                desc={`"${cierre.accion_texto}" can become part of your active mission.`}
                onClick={() => router.push("/pacer")} />
      )}

      <button className="link" onClick={() => router.push("/clarity/conversacion")}
              style={{ background: "none", border: "none", cursor: "pointer", marginTop: 16 }}>
        ↻ I want to keep talking
      </button>
    </main>
  );
}
