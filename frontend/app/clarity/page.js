"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";

export default function ClarityEspejo() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [espejo, setEspejo] = useState(null);
  const [texto, setTexto] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    (async () => {
      try {
        setEspejo(await api(`/api/usuarios/${u.id_usuario}/clarity/espejo`));
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [router]);

  function empezar() {
    const t = texto.trim();
    if (!t) return;
    localStorage.setItem("climb_clarity_inicial", t);
    localStorage.removeItem("climb_clarity_turns");
    router.push("/clarity/conversacion");
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/dashboard">← Back to dashboard</Link>
      <h1 style={{ marginTop: 16 }}>This is what you&apos;ve built{espejo?.nombre ? `, ${espejo.nombre}` : ""}</h1>
      {error && <p className="error">{error}</p>}

      {espejo && espejo.bloques.map((b, i) => (
        <div className="card" key={i}>
          <div className="muted" style={{ fontSize: 12, textTransform: "uppercase" }}>{b.numero} · {b.agente}</div>
          <p style={{ margin: "6px 0 0" }}>
            {b.segmentos.map(([t, esDato], j) => (
              <span key={j} style={esDato ? { color: "var(--amber)", fontWeight: 700 } : undefined}>{t}</span>
            ))}
          </p>
          {b.cta_texto && b.cta_ruta && (
            <Link className="link" href={b.cta_ruta} style={{ display: "inline-block", marginTop: 8 }}>{b.cta_texto}</Link>
          )}
        </div>
      ))}

      <h2>Now you</h2>
      <p className="sub">What&apos;s on your mind? Tell me what you want to think through.</p>
      <textarea value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Whatever's on your mind..." />
      <button className="btn" onClick={empezar}>Start →</button>
    </main>
  );
}
