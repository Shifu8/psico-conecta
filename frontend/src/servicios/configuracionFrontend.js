const API_PRODUCCION_PREDETERMINADA = "https://d1wkhs3cq8vcom.cloudfront.net";
const GOOGLE_CLIENT_ID_PRODUCCION =
  "339658076678-kah0e205d5asf6ufnlh009lh5i4g8u70.apps.googleusercontent.com";
const TURNSTILE_SITE_KEY_PRODUCCION = "0x4AAAAAADeaQizjXYRnGG6E";
const POSTHOG_KEY_PRODUCCION = "phc_yr69k3vnBrjCGETfFnGvw2j3XWMQSggpXzoXsoFRYtYf";

const valorEntorno = (nombre) => import.meta.env[nombre]?.trim();
const captchaDesactivado = valorEntorno("VITE_CAPTCHA_DESACTIVADO") === "true";
const urlServicioLocal = (puerto) => `http://127.0.0.1:${puerto}`;

const API_PUBLICA =
  valorEntorno("VITE_GATEWAY_API_URL") ||
  valorEntorno("VITE_API_URL") ||
  (import.meta.env.PROD ? API_PRODUCCION_PREDETERMINADA : "");

const urlServicio = (variable, puerto) =>
  valorEntorno(variable) || (import.meta.env.PROD ? API_PUBLICA : urlServicioLocal(puerto));

export const API_BASE_URL =
  valorEntorno("VITE_USERS_API_URL") ||
  API_PUBLICA ||
  urlServicioLocal(5001);

export const URLS_SERVICIOS = {
  usuarios: API_BASE_URL,
  citas: urlServicio("VITE_CITAS_API_URL", 5002),
  teleconsulta: urlServicio("VITE_TELECONSULTA_API_URL", 5003),
  pagos: urlServicio("VITE_PAGOS_API_URL", 5004),
  iot: urlServicio("VITE_IOT_API_URL", 5005),
  gateway: API_PUBLICA || urlServicioLocal(5000),
};

export const GOOGLE_CLIENT_ID =
  valorEntorno("VITE_GOOGLE_CLIENT_ID") ||
  (import.meta.env.PROD ? GOOGLE_CLIENT_ID_PRODUCCION : "");

const esLocalOWorker = typeof window !== "undefined" && (
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname.endsWith("cloudfront.net") ||
  window.location.hostname.endsWith("amazonaws.com")
);

export const TURNSTILE_SITE_KEY = (captchaDesactivado || esLocalOWorker)
  ? ""
  : valorEntorno("VITE_TURNSTILE_SITE_KEY") ||
    (import.meta.env.PROD ? TURNSTILE_SITE_KEY_PRODUCCION : "");

export const POSTHOG_KEY =
  valorEntorno("VITE_POSTHOG_KEY") ||
  (import.meta.env.PROD ? POSTHOG_KEY_PRODUCCION : "");
export const POSTHOG_HOST = valorEntorno("VITE_POSTHOG_HOST") || "https://us.i.posthog.com";
