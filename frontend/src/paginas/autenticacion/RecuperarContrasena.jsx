import { useState } from 'react'
import { Link } from 'react-router-dom'
import PlantillaAutenticacion from '../../plantillas/PlantillaAutenticacion'
import CampoFormulario from '../../componentes/CampoFormulario'
import { Mail, SendHorizonal } from 'lucide-react'
import api from '../../servicios/api'

export default function RecuperarContrasena() {
  const [correo, setCorreo] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  const manejarEnvio = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError('')
    setMensaje('')
    try {
      const respuesta = await api.post('/api/usuarios/autenticacion/recuperar-contrasena', { correo })
      setMensaje(respuesta.data.message || 'Se ha enviado un enlace de recuperación a tu correo.')
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'No fue posible procesar la solicitud.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <PlantillaAutenticacion
      titulo="Recuperar contraseña"
      subtitulo="Te enviaremos un enlace para restablecer tu contraseña"
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
        <CampoFormulario label="Correo electrónico">
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="email"
              value={correo}
              onChange={(e) => { setCorreo(e.target.value); setError('') }}
              required
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              placeholder="correo@unl.edu.ec"
            />
          </div>
        </CampoFormulario>
        <button
          type="submit"
          disabled={cargando}
          className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg font-medium text-sm transition-colors disabled:opacity-50"
        >
          {cargando ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <SendHorizonal className="h-4 w-4" />
          )}
          {cargando ? 'Enviando...' : 'Enviar enlace'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
        <Link to="/iniciar-sesion" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">
          Volver a iniciar sesión
        </Link>
      </p>
    </PlantillaAutenticacion>
  )
}
