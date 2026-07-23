"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setUsuario } from "../../lib/api";

export default function Login() {
  const router = useRouter();
  const [form, setForm] = useState({ identificador: "", clave: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const u = await api("/api/auth/login", { method: "POST", body: form });
      setUsuario(u);
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Sign in</h1>
      <p className="sub">Sign in with your email or your username.</p>
      <form onSubmit={submit}>
        <label>Email or username</label>
        <input value={form.identificador} onChange={upd("identificador")} placeholder="you@email.com or username" />
        <label>Password</label>
        <input type="password" value={form.clave} onChange={upd("clave")} placeholder="••••••••" />
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
      <p className="muted" style={{ marginTop: 20 }}>
        Don&apos;t have an account? <Link className="link" href="/register">Create one</Link>
      </p>
    </main>
  );
}
