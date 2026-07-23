// i18n mínimo del frontend. El idioma sale del usuario logueado (climb_user.idioma)
// o, antes de tener cuenta, de climb_lang (toggle en la landing). Default: inglés.

export function getLang() {
  if (typeof window === "undefined") return "en";
  try {
    const u = JSON.parse(localStorage.getItem("climb_user"));
    if (u && (u.idioma === "es" || u.idioma === "en")) return u.idioma;
  } catch {
    /* ignore */
  }
  return localStorage.getItem("climb_lang") === "es" ? "es" : "en";
}

export function setLang(l) {
  if (typeof window !== "undefined") localStorage.setItem("climb_lang", l);
}

const T = {
  en: {
    // landing
    tagline: "Your career's right hand",
    get_started: "Get started",
    have_account: "I already have an account",
    keywords: "CONTEXT  ·  PATTERN  ·  EXECUTION",
    // register
    reg_title: "Create your account",
    reg_sub: "Your name is how Climb greets you. Your username and email are how you sign back in.",
    name: "Your name",
    email: "Email",
    username: "Username",
    password: "Password",
    language: "Language",
    create_account: "Create account",
    already_signin: "Already have an account? Sign in",
    // login
    login_title: "Sign in",
    login_sub: "Sign in with your email or your username.",
    email_or_username: "Email or username",
    your_password: "Your password",
    sign_in: "Sign in",
    forgot: "Forgot your password?",
    no_account: "Don't have an account? Create one",
    signing_in: "Signing in…",
    creating: "Creating…",
    // recuperar
    reset_title: "Reset your password",
    reset_sub: "Enter your email and we'll send you a code.",
    send_code: "Send code",
    sending: "Sending…",
    reset_sent: "If an account exists for that email, we sent a code. Check your inbox.",
    code: "Code",
    new_password: "New password",
    confirm_password: "Confirm new password",
    reset_password: "Reset password",
    resetting: "Resetting…",
    resend: "Didn't get it? Send again",
    back_signin: "Back to sign in",
    at_least_4: "At least 4 characters",
    passwords_no_match: "Passwords don't match.",
    password_short: "Your password must be at least 4 characters.",
  },
  es: {
    tagline: "La mano derecha de tu carrera",
    get_started: "Comenzar",
    have_account: "Ya tengo cuenta",
    keywords: "CONTEXTO  ·  PATRÓN  ·  EJECUCIÓN",
    reg_title: "Crea tu cuenta",
    reg_sub: "Tu nombre es cómo Climb te saluda. Tu usuario y tu correo son cómo vuelves a entrar.",
    name: "Tu nombre",
    email: "Correo",
    username: "Nombre de usuario",
    password: "Contraseña",
    language: "Idioma",
    create_account: "Crear cuenta",
    already_signin: "¿Ya tienes cuenta? Inicia sesión",
    login_title: "Iniciar sesión",
    login_sub: "Inicia sesión con tu correo o tu nombre de usuario.",
    email_or_username: "Correo o nombre de usuario",
    your_password: "Tu contraseña",
    sign_in: "Iniciar sesión",
    forgot: "¿Olvidaste tu contraseña?",
    no_account: "¿No tienes cuenta? Crea una",
    signing_in: "Entrando…",
    creating: "Creando…",
    reset_title: "Restablece tu contraseña",
    reset_sub: "Escribe tu correo y te enviaremos un código.",
    send_code: "Enviar código",
    sending: "Enviando…",
    reset_sent: "Si existe una cuenta con ese correo, te enviamos un código. Revisa tu bandeja.",
    code: "Código",
    new_password: "Nueva contraseña",
    confirm_password: "Confirma la nueva contraseña",
    reset_password: "Restablecer contraseña",
    resetting: "Restableciendo…",
    resend: "¿No llegó? Enviar de nuevo",
    back_signin: "Volver a iniciar sesión",
    at_least_4: "Al menos 4 caracteres",
    passwords_no_match: "Las contraseñas no coinciden.",
    password_short: "Tu contraseña debe tener al menos 4 caracteres.",
  },
};

export function t(key, lang) {
  const l = lang || getLang();
  return (T[l] && T[l][key]) || T.en[key] || key;
}
