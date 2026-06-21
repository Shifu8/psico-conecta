import posthog from "posthog-js";
import { POSTHOG_HOST, POSTHOG_KEY } from "./configuracionFrontend";

let inicializada = false;

export const iniciarAnalitica = () => {
  if (!POSTHOG_KEY || inicializada) return false;
  posthog.init(POSTHOG_KEY, {
    api_host: POSTHOG_HOST,
    autocapture: true,
    capture_pageview: true,
    person_profiles: "identified_only",
    debug: import.meta.env.DEV,
  });
  inicializada = true;
  return true;
};

export const analiticaActiva = () => inicializada;

export const identificarUsuario = (usuario) => {
  if (!inicializada || !usuario?.id) return;
  posthog.identify(`usuario_${usuario.id}`, {
    rol: usuario.role,
    estado: usuario.status,
  });
};

export const capturarEvento = (nombre, propiedades = {}) => {
  if (!inicializada) return;
  posthog.capture(nombre, {
    app: "psicoconecta",
    ...propiedades,
  });
};

export const resetearAnalitica = () => {
  if (!inicializada) return;
  posthog.reset();
};
