export default function TarjetaCaracteristica({ icono, titulo, descripcion }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-center w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg mb-4">
        {icono}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {titulo}
      </h3>
      <p className="text-gray-600 dark:text-gray-400 text-sm">
        {descripcion}
      </p>
    </div>
  )
}
