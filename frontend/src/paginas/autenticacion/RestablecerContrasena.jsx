import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import PlantillaAutenticacion from '../../plantillas/PlantillaAutenticacion'
import CampoFormulario from '../../componentes/CampoFormulario'
import { Lock, KeyRound } from 'lucide-react'
import api from '../../servicios/api'

export default function RestablecerContrasena() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  const [datos, setDatos] = useState({ contrasena: '', confirmarContrasena: '' })
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [cargando, setCargando] = useState(false)

  const manejarCambio = (e) => {
    setDatos({ ...datos, [e.target.name]: e.target.value })
    setError('')
  }

  const manejarEnvio = async (e) => {
    e.preventDefault()
    if (datos.contrasena !== datos.confirmarContrasena) {
      setError('Las contraseñas no coinciden')
      return
    }
    setCargando(true)
    setError('')
    try {
      const respuesta = await api.post('/api/usuarios/autenticacion/restablecer-contrasena', {
        token,
        contrasena: datos.contrasena,
      })
      setMensaje(respuesta.data.message || 'Contraseña restablecida exitosamente.')
      setTimeout(() => navigate('/iniciar-sesion'), 3000)
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'El enlace no es válido o ha expirado.')
    } finally {
      setCargando(false)
    }
  }

  if (!token) {
    return (
      <PlantillaAutenticacion titulo="Enlace inválido" subtitulo="El enlace de recuperación no es válido">
        <p className="text-center text-gray-600 dark:text-gray-400">
          El enlace al que intentas acceder no es válido. Solicita un nuevo enlace de recuperación.
        </p>
      </PlantillaAutenticacion>
    )
  }

  return (
    <PlantillaAutenticacion
      titulo="Restablecer contraseña"
      subtitulo="Ingresa tu nueva contraseña"
    >
      <form onSubmit={manejarEnvio} className="space-y-4">
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg">
            {error}
          </div>
        )}
        {mensaje && (
          <div className="bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 text-sm p-3 rounded-lg">
            {mensaje}
          </div>
        )}
        <CampoFormulario label="Nueva contraseña">
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="password"
              name="contrasena"
              value={datos.contrasena}
              onChange={manejarCambio}
              required
              minLength={8}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              placeholder="••••••••"
            />
          </div>
        </CampoFormulario>
        <CampoFormulario label="Confirmar contraseña">
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="password"
              name="confirmarContrasena"
              value={datos.confirmarContrasena}
              onChange={manejarCambio}
              required
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              placeholder="••••••••"
            />
          </div>
        </CampoFormulario>
        <button
          type="submit"
          disabled={cargando || !!mensaje}
          className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg font-medium text-sm transition-colors disabled:opacity-50"
        >
          {cargando ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <KeyRound className="h-4 w-4" />
          )}
          {cargando ? 'Restableciendo...' : 'Restablecer contraseña'}
        </button>
      </form>
    </PlantillaAutenticacion>
  )
}
