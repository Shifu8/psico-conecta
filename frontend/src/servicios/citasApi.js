import axios from 'axios';
import { URLS_SERVICIOS } from './configuracionFrontend';

// Usamos el servicio-citas directamente desde la configuración centralizada
const baseURL = URLS_SERVICIOS.citas + '/api';

const API = axios.create({ baseURL });

API.interceptors.request.use(config => {
  const token = localStorage.getItem('psicoconecta_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const citasApi = {
  // Disponibilidad
  getSlots: (psicologoId, fecha) => API.get(`/disponibilidad/${psicologoId}/slots`, { params: { fecha } }),
  getDisponibilidad: (psicologoId) => API.get(`/disponibilidad/${psicologoId}`),
  crearBloque: (data) => API.post('/disponibilidad', data),
  editarBloque: (id, data) => API.put(`/disponibilidad/${id}`, data),
  eliminarBloque: (id) => API.delete(`/disponibilidad/${id}`),
  getExcepciones: (psicologoId) => API.get(`/disponibilidad/${psicologoId}/excepciones`),
  crearExcepcion: (psicologoId, data) => API.post(`/disponibilidad/${psicologoId}/excepciones`, data),
  eliminarExcepcion: (id) => API.delete(`/disponibilidad/excepciones/${id}`),

  // Citas
  agendar: (data) => API.post('/citas', data),
  getMisCitas: (params) => API.get('/citas/mis-citas', { params }),
  getTodasLasCitas: (params) => API.get('/citas', { params }),
  getDetalle: (id) => API.get(`/citas/${id}`),
  confirmar: (id) => API.put(`/citas/${id}/confirmar`),
  reprogramar: (id, data) => API.put(`/citas/${id}/reprogramar`, data),
  cancelar: (id, data) => API.put(`/citas/${id}/cancelar`, data),
  completar: (id) => API.put(`/citas/${id}/completar`),
  marcarNoAsistida: (id) => API.put(`/citas/${id}/no-asistida`),
  getHistorial: (id) => API.get(`/citas/${id}/historial`),
};
