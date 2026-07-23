"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setUsuario } from "../../lib/api";

export default function Register() {
  const router = useRouter();
  const [form, setForm] = useState({ nombre: "", correo: "", username: "", clave: "", idioma: "en" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await api("/api/auth/registro", { method: "POST", body: form });
      setUsuario({ id_usuario: r.id_usuario, username: r.username, nombre: form.nombre, idioma: form.idioma });
      router.push("/onboarding");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Create your account</h1>
      <p className="sub">Your name is how Climb greets you. Your username and email are how you sign back in.</p>
      <form onSubmit={submit}>
        <label>Your name</label>
        <input value={form.nombre} onChange={upd("nombre")} placeholder="Alex Carter" />
        <label>Email</label>
        <input value={form.correo} onChange={upd("correo")} placeholder="you@email.com" />
        <label>Username</label>
        <input value={form.username} onChange={upd("username")} placeholder="alexcarter" />
        <label>Password</label>
        <input type="password" value={form.clave} onChange={upd("clave")} placeholder="At least 4 characters" />
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? "Creating…" : "Create account"}</button>
      </form>
      <p className="muted" style={{ marginTop: 20 }}>
        Already have an account? <Link className="link" href="/login">Sign in</Link>
      </p>
    </main>
  );
}
