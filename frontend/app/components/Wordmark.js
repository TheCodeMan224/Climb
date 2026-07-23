"use client";
import { useState } from "react";
import Link from "next/link";

// Logo Climb (imagen en /public/climb-logo.png). Si el archivo aún no existe,
// cae con gracia al wordmark en Syne para no romper el layout.
export default function Wordmark({ href = "/dashboard", height = 30 }) {
  const [err, setErr] = useState(false);

  const content = err ? (
    <span style={{ fontFamily: "var(--syne)", fontWeight: 700, fontSize: height * 0.82, letterSpacing: "-0.02em", color: "var(--navy)" }}>Climb</span>
  ) : (
    <img src="/climb-logo.png" alt="Climb" onError={() => setErr(true)}
         style={{ height, width: "auto", maxWidth: "100%", display: "block" }} />
  );

  return href ? (
    <Link href={href} style={{ display: "inline-flex", alignItems: "center", textDecoration: "none" }}>{content}</Link>
  ) : (
    <span style={{ display: "inline-flex", alignItems: "center" }}>{content}</span>
  );
}
