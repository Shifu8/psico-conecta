import axios from "axios";
import { URLS_SERVICIOS } from "./configuracionFrontend";

const cliente = axios.create({
  baseURL: URLS_SERVICIOS.pagos,
  headers: { "Content-Type": "application/json" },
  timeout: 12000,
});

cliente.interceptors.request.use((configuracion) => {
  const token = localStorage.getItem("psicoconecta_token");
  if (token) configuracion.headers.Authorization = `Bearer ${token}`;
  return configuracion;
});

export const mensajeErrorPago = (error, defecto = "No fue posible completar la operación.") =>
  error?.response?.data?.mensaje || error?.response?.data?.message || error?.message || defecto;

export const pagosApi = {
  listarMisPagos: async (estado) => {
    const { data } = await cliente.get("/api/pagos/mis-pagos", {
      params: estado ? { estado } : undefined,
    });
    return Array.isArray(data) ? data : [];
  },

  listarTodos: async (estado) => {
    const { data } = await cliente.get("/api/pagos", {
      params: estado ? { estado } : undefined,
    });
    return Array.isArray(data?.pagos) ? data.pagos : [];
  },

  obtener: async (pagoId) => {
    const { data } = await cliente.get(`/api/pagos/${pagoId}`);
    return data?.pago || null;
  },

  obtenerPorCita: async (citaId) => {
    const { data } = await cliente.get(`/api/pagos/cita/${citaId}`);
    return data?.pago || null;
  },

  crearCheckout: async (citaId) => {
    const { data } = await cliente.post(`/api/pagos/cita/${citaId}/checkout`);
    return data?.pago || null;
  },

  sincronizarCheckout: async (sessionId) => {
    const { data } = await cliente.post(`/api/pagos/checkout/${sessionId}/sincronizar`);
    return data?.pago || null;
  },

  reembolsar: async (pagoId, datos) => {
    const { data } = await cliente.post(`/api/pagos/${pagoId}/reembolsar`, datos);
    return data?.pago || null;
  },

  sincronizarCitas: async () => {
    const { data } = await cliente.post("/api/pagos/sincronizar-citas");
    return data;
  },

  listarTarifas: async (soloActivas = false) => {
    const { data } = await cliente.get("/api/pagos/tarifas", {
      params: { activas: soloActivas },
    });
    return Array.isArray(data?.tarifas) ? data.tarifas : [];
  },

  crearTarifa: async (datos) => {
    const { data } = await cliente.post("/api/pagos/tarifas", datos);
    return data?.tarifa || null;
  },

  desactivarTarifa: async (tarifaId) => {
    const { data } = await cliente.delete(`/api/pagos/tarifas/${tarifaId}`);
    return data?.tarifa || null;
  },
};

export default cliente;
