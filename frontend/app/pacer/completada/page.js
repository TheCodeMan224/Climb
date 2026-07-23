"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";

export default function PacerCompletada() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [sugerencias, setSugerencias] = useState(null);
  const [busy, setBusy] = useState(false);
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
        const r = await api(`/api/usuarios/${u.id_usuario}/misiones/sugerencias`);
        setSugerencias(r.sugerencias || []);
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [router]);

  async function elegir(mision) {
    if (busy) return;
    setBusy(true);
    try {
      await api(`/api/usuarios/${user.id_usuario}/misiones`, { method: "POST", body: { mision } });
      router.push("/pacer");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!user) return null;

  return (
    <main>
      <Link className="link" href="/dashboard">← Back to dashboard</Link>
      <h1 style={{ marginTop: 16 }}>Mission complete</h1>
      <p className="sub">It&apos;s recorded in your path. Here&apos;s what can come next.</p>
      {error && <p className="error">{error}</p>}
      {!sugerencias && !error && <p className="muted">Pacer is thinking through your next steps…</p>}
      {sugerencias && sugerencias.map((s, i) => (
        <div className="card" key={i}>
          <strong>{s.nombre_mision}</strong>
          <p className="muted">{s.descripcion}</p>
          <p className="muted">{(s.acciones || []).length} actions</p>
          <button className="btn" disabled={busy} onClick={() => elegir(s)}>
            {busy ? "Setting up…" : "Choose"}
          </button>
        </div>
      ))}
    </main>
  );
}
