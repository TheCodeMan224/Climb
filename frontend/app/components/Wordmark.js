import Link from "next/link";

// Marca Climb: montaña (navy) con la cima en oro + wordmark en Syne.
export default function Wordmark({ href = "/dashboard", size = 22 }) {
  const mark = (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 11 }}>
      <svg viewBox="0 0 26 26" width={size} height={size} fill="none" aria-hidden>
        <path d="M2 24 L13 3 L24 24" stroke="var(--navy)" strokeWidth="2.2" strokeLinejoin="round" />
        <path d="M9.5 13 L13 3 L16.5 13" stroke="var(--gold)" strokeWidth="2.2" strokeLinejoin="round" />
      </svg>
      <span style={{ fontFamily: "var(--syne)", fontWeight: 700, fontSize: size * 0.77, letterSpacing: "-0.01em", color: "var(--navy)" }}>Climb</span>
    </span>
  );
  return href ? (
    <Link href={href} style={{ textDecoration: "none" }}>{mark}</Link>
  ) : mark;
}
