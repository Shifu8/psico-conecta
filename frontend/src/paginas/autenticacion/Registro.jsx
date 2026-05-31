import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAutenticacion } from '../../contexto/ContextoAutenticacion'
import { getApiError } from '../../servicios/servicioAutenticacion'
import PlantillaAutenticacion from '../../plantillas/PlantillaAutenticacion'
import CampoFormulario from '../../componentes/CampoFormulario'
import { Mail, User, Lock, UserPlus } from 'lucide-react'

export default function Registro() {
  const { registrar } = useAutenticacion()
  const navigate = useNavigate()
  const [datos, setDatos] = useState({ nombres: '', correo: '', contrasena: '', confirmarContrasena: '' })
  const [error, setError] = useState('')
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
      await registrar({ nombres: datos.nombres, correo: datos.correo, contrasena: datos.contrasena })
      navigate('/panel')
    } catch (requestError) {
      setError(getApiError(requestError))
    } finally {
      setCargando(false)
    }
  }

  return (
    <PlantillaAutenticacion
      titulo="Crear cuenta"
      subtitulo="Regístrate en PsicoConecta"
    >
      <form onSubmit={manejarEnvio} className="space-y-4">
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg">
            {error}
          </div>
        )}
        <CampoFormulario label="Nombres completos">
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              name="nombres"
              value={datos.nombres}
              onChange={manejarCambio}
              required
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              placeholder="Juan Pérez"
            />
          </div>
        </CampoFormulario>
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
          disabled={cargando}
          className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg font-medium text-sm transition-colors disabled:opacity-50"
        >
          {cargando ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <UserPlus className="h-4 w-4" />
          )}
          {cargando ? 'Registrando...' : 'Crear cuenta'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
        ¿Ya tienes cuenta?{' '}
        <Link to="/iniciar-sesion" className="text-primary-600 dark:text-primary-400 hover:underline font-medium">
          Iniciar sesión
        </Link>
      </p>
    </PlantillaAutenticacion>
  )
}
