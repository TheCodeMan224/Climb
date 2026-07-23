"use client";
import { useEffect, useRef, useState } from "react";
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
  const [contexto, setContexto] = useState("");
  const [contextoTitulo, setContextoTitulo] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const chatRef = useRef(null);

  useEffect(() => {
    const u = getUsuario();
    if (!u) {
      router.push("/login");
      return;
    }
    setUser(u);

    // Contexto que llega desde Archive (un logro para redactar).
    try {
      const ctx = JSON.parse(localStorage.getItem("climb_editor_contexto"));
      if (ctx) {
        setContexto(ctx.texto || "");
        setContextoTitulo(ctx.titulo || "");
        localStorage.removeItem("climb_editor_contexto");
      }
    } catch { /* sin contexto */ }

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

  useEffect(() => { chatRef.current?.scrollTo(0, chatRef.current.scrollHeight); }, [turns, busy]);

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
        body: { id_borrador: idBorrador, formato, contexto, borrador_actual: borrador, turns: nuevos },
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

  // --- Selección de formato (antes de abrir el estudio) ---
  if (!formato) {
    return (
      <main>
        <Link className="link" href="/editor">← Back to Editor</Link>
        <h1 style={{ marginTop: 16 }}>Editor studio</h1>
        {contextoTitulo && <p className="muted">Writing about: <strong>{contextoTitulo}</strong></p>}
        <p className="sub">What do you want to write? Pick a format to start.</p>
        <div className="row">
          {FORMATOS.map(([f, label]) => (
            <button key={f} className="btn" style={{ marginTop: 0 }} onClick={() => setFormato(f)}>{label}</button>
          ))}
        </div>
      </main>
    );
  }

  // --- Estudio de 2 paneles ---
  return (
    <main style={{ maxWidth: 1080 }}>
      <div className="row" style={{ justifyContent: "space-between", marginTop: 0 }}>
        <Link className="link" href="/editor">← Back to Editor</Link>
        {idBorrador && <button className="link" onClick={completar} style={{ background: "none", border: "none", cursor: "pointer" }}>✓ Complete</button>}
      </div>
      {contextoTitulo && <p className="muted" style={{ marginTop: 8 }}>Based on · <strong>{contextoTitulo}</strong></p>}

      <div style={{ display: "flex", gap: 20, marginTop: 16, alignItems: "stretch", minHeight: "68vh" }}>
        {/* IZQUIERDA: previsualización grande */}
        <div className="card" style={{ flex: 1.5, overflow: "auto", whiteSpace: "pre-wrap", margin: 0 }}>
          {esCorreo && asunto && (
            <div style={{ fontFamily: "var(--dm)", fontWeight: 600, marginBottom: 10, paddingBottom: 10, borderBottom: "1px solid var(--border)" }}>
              Subject: {asunto}
            </div>
          )}
          {borrador || <span className="muted">Your draft will appear here.</span>}
        </div>

        {/* DERECHA: arriba chat, abajo sugerencias */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 12, minWidth: 300 }}>
          {/* Chat (arriba) */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", border: "1px solid var(--border)", borderRadius: 14, background: "var(--surface)", overflow: "hidden" }}>
            <div ref={chatRef} style={{ flex: 1, overflow: "auto", padding: "14px 16px" }}>
              {turns.length === 0 && <p className="muted">Tell Editor what to write.</p>}
              {turns.map(([who, t], i) => (
                <div key={i} style={{ margin: "10px 0" }}>
                  <div className="muted" style={{ fontSize: 11, textTransform: "uppercase", fontFamily: "var(--dm)" }}>{who === "user" ? "You" : "Editor"}</div>
                  <div>{t}</div>
                </div>
              ))}
              {busy && <p className="muted">Editor is writing…</p>}
            </div>
            <div style={{ display: "flex", gap: 8, padding: 10, borderTop: "1px solid var(--border)" }}>
              <input value={texto} onChange={(e) => setTexto(e.target.value)}
                     onKeyDown={(e) => e.key === "Enter" && enviar()}
                     placeholder="Ask Editor to write or tweak..." style={{ margin: 0 }} />
              <button className="btn" style={{ marginTop: 0 }} disabled={busy} onClick={() => enviar()}>Send</button>
            </div>
          </div>

          {/* Sugerencias (abajo) */}
          <div className="card" style={{ margin: 0 }}>
            <div className="muted" style={{ fontSize: 11, textTransform: "uppercase", fontFamily: "var(--dm)", marginBottom: 8 }}>Suggestions</div>
            {sugerencias.length === 0 ? (
              <p className="muted" style={{ margin: 0 }}>Editor&apos;s tweak ideas will show here.</p>
            ) : (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {sugerencias.map((s, i) => (
                  <button key={i} onClick={() => enviar(s)} disabled={busy}
                          style={{ border: "1px solid var(--border)", borderRadius: 16, padding: "6px 12px", background: "#fff", cursor: "pointer", fontFamily: "var(--inter)", fontSize: 13, color: "var(--navy)" }}>
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
    </main>
  );
}
