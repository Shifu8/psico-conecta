import { Outlet } from 'react-router-dom'
import BarraNavegacion from '../componentes/BarraNavegacion'

export default function PlantillaPanel() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <BarraNavegacion />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
