"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../lib/api";

export default function Pacer() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [estado, setEstado] = useState(null); // {id_mision, mision, progreso}
  const [sinMision, setSinMision] = useState(false);
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
        setEstado(await api(`/api/usuarios/${u.id_usuario}/mision`));
      } catch {
        setSinMision(true);
      }
    })();
  }, [router]);

  async function toggle(i) {
    const progreso = estado.progreso.slice();
    progreso[i] = !progreso[i];
    setEstado({ ...estado, progreso });
    try {
      await api(`/api/misiones/${estado.id_mision}/progreso`, { method: "PATCH", body: { progreso } });
    } catch (err) {
      setError(err.message);
    }
  }

  async function generar() {
    setBusy(true);
    setError("");
    try {
      await api(`/api/usuarios/${user.id_usuario}/mision`, { method: "POST" });
      setSinMision(false);
      setEstado(await api(`/api/usuarios/${user.id_usuario}/mision`));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function completar() {
    setBusy(true);
    try {
      await api(`/api/misiones/${estado.id_mision}/completar`, { method: "POST" });
      router.push("/pacer/completada");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (!user) return null;

  if (sinMision) {
    return (
      <main>
        <Link className="link" href="/dashboard">← Back to dashboard</Link>
        <h1 style={{ marginTop: 16 }}>Pacer · Your week</h1>
        <p className="sub">You don&apos;t have an active mission.</p>
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy} onClick={generar}>
          {busy ? "Generating…" : "Generate my mission"}
        </button>
      </main>
    );
  }
  if (!estado) return <main><p className="muted">Loading your mission…</p></main>;

  const m = estado.mision;
  const total = (m.acciones || []).length;
  const hechas = estado.progreso.filter(Boolean).length;
  const allDone = total > 0 && hechas === total;

  return (
    <main>
      <Link className="link" href="/dashboard">← Back to dashboard</Link>
      <h2 style={{ marginTop: 16 }}>Pacer · {hechas} of {total} actions</h2>
      <h1>{m.nombre_mision}</h1>
      <p className="sub">{m.descripcion}</p>

      <div className="card">
        {(m.acciones || []).map((a, i) => (
          <label key={i} style={{ display: "flex", gap: 10, margin: "10px 0", color: "var(--navy)", cursor: "pointer" }}>
            <input type="checkbox" checked={!!estado.progreso[i]} onChange={() => toggle(i)} style={{ width: "auto" }} />
            <span style={{ textDecoration: estado.progreso[i] ? "line-through" : "none" }}>{a}</span>
          </label>
        ))}
      </div>

      {m.conexion_camino && (
        <div className="card" style={{ background: "var(--navy)", color: "var(--offwhite)" }}>
          <strong>Connection with your path</strong>
          <p style={{ margin: "6px 0 0" }}>{m.conexion_camino}</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {allDone && (
        <button className="btn" disabled={busy} onClick={completar}>
          {busy ? "Closing…" : "Complete mission →"}
        </button>
      )}
    </main>
  );
}
