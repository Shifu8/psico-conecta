import PlantillaPanel from '../../plantillas/PlantillaPanel'
import EncabezadoPanel from './EncabezadoPanel'

export default function PanelPsicologo() {
  return (
    <PlantillaPanel>
      <EncabezadoPanel
        titulo="Panel del Psicólogo"
        descripcion="Gestiona tus pacientes y sesiones"
      />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Mis Pacientes</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Gestiona la lista de tus pacientes</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Próximas Citas</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Revisa tus citas programadas</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Historial Clínico</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">Accede al historial de tus pacientes</p>
        </div>
      </div>
    </PlantillaPanel>
  )
}
