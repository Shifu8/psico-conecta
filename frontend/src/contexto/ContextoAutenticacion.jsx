import { createContext, useContext, useState, useEffect } from 'react'
import { iniciarSesionRequest, verificarSesionRequest, cerrarSesionRequest, registrarRequest, googleLoginRequest } from '../servicios/servicioAutenticacion'

const ContextoAutenticacion = createContext()

export function ContextoAutenticacionProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    verificarSesion()
  }, [])

  const verificarSesion = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        setCargando(false)
        return
      }
      const respuesta = await verificarSesionRequest()
      setUsuario(respuesta.usuario)
    } catch {
      localStorage.removeItem('token')
    } finally {
      setCargando(false)
    }
  }

  const iniciarSesion = async (datos) => {
    const respuesta = await iniciarSesionRequest(datos)
    localStorage.setItem('token', respuesta.token)
    setUsuario(respuesta.usuario)
    return respuesta
  }

  const registrar = async (datos) => {
    const respuesta = await registrarRequest(datos)
    localStorage.setItem('token', respuesta.token)
    setUsuario(respuesta.usuario)
    return respuesta
  }

  const googleLogin = async (credential) => {
    const respuesta = await googleLoginRequest(credential)
    localStorage.setItem('token', respuesta.token)
    setUsuario(respuesta.usuario)
    return respuesta
  }

  const cerrarSesion = async () => {
    try {
      await cerrarSesionRequest()
    } catch {
    } finally {
      localStorage.removeItem('token')
      setUsuario(null)
    }
  }

  return (
    <ContextoAutenticacion.Provider value={{
      usuario, cargando, iniciarSesion, registrar, googleLogin, cerrarSesion, verificarSesion,
    }}>
      {children}
    </ContextoAutenticacion.Provider>
  )
}

export const useAutenticacion = () => useContext(ContextoAutenticacion)
export default ContextoAutenticacion
