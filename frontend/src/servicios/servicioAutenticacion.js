import api from "./api";

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
