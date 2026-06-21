import posthog from "posthog-js";
import { POSTHOG_HOST, POSTHOG_KEY } from "./configuracionFrontend";

let inicializada = false;
let distinctIdActual = null;

const ANALITICA_ID_KEY = "psicoconecta_analitica_id";
const POSTHOG_PROXY_PATH = "/posthog";

const crearIdentificador = () => {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const obtenerDistinctId = () => {
  if (distinctIdActual) return distinctIdActual;
  const guardado = localStorage.getItem(ANALITICA_ID_KEY);
  if (guardado) {
    distinctIdActual = guardado;
    return distinctIdActual;
  }
  distinctIdActual = `anonimo_${crearIdentificador()}`;
  localStorage.setItem(ANALITICA_ID_KEY, distinctIdActual);
  return distinctIdActual;
};

const usarProxyPostHog = () =>
  import.meta.env.PROD &&
  typeof window !== "undefined" &&
  window.location.hostname.endsWith("workers.dev");

const hostPostHog = () =>
  usarProxyPostHog()
    ? `${window.location.origin}${POSTHOG_PROXY_PATH}`
    : POSTHOG_HOST.replace(/\/$/, "");

const endpointPostHog = () => `${hostPostHog()}/capture/`;

const enviarEventoDirecto = (nombre, propiedades) => {
  if (!POSTHOG_KEY) return;
  const payload = JSON.stringify({
    token: POSTHOG_KEY,
    event: nombre,
    distinct_id: obtenerDistinctId(),
    properties: propiedades,
  });
  const url = endpointPostHog();

  if (navigator.sendBeacon) {
    const enviado = navigator.sendBeacon(
      url,
      new Blob([payload], { type: "application/json" }),
    );
    if (enviado) return;
  }

  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload,
    keepalive: true,
    mode: "cors",
  }).catch(() => {});
};

const propiedadesBase = (propiedades = {}) => ({
  app: "psicoconecta",
  $lib: "web",
  $current_url: window.location.href,
  $host: window.location.host,
  $pathname: window.location.pathname,
  $referrer: document.referrer,
  $screen_width: window.screen.width,
  $screen_height: window.screen.height,
  $insert_id: `psicoconecta_${crearIdentificador()}`,
  ...propiedades,
});

export const iniciarAnalitica = () => {
  if (!POSTHOG_KEY || inicializada) return false;
  posthog.init(POSTHOG_KEY, {
    api_host: hostPostHog(),
    autocapture: true,
    capture_pageview: false,
    person_profiles: "identified_only",
    debug: import.meta.env.DEV,
  });
  inicializada = true;
  return true;
};

export const analiticaActiva = () => inicializada;

export const identificarUsuario = (usuario) => {
  if (!usuario?.id) return;
  distinctIdActual = `usuario_${usuario.id}`;
  localStorage.setItem(ANALITICA_ID_KEY, distinctIdActual);
  if (!inicializada) return;
  posthog.identify(`usuario_${usuario.id}`, {
    rol: usuario.role,
    estado: usuario.status,
  });
};

export const capturarEvento = (nombre, propiedades = {}) => {
  const propiedadesEvento = propiedadesBase(propiedades);
  if (inicializada) {
    posthog.capture(nombre, propiedadesEvento);
  }
  enviarEventoDirecto(nombre, propiedadesEvento);
};

export const capturarVistaPagina = () => {
  const propiedadesEvento = propiedadesBase({
    $current_url: window.location.href,
    path: window.location.pathname,
  });
  if (inicializada) {
    posthog.capture("$pageview", propiedadesEvento);
  }
  enviarEventoDirecto("$pageview", propiedadesEvento);
};

export const resetearAnalitica = () => {
  if (!inicializada) return;
  posthog.reset();
};
