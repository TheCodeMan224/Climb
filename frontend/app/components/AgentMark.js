// Marcas geométricas de los agentes (Design System): un anillo navy con un
// trazo simple dentro. Mismos dibujos que el documento de diseño.
const INNER = {
  Scout: '<circle cx="24" cy="24" r="9" stroke="#0A1F3D" stroke-width="1.8"/><path d="M31 31 L37 37" stroke="#0A1F3D" stroke-width="2" stroke-linecap="round"/>',
  Pacer: '<path d="M17 34 L17 27 M24 34 L24 22 M31 34 L31 17 M38 34 L38 24" stroke="#0A1F3D" stroke-width="2" stroke-linecap="round"/>',
  Mirror: '<path d="M28 15 C21 15 18 24 18 24 C18 24 21 33 28 33" stroke="#0A1F3D" stroke-width="1.8" fill="none"/><path d="M28 15 C35 15 38 24 38 24 C38 24 35 33 28 33" stroke="#0A1F3D" stroke-width="1.8" fill="none"/>',
  Archive: '<rect x="17" y="18" width="22" height="6" rx="1.4" stroke="#0A1F3D" stroke-width="1.8"/><rect x="17" y="26" width="22" height="6" rx="1.4" stroke="#0A1F3D" stroke-width="1.8"/><path d="M25 21 L31 21" stroke="#0A1F3D" stroke-width="1.8" stroke-linecap="round"/>',
  Editor: '<path d="M20 20 L20 36 M20 20 L30 20 M20 28 L27 28 M20 36 L30 36" stroke="#0A1F3D" stroke-width="1.8" stroke-linecap="round"/><path d="M34 20 L38 24 L30 32 L26 32 L26 28 Z" stroke="#0A1F3D" stroke-width="1.8" stroke-linejoin="round"/>',
  Clarity: '<path d="M28 15 L38 28 L28 41 L18 28 Z" stroke="#0A1F3D" stroke-width="1.8" stroke-linejoin="round"/><path d="M28 15 L28 41" stroke="#0A1F3D" stroke-width="1.6"/>',
};

export default function AgentMark({ name, size = 48 }) {
  return (
    <span style={{ width: size, height: size, borderRadius: "50%", border: "1.5px solid var(--navy)", display: "inline-flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      <svg viewBox="0 0 56 56" width={Math.round(size * 0.83)} height={Math.round(size * 0.83)} fill="none"
           dangerouslySetInnerHTML={{ __html: INNER[name] || "" }} />
    </span>
  );
}
