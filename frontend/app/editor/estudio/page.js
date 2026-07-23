"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, getUsuario } from "../../../lib/api";

const FORMATOS = [
  ["correo", "Email"],
  ["linkedin", "LinkedIn post"],
];

export default function EditorEstudio() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [idBorrador, setIdBorrador] = useState(null);
  const [formato, setFormato] = useState("");
  const [borrador, setBorrador] = useState("");
  const [asunto, setAsunto] = useState("");
  const [esCorreo, setEsCorreo] = useState(false);
  const [turns, setTurns] = useState([]);
  const [sugerencias, setSugerencias] = useState([]);
  const [texto, setTexto] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);
    const id = new URLSearchParams(window.location.search).get("id");
    if (id) {
      (async () => {
        try {
          const b = await api(`/api/editor/borradores/${id}`);
          setIdBorrador(b.id_borrador);
          setFormato(b.formato || "");
          setBorrador(b.borrador || "");
          setAsunto(b.asunto || "");
          setEsCorreo(b.es_correo);
          try { setTurns(JSON.parse(b.turns_json) || []); } catch { setTurns([]); }
        } catch (err) {
          setError(err.message);
        }
      })();
    }
  }, [router]);

  async function enviar(instruccion) {
    const msg = (instruccion ?? texto).trim();
    if (!msg || busy || !formato) return;
    const nuevos = [...turns, ["user", msg]];
    setTurns(nuevos);
    setTexto("");
    setBusy(true);
    setError("");
    try {
      const r = await api(`/api/usuarios/${user.id_usuario}/editor/estudio`, {
        method: "POST",
        body: { id_borrador: idBorrador, formato, borrador_actual: borrador, turns: nuevos },
      });
      setIdBorrador(r.id_borrador);
      setBorrador(r.borrador);
      setAsunto(r.asunto);
      setEsCorreo(r.es_correo);
      setSugerencias(r.sugerencias || []);
      setTurns(r.turns || nuevos);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function completar() {
    if (!idBorrador) return;
    try {
      await api(`/api/editor/borradores/${idBorrador}/completar`, { method: "POST" });
      router.push("/editor");
    } catch (err) {
      setError(err.message);
    }
  }

  if (!user) return null;

  return (
    <main style={{ maxWidth: 720 }}>
      <Link className="link" href="/editor">← Back to Editor</Link>
      <h1 style={{ marginTop: 16 }}>Editor studio</h1>

      {!formato ? (
        <>
          <p className="sub">What do you want to write? Pick a format to start.</p>
          <div className="row">
            {FORMATOS.map(([f, label]) => (
              <button key={f} className="btn" style={{ marginTop: 0 }} onClick={() => setFormato(f)}>{label}</button>
            ))}
          </div>
        </>
      ) : (
        <>
          {/* Preview del borrador */}
          <div className="card" style={{ whiteSpace: "pre-wrap" }}>
            {esCorreo && asunto && <div style={{ fontWeight: 700, marginBottom: 8 }}>Subject: {asunto}</div>}
            {borrador || <span className="muted">Your draft will appear here.</span>}
          </div>

          {sugerencias.length > 0 && (
            <div className="row" style={{ flexWrap: "wrap" }}>
              {sugerencias.map((s, i) => (
                <button key={i} className="link" onClick={() => enviar(s)} disabled={busy}
                        style={{ border: "1px solid var(--border)", borderRadius: 16, padding: "6px 12px", background: "#fff", cursor: "pointer" }}>
                  {s}
                </button>
              ))}
            </div>
          )}

          {error && <p className="error">{error}</p>}
          {busy && <p className="muted">Editor is writing…</p>}

          <div className="row">
            <input value={texto} onChange={(e) => setTexto(e.target.value)}
                   onKeyDown={(e) => e.key === "Enter" && enviar()}
                   placeholder="Tell Editor what to write or tweak..." />
            <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={() => enviar()}>Send</button>
          </div>

          {idBorrador && (
            <button className="link" onClick={completar} style={{ background: "none", border: "none", cursor: "pointer", marginTop: 16 }}>
              ✓ Complete draft
            </button>
          )}
        </>
      )}
    </main>
  );
}
