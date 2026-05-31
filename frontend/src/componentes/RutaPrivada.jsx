import { Navigate } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'

export default function RutaPrivada({ children }) {
  const { usuario, cargando } = useAutenticacion()

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!usuario) {
    return <Navigate to="/iniciar-sesion" replace />
  }

  return children
}
