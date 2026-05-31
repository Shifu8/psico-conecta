import { Navigate } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'

export default function RutaRol({ roles, children }) {
  const { usuario } = useAutenticacion()

  if (!usuario) {
    return <Navigate to="/iniciar-sesion" replace />
  }

  const tieneRol = usuario.rol && roles.includes(usuario.rol)

  if (!tieneRol) {
    return <Navigate to="/panel" replace />
  }

  return children
}
