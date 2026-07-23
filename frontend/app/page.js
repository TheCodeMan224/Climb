"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { t, getLang, setLang } from "../lib/i18n";

export default function Home() {
  const [lang, setLangState] = useState("en");
  useEffect(() => setLangState(getLang()), []);
  const tr = (k) => t(k, lang);

  function cambiar(l) {
    setLang(l);
    setLangState(l);
  }

  return (
    <main className="center">
      <div style={{ position: "absolute", top: 18, right: 20, display: "flex", gap: 6 }}>
        {["en", "es"].map((l) => (
          <button key={l} onClick={() => cambiar(l)}
            style={{ fontFamily: "var(--dm)", fontWeight: 600, fontSize: 12,
                     background: lang === l ? "var(--navy)" : "transparent",
                     color: lang === l ? "var(--offwhite)" : "var(--muted)",
                     border: "1px solid var(--border)", borderRadius: 14, padding: "5px 11px", cursor: "pointer" }}>
            {l.toUpperCase()}
          </button>
        ))}
      </div>

      <h1 className="logo">Climb</h1>
      <p className="tag">{tr("tagline")}</p>
      <div className="row">
        <Link className="btn" href="/register" style={{ marginTop: 0 }}>{tr("get_started")}</Link>
        <Link className="link" href="/login">{tr("have_account")}</Link>
      </div>
      <p className="muted" style={{ marginTop: 40, fontFamily: "var(--dm)", letterSpacing: "0.08em", fontSize: 11 }}>{tr("keywords")}</p>
    </main>
  );
}
