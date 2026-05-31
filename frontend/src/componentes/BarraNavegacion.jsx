import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'
import { useTema } from '../contexto/ContextoTema'
import BotonTema from './BotonTema'
import Logo from './Logo'
import { Menu, X, User, LogOut, LayoutDashboard } from 'lucide-react'

export default function BarraNavegacion() {
  const { usuario, cerrarSesion } = useAutenticacion()
  const [abierto, setAbierto] = useState(false)
  const navigate = useNavigate()

  const manejarCerrarSesion = async () => {
    await cerrarSesion()
    navigate('/iniciar-sesion')
  }

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0">
              <Logo />
            </Link>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <BotonTema />
            {usuario ? (
              <>
                <Link to="/perfil" className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">
                  <User className="h-4 w-4" />
                  {usuario.nombres || usuario.correo}
                </Link>
                <Link to="/panel" className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">
                  <LayoutDashboard className="h-4 w-4" />
                  Panel
                </Link>
                <button onClick={manejarCerrarSesion} className="flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 px-3 py-2 rounded-md text-sm font-medium">
                  <LogOut className="h-4 w-4" />
                  Cerrar sesión
                </button>
              </>
            ) : (
              <Link to="/iniciar-sesion" className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Iniciar sesión
              </Link>
            )}
          </div>
          <div className="md:hidden flex items-center gap-2">
            <BotonTema />
            <button onClick={() => setAbierto(!abierto)} className="text-gray-600 dark:text-gray-300">
              {abierto ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>
      {abierto && (
        <div className="md:hidden border-t border-gray-200 dark:border-gray-700">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {usuario ? (
              <>
                <Link to="/perfil" className="block px-3 py-2 rounded-md text-base font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                  Perfil
                </Link>
                <Link to="/panel" className="block px-3 py-2 rounded-md text-base font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                  Panel
                </Link>
                <button onClick={manejarCerrarSesion} className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700">
                  Cerrar sesión
                </button>
              </>
            ) : (
              <Link to="/iniciar-sesion" className="block px-3 py-2 rounded-md text-base font-medium text-primary-600 dark:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700">
                Iniciar sesión
              </Link>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
