"use client";
import { useState } from "react";

// Logo Climb: archivo cuadrado 500x500 en /public/climb-logo.png con el
// wordmark centrado y margen blanco arriba/abajo. Lo mostramos dentro de una
// ventana apaisada (RATIO ancho:alto) con object-fit:cover, que recorta ese
// margen vertical y deja solo la banda del wordmark. Si el archivo no existe,
// cae con gracia al wordmark "Climb" en Syne.
//
// Es SOLO marca: no navega (para regresar hay un enlace dorado aparte).
//
// RATIO: sube el número para recortar MÁS blanco (banda más delgada), bájalo
// para mostrar más del logo. Ajústalo si el recorte te clipa las letras.
const RATIO = 2.4;

export default function Wordmark({ height = 30 }) {
  const [err, setErr] = useState(false);

  const content = err ? (
    <span style={{ fontFamily: "var(--syne)", fontWeight: 700, fontSize: height * 0.82, letterSpacing: "-0.02em", color: "var(--navy)" }}>Climb</span>
  ) : (
    <span style={{ display: "inline-block", height, width: height * RATIO, maxWidth: "100%", overflow: "hidden" }}>
      <img src="/climb-logo.png" alt="Climb" onError={() => setErr(true)}
           style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center", display: "block" }} />
    </span>
  );

  return <span style={{ display: "inline-flex", alignItems: "center" }}>{content}</span>;
}
