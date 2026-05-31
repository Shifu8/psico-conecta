import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAutenticacion } from '../../contexto/ContextoAutenticacion'
import { getApiError } from '../../servicios/servicioAutenticacion'
import PlantillaAutenticacion from '../../plantillas/PlantillaAutenticacion'
import CampoFormulario from '../../componentes/CampoFormulario'
import { GoogleLogin } from '@react-oauth/google'
import { Mail, Lock, LogIn } from 'lucide-react'

export default function InicioSesion() {
  const { iniciarSesion, googleLogin } = useAutenticacion()
  const navigate = useNavigate()
  const [datos, setDatos] = useState({ correo: '', contrasena: '' })
  const [error, setError] = useState('')
  const [googleError, setGoogleError] = useState('')
  const [cargando, setCargando] = useState(false)

  const manejarCambio = (e) => {
    setDatos({ ...datos, [e.target.name]: e.target.value })
    setError('')
  }

  const manejarEnvio = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError('')
    try {
      const respuesta = await iniciarSesion(datos)
      if (respuesta.redirigir) {
        navigate(respuesta.redirigir)
      } else {
        navigate('/panel')
      }
    } catch (requestError) {
      setError(getApiError(requestError))
    } finally {
      setCargando(false)
    }
  }

  const manejarGoogleExito = async (response) => {
    try {
      setGoogleError('')
      const respuesta = await googleLogin(response.credential)
      if (respuesta.redirigir) {
        navigate(respuesta.redirigir)
      } else {
        navigate('/panel')
      }
    } catch (requestError) {
      setGoogleError(getApiError(requestError))
    }
  }

  const manejarGoogleError = () => {
    setGoogleError('No se pudo iniciar sesión con Google. Intenta de nuevo.')
  }

  return (
    <PlantillaAutenticacion
      titulo="Iniciar sesión"
      subtitulo="Accede a tu cuenta de PsicoConecta"
    >
      <form onSubmit={manejarEnvio} className="space-y-4">
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg">
            {error}
          </div>
        )}
        <CampoFormulario label="Correo electrónico">
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="email"
              name="correo"
              value={datos.correo}
              onChange={manejarCambio}
              required
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              placeholder="correo@unl.edu.ec"
            />
          </div>
        </CampoFormulario>
        <CampoFormulario label="Contraseña">
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="password"
              name="contrasena"
              value={datos.contrasena}
              onChange={manejarCambio}
              required
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              placeholder="••••••••"
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
            <LogIn className="h-4 w-4" />
          )}
          {cargando ? 'Iniciando sesión...' : 'Iniciar sesión'}
        </button>
      </form>

      <div className="mt-4">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-800 text-gray-500">O continúa con</span>
          </div>
        </div>

        {googleError && (
          <div className="mt-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg">
            {googleError}
          </div>
        )}

        <div className="mt-3 flex justify-center">
          <GoogleLogin
            onSuccess={manejarGoogleExito}
            onError={manejarGoogleError}
            size="large"
            text="signin_with"
            shape="rectangular"
          />
        </div>
      </div>

      <div className="mt-6 text-center space-y-2 text-sm">
        <p className="text-gray-600 dark:text-gray-400">
          ¿No tienes cuenta?{' '}
          <Link to="/registro" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">
            Registrarse
          </Link>
        </p>
        <p className="text-gray-600 dark:text-gray-400">
          <Link to="/recuperar-contrasena" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">
            ¿Olvidaste tu contraseña?
          </Link>
        </p>
      </div>
    </PlantillaAutenticacion>
  )
}
