import api from "./api";
import { API_BASE_URL } from "./configuracionFrontend";

const BASE = "/api/usuarios/autenticacion";

export const iniciarSesion = (credenciales) =>
  api.post(`${BASE}/inicio-sesion`, credenciales);

export const registrarUsuario = (datos) => api.post(`${BASE}/registro`, datos);

export const cerrarSesion = () => api.post(`${BASE}/cierre-sesion`);

export const solicitarRecuperacion = (email, captcha_token) =>
  api.post(`${BASE}/recuperar-contrasena`, {
    email,
    ...(captcha_token ? { captcha_token } : {}),
  });

export const restablecerContrasena = (datos) =>
  api.post(`${BASE}/restablecer-contrasena`, datos);

export const obtenerMiPerfil = () => api.get(`${BASE}/mi-perfil`);

export const actualizarPerfil = (userId, datos) =>
  api.put(`/api/usuarios/${userId}`, datos);

export const subirFotoPerfil = (userId, archivo) => {
  const datos = new FormData();
  datos.append("foto", archivo);
  return api.post(`/api/usuarios/${userId}/foto-perfil`, datos, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const eliminarFotoPerfil = (userId) =>
  api.delete(`/api/usuarios/${userId}/foto-perfil`);

export const registrarEventoAuditoria = (evento) =>
  api.post(`/api/usuarios/auditoria/registrar`, evento);

export const resolverUrlFotoPerfil = (usuario) => {
  const url = usuario?.profile_photo_url;
  if (!url) return "";
  if (/^https?:\/\//i.test(url)) return url;
  
  let base = API_BASE_URL;
  if (base.endsWith('/api') && url.startsWith('/api')) {
    base = base.replace(/\/api$/, '');
  }
  
  return `${base}${url.startsWith("/") ? url : `/${url}`}`;
};

export const googleLoginRequest = (credential) =>
  api.post(`${BASE}/google`, { credential });

export const obtenerConfiguracionGoogle = () =>
  api.get(`${BASE}/google/configuracion`);

export const rutaInicialPorRol = (rol) => {
  const rutas = {
    ADMIN: "/administrador",
    PSYCHOLOGIST: "/psicologo",
    PATIENT: "/paciente",
  };
  return rutas[rol] || "/perfil";
};