export default function PlantillaAutenticacion({ titulo, subtitulo, children }) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-600 dark:text-primary-400">
            PsicoConecta
          </h1>
          <h2 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
            {titulo}
          </h2>
          {subtitulo && (
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {subtitulo}
            </p>
          )}
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          {children}
        </div>
      </div>
    </div>
  )
}
