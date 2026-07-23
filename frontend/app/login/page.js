"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setUsuario } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

export default function Login() {
  const router = useRouter();
  const [form, setForm] = useState({ identificador: "", clave: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [lang, setLangState] = useState("en");

  useEffect(() => setLangState(getLang()), []);
  const tr = (k) => t(k, lang);
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
      <h1>{tr("login_title")}</h1>
      <p className="sub">{tr("login_sub")}</p>
      <form onSubmit={submit}>
        <label>{tr("email_or_username")}</label>
        <input value={form.identificador} onChange={upd("identificador")} placeholder="you@email.com" />
        <label>{tr("your_password")}</label>
        <input type="password" value={form.clave} onChange={upd("clave")} placeholder="••••••••" />
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? tr("signing_in") : tr("sign_in")}</button>
      </form>
      <p className="muted" style={{ marginTop: 12 }}>
        <Link className="link" href="/recuperar">{tr("forgot")}</Link>
      </p>
      <p className="muted" style={{ marginTop: 8 }}>
        <Link className="link" href="/register">{tr("no_account")}</Link>
      </p>
    </main>
  );
}
