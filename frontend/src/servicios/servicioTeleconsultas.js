import axios from "axios";
import { URLS_SERVICIOS } from "./configuracionFrontend";

const apiTeleconsulta = axios.create({
  baseURL: `${URLS_SERVICIOS.teleconsulta}/api/teleconsultas`,
  headers: { "Content-Type": "application/json" },
  timeout: 12000,
});

apiTeleconsulta.interceptors.request.use((config) => {
  const token = localStorage.getItem("psicoconecta_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiTeleconsulta.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem("psicoconecta_token")) {
      localStorage.removeItem("psicoconecta_token");
      window.dispatchEvent(new Event("psicoconecta:sesion-expirada"));
    }
    return Promise.reject(error);
  },
);

export const teleconsultasApi = {
  misSesiones: () => apiTeleconsulta.get("/mis-sesiones"),
  obtenerPorCita: (citaId) => apiTeleconsulta.get(`/cita/${citaId}`),
  obtenerAcceso: (citaId) => apiTeleconsulta.post(`/cita/${citaId}/acceso`),
};

export const mensajeErrorTeleconsulta = (error, defecto) =>
  error?.response?.data?.mensaje || error?.response?.data?.message || defecto;
