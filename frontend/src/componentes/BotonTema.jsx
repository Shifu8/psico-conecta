import { useTema } from '../contexto/ContextoTema'
import { Sun, Moon } from 'lucide-react'

export default function BotonTema() {
  const { oscuro, toggleTema } = useTema()

  return (
    <button
      onClick={toggleTema}
      className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      aria-label="Cambiar tema"
    >
      {oscuro ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </button>
  )
}
