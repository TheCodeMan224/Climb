"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "../../lib/api";
import { t, getLang } from "../../lib/i18n";

export default function Recuperar() {
  const router = useRouter();
  const [fase, setFase] = useState("correo");
  const [correo, setCorreo] = useState("");
  const [codigo, setCodigo] = useState("");
  const [clave, setClave] = useState("");
  const [clave2, setClave2] = useState("");
  const [info, setInfo] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [lang, setLangState] = useState("en");

  useEffect(() => setLangState(getLang()), []);
  const tr = (k) => t(k, lang);

  async function enviar() {
    if (!correo.trim() || busy) return;
    setBusy(true); setError(""); setInfo("");
    try {
      await api("/api/auth/recuperar", { method: "POST", body: { correo } });
      setInfo(tr("reset_sent"));
      setFase("codigo");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function restablecer() {
    if (busy) return;
    if (clave.length < 4) return setError(tr("password_short"));
    if (clave !== clave2) return setError(tr("passwords_no_match"));
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
      <h1>{tr("reset_title")}</h1>
      {fase === "correo" ? (
        <>
          <p className="sub">{tr("reset_sub")}</p>
          <label>{tr("email")}</label>
          <input value={correo} onChange={(e) => setCorreo(e.target.value)} placeholder="you@email.com" />
          {error && <p className="error">{error}</p>}
          <button className="btn" disabled={busy} onClick={enviar}>{busy ? tr("sending") : tr("send_code")}</button>
        </>
      ) : (
        <>
          {info && <p className="muted">{info}</p>}
          <label>{tr("code")}</label>
          <input value={codigo} onChange={(e) => setCodigo(e.target.value)} placeholder="123456" />
          <label>{tr("new_password")}</label>
          <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} placeholder={tr("at_least_4")} />
          <label>{tr("confirm_password")}</label>
          <input type="password" value={clave2} onChange={(e) => setClave2(e.target.value)} placeholder={tr("at_least_4")} />
          {error && <p className="error">{error}</p>}
          <button className="btn" disabled={busy} onClick={restablecer}>{busy ? tr("resetting") : tr("reset_password")}</button>
          <p className="muted" style={{ marginTop: 12 }}>
            <button className="link" onClick={enviar} style={{ background: "none", border: "none", cursor: "pointer" }}>{tr("resend")}</button>
          </p>
        </>
      )}
      <p className="muted" style={{ marginTop: 20 }}>
        <Link className="link" href="/login">{tr("back_signin")}</Link>
      </p>
    </main>
  );
}
