// Cliente HTTP mínimo hacia la API de Climb (FastAPI).
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `Error ${res.status}`);
  }
  return data;
}

// Sesión mínima en localStorage (MVP; sin tokens todavía).
export function setUsuario(u) {
  localStorage.setItem("climb_user", JSON.stringify(u));
}
export function getUsuario() {
  try {
    return JSON.parse(localStorage.getItem("climb_user"));
  } catch {
    return null;
  }
}
export function clearUsuario() {
  localStorage.removeItem("climb_user");
}
