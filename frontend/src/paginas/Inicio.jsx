import { Link } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'
import BarraNavegacion from '../componentes/BarraNavegacion'
import TarjetaCaracteristica from '../componentes/TarjetaCaracteristica'
import { Brain, Calendar, Shield, ArrowRight, MessageCircle } from 'lucide-react'

export default function Inicio() {
  const { usuario } = useAutenticacion()

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <BarraNavegacion />

      <main>
        <section className="relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
                Bienvenido a{' '}
                <span className="text-primary-600 dark:text-primary-400">PsicoConecta</span>
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8">
                Plataforma integral de telepsicología que conecta pacientes con psicólogos
                profesionales para brindar apoyo emocional accesible y de calidad.
              </p>
              <div className="flex justify-center gap-4">
                {usuario ? (
                  <Link
                    to="/panel"
                    className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Ir a mi panel
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                ) : (
                  <>
                    <Link
                      to="/registro"
                      className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    >
                      Registrarse
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                    <Link
                      to="/iniciar-sesion"
                      className="inline-flex items-center gap-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 px-6 py-3 rounded-lg font-medium transition-colors"
                    >
                      Iniciar sesión
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-gray-50 dark:bg-gray-800/50 py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
              ¿Por qué PsicoConecta?
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <TarjetaCaracteristica
                icono={<Brain className="h-6 w-6 text-primary-600" />}
                titulo="Atención Profesional"
                descripcion="Conéctate con psicólogos certificados desde la comodidad de tu hogar."
              />
              <TarjetaCaracteristica
                icono={<Calendar className="h-6 w-6 text-primary-600" />}
                titulo="Gestión de Citas"
                descripcion="Programa y administra tus sesiones de manera fácil y rápida."
              />
              <TarjetaCaracteristica
                icono={<MessageCircle className="h-6 w-6 text-primary-600" />}
                titulo="Teleconsulta"
                descripcion="Sesiones virtuales seguras con herramientas de videollamada integradas."
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
