import axios from "axios";
import { API_BASE_URL } from "./configuracionFrontend";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((configuracion) => {
  const token = localStorage.getItem("psicoconecta_token");
  if (token) {
    configuracion.headers.Authorization = `Bearer ${token}`;
  }
  return configuracion;
});

api.interceptors.response.use(
  (respuesta) => respuesta,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem("psicoconecta_token")) {
      localStorage.removeItem("psicoconecta_token");
      window.dispatchEvent(new Event("psicoconecta:sesion-expirada"));
    }
    return Promise.reject(error);
  },
);

export default api;
