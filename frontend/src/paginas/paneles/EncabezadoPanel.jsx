import { useAutenticacion } from '../../contexto/ContextoAutenticacion'

export default function EncabezadoPanel({ titulo, descripcion }) {
  const { usuario } = useAutenticacion()

  return (
    <div className="mb-8">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{titulo}</h1>
      {descripcion && (
        <p className="mt-1 text-gray-600 dark:text-gray-400">{descripcion}</p>
      )}
      {usuario && (
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          Bienvenido, {usuario.nombres || usuario.correo}
        </p>
      )}
    </div>
  )
}
