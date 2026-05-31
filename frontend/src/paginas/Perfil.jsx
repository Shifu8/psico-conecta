import { useAutenticacion } from '../contexto/ContextoAutenticacion'
import RutaPrivada from '../componentes/RutaPrivada'
import PlantillaPanel from '../plantillas/PlantillaPanel'
import EncabezadoPanel from './paneles/EncabezadoPanel'
import { User, Mail, Shield } from 'lucide-react'

function PerfilContenido() {
  const { usuario } = useAutenticacion()

  return (
    <div>
      <EncabezadoPanel titulo="Mi Perfil" descripcion="Información de tu cuenta" />
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <User className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Nombres</p>
              <p className="text-gray-900 dark:text-white font-medium">{usuario?.nombres || '—'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Mail className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Correo</p>
              <p className="text-gray-900 dark:text-white font-medium">{usuario?.correo || '—'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Shield className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Rol</p>
              <p className="text-gray-900 dark:text-white font-medium capitalize">{usuario?.rol || '—'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Perfil() {
  return (
    <RutaPrivada>
      <PlantillaPanel>
        <PerfilContenido />
      </PlantillaPanel>
    </RutaPrivada>
  )
}
