import { Routes, Route, Navigate } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'
import RutaPrivada from '../componentes/RutaPrivada'
import RutaRol from '../componentes/RutaRol'
import Inicio from '../paginas/Inicio'
import Perfil from '../paginas/Perfil'
import InicioSesion from '../paginas/autenticacion/InicioSesion'
import Registro from '../paginas/autenticacion/Registro'
import RecuperarContrasena from '../paginas/autenticacion/RecuperarContrasena'
import RestablecerContrasena from '../paginas/autenticacion/RestablecerContrasena'
import PlantillaPanel from '../plantillas/PlantillaPanel'
import PanelAdministrador from '../paginas/paneles/PanelAdministrador'
import PanelPaciente from '../paginas/paneles/PanelPaciente'
import PanelPsicologo from '../paginas/paneles/PanelPsicologo'

export default function RutasAplicacion() {
  const { usuario } = useAutenticacion()

  const obtenerPanel = () => {
    if (!usuario) return <Navigate to="/iniciar-sesion" replace />
    switch (usuario.rol) {
      case 'administrador':
        return <PanelAdministrador />
      case 'psicologo':
        return <PanelPsicologo />
      case 'paciente':
        return <PanelPaciente />
      default:
        return <PanelPaciente />
    }
  }

  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/iniciar-sesion" element={<InicioSesion />} />
      <Route path="/registro" element={<Registro />} />
      <Route path="/recuperar-contrasena" element={<RecuperarContrasena />} />
      <Route path="/restablecer-contrasena" element={<RestablecerContrasena />} />
      <Route
        path="/perfil"
        element={
          <RutaPrivada>
            <PlantillaPanel />
          </RutaPrivada>
        }
      >
        <Route index element={<Perfil />} />
      </Route>
      <Route
        path="/panel"
        element={
          <RutaPrivada>
            <PlantillaPanel />
          </RutaPrivada>
        }
      >
        <Route index element={<>{obtenerPanel()}</>} />
      </Route>
      <Route
        path="/panel/administrador"
        element={
          <RutaRol roles={['administrador']}>
            <PlantillaPanel />
          </RutaRol>
        }
      >
        <Route index element={<PanelAdministrador />} />
      </Route>
      <Route
        path="/panel/psicologo"
        element={
          <RutaRol roles={['psicologo']}>
            <PlantillaPanel />
          </RutaRol>
        }
      >
        <Route index element={<PanelPsicologo />} />
      </Route>
      <Route
        path="/panel/paciente"
        element={
          <RutaRol roles={['paciente']}>
            <PlantillaPanel />
          </RutaRol>
        }
      >
        <Route index element={<PanelPaciente />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
