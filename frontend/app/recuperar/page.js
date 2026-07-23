"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "../../lib/api";

export default function Recuperar() {
  const router = useRouter();
  const [fase, setFase] = useState("correo"); // 'correo' | 'codigo'
  const [correo, setCorreo] = useState("");
  const [codigo, setCodigo] = useState("");
  const [clave, setClave] = useState("");
  const [clave2, setClave2] = useState("");
  const [info, setInfo] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function enviar() {
    if (!correo.trim() || busy) return;
    setBusy(true); setError(""); setInfo("");
    try {
      await api("/api/auth/recuperar", { method: "POST", body: { correo } });
      setInfo("If an account exists for that email, we sent a code. Check your inbox.");
      setFase("codigo");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function restablecer() {
    if (busy) return;
    if (clave.length < 4) return setError("Your password must be at least 4 characters.");
    if (clave !== clave2) return setError("Passwords don't match.");
    setBusy(true); setError("");
    try {
      await api("/api/auth/restablecer", { method: "POST", body: { correo, codigo, nueva_clave: clave } });
      router.push("/login");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Reset your password</h1>
      {fase === "correo" ? (
        <>
          <p className="sub">Enter your email and we&apos;ll send you a code.</p>
          <label>Email</label>
          <input value={correo} onChange={(e) => setCorreo(e.target.value)} placeholder="you@email.com" />
          {error && <p className="error">{error}</p>}
          <button className="btn" disabled={busy} onClick={enviar}>{busy ? "Sending…" : "Send code"}</button>
        </>
      ) : (
        <>
          {info && <p className="muted">{info}</p>}
          <label>Code</label>
          <input value={codigo} onChange={(e) => setCodigo(e.target.value)} placeholder="123456" />
          <label>New password</label>
          <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} placeholder="At least 4 characters" />
          <label>Confirm new password</label>
          <input type="password" value={clave2} onChange={(e) => setClave2(e.target.value)} placeholder="Repeat your password" />
          {error && <p className="error">{error}</p>}
          <button className="btn" disabled={busy} onClick={restablecer}>{busy ? "Resetting…" : "Reset password"}</button>
          <p className="muted" style={{ marginTop: 12 }}>
            <button className="link" onClick={enviar} style={{ background: "none", border: "none", cursor: "pointer" }}>Didn&apos;t get it? Send again</button>
          </p>
        </>
      )}
      <p className="muted" style={{ marginTop: 20 }}>
        <Link className="link" href="/login">Back to sign in</Link>
      </p>
    </main>
  );
}
