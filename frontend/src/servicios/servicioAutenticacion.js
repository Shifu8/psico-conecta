import api from './api'

export const getApiError = (error) => error.response?.data?.message || 'No fue posible completar la solicitud.'

export const iniciarSesionRequest = async (datos) => {
  const respuesta = await api.post('/api/usuarios/autenticacion/iniciar-sesion', datos)
  return respuesta.data
}

export const registrarRequest = async (datos) => {
  const respuesta = await api.post('/api/usuarios/autenticacion/registro', datos)
  return respuesta.data
}

export const cerrarSesionRequest = async () => {
  const respuesta = await api.post('/api/usuarios/autenticacion/cerrar-sesion')
  return respuesta.data
}

export const verificarSesionRequest = async () => {
  const respuesta = await api.get('/api/usuarios/autenticacion/verificar')
  return respuesta.data
}

export const googleLoginRequest = async (credential) => {
  const respuesta = await api.post('/api/usuarios/autenticacion/google', { credential })
  return respuesta.data
}
