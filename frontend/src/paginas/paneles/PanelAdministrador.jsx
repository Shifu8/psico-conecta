import PlantillaPanel from '../../plantillas/PlantillaPanel'
import EncabezadoPanel from './EncabezadoPanel'
import { useAutenticacion } from '../../contexto/ContextoAutenticacion'

export default function PanelAdministrador() {
  const { usuario } = useAutenticacion()

  return (
    <PlantillaPanel>
      <EncabezadoPanel
        titulo="Panel de Administración"
        descripcion="Gestiona usuarios, roles y configuración del sistema"
      />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Usuarios</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Gestiona los usuarios registrados en el sistema</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Roles</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Administra los roles y permisos del sistema</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Configuración</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Configura los parámetros generales del sistema</p>
        </div>
      </div>
    </PlantillaPanel>
  )
}
