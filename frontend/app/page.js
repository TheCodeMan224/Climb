"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import Wordmark from "./components/Wordmark";
import { t, getLang, setLang } from "../lib/i18n";

export default function Home() {
  const [lang, setLangState] = useState("en");
  useEffect(() => setLangState(getLang()), []);
  const tr = (k) => t(k, lang);

  function cambiar(l) {
    setLang(l);
    setLangState(l);
  }

  const promesa = tr("keywords").split("·").map((s) => s.trim());

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", padding: "clamp(28px,4vw,40px) clamp(24px,5vw,48px)" }}>
      {/* top bar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Wordmark href={null} />
        <div style={{ display: "flex", gap: 6 }}>
          {["en", "es"].map((l) => (
            <button key={l} onClick={() => cambiar(l)}
              style={{ fontFamily: "var(--inter)", fontWeight: 600, fontSize: 12,
                       background: lang === l ? "var(--navy)" : "transparent",
                       color: lang === l ? "var(--offwhite)" : "var(--muted)",
                       border: "1px solid var(--border)", borderRadius: 14, padding: "5px 12px", cursor: "pointer" }}>
              {l.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* center hero */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "40px 0" }}>
        <Wordmark href={null} height={104} />
        <p className="tag" style={{ marginTop: 32 }}>{tr("tagline")}</p>
        <Link className="btn" href="/register" style={{ marginTop: 0, padding: "17px 40px", fontSize: 16 }}>{tr("get_started")}</Link>
        <div style={{ marginTop: 28, fontSize: 15, color: "var(--muted)" }}>
          {tr("have_account")} — <Link className="link" href="/login">{tr("sign_in")}</Link>
        </div>
      </div>

      {/* bottom promise */}
      <div style={{ display: "flex", justifyContent: "center", paddingTop: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, fontFamily: "var(--inter)", fontSize: 13, fontWeight: 600, letterSpacing: "0.28em", textTransform: "uppercase", color: "var(--navy)", flexWrap: "wrap", justifyContent: "center" }}>
          {promesa.map((p, i) => (
            <span key={i} style={{ display: "flex", alignItems: "center", gap: 20 }}>
              {i > 0 && <span style={{ width: 5, height: 5, borderRadius: "50%", background: "var(--gold)" }} />}
              <span>{p}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
