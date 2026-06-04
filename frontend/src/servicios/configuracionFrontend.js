const API_PRODUCCION = "https://d1wkhs3cq8vcom.cloudfront.net";
const GOOGLE_CLIENT_ID_PRODUCCION =
  "339658076678-kah0e205d5asf6ufnlh009lh5i4g8u70.apps.googleusercontent.com";
const TURNSTILE_SITE_KEY_PRODUCCION = "0x4AAAAAADeaQizjXYRnGG6E";

const valorEntorno = (nombre) => import.meta.env[nombre]?.trim();

export const API_BASE_URL =
  valorEntorno("VITE_API_URL") ||
  valorEntorno("VITE_USERS_API_URL") ||
  (import.meta.env.PROD ? API_PRODUCCION : "http://127.0.0.1:5001");

export const GOOGLE_CLIENT_ID =
  valorEntorno("VITE_GOOGLE_CLIENT_ID") ||
  (import.meta.env.PROD ? GOOGLE_CLIENT_ID_PRODUCCION : "");

export const TURNSTILE_SITE_KEY =
  valorEntorno("VITE_TURNSTILE_SITE_KEY") ||
  (import.meta.env.PROD ? TURNSTILE_SITE_KEY_PRODUCCION : "");
