import { Navigate, Route, Routes } from "react-router-dom";
import RutaPrivada from "../componentes/RutaPrivada";
import RutaRol from "../componentes/RutaRol";
import Inicio from "../paginas/Inicio";
import Perfil from "../paginas/Perfil";
import InicioSesion from "../paginas/autenticacion/InicioSesion";
import RecuperarContrasena from "../paginas/autenticacion/RecuperarContrasena";
import Registro from "../paginas/autenticacion/Registro";
import RestablecerContrasena from "../paginas/autenticacion/RestablecerContrasena";
import PanelAdministrador from "../paginas/paneles/PanelAdministrador";
import PaginaDisponibilidadAdmin from "../paginas/admin/PaginaDisponibilidadAdmin";
import PanelPaciente from "../paginas/paneles/PanelPaciente";
import PanelPsicologo from "../paginas/paneles/PanelPsicologo";
import DashboardPsicologo from "../paginas/paneles/DashboardPsicologo";
import PlantillaAutenticacion from "../plantillas/PlantillaAutenticacion";
import PlantillaPanel from "../plantillas/PlantillaPanel";

// Citas
import PaginaCitas from "../paginas/citas/PaginaCitas";
import PaginaAgendarCita from "../paginas/citas/PaginaAgendarCita";
import PaginaDetalleCita from "../paginas/citas/PaginaDetalleCita";
import PaginaTeleconsultas from "../paginas/teleconsultas/PaginaTeleconsultas";
import PaginaSalaTeleconsulta from "../paginas/teleconsultas/PaginaSalaTeleconsulta";

export default function RutasAplicacion() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route element={<PlantillaAutenticacion />}>
        <Route path="/iniciar-sesion" element={<InicioSesion />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/recuperar-contrasena" element={<RecuperarContrasena />} />
        <Route path="/restablecer-contrasena" element={<RestablecerContrasena />} />
      </Route>

      <Route element={<RutaPrivada />}>
        <Route element={<PlantillaPanel />}>
          <Route path="/perfil" element={<Perfil />} />
          
          <Route path="/citas" element={<PaginaCitas />} />
          <Route path="/citas/:id" element={<PaginaDetalleCita />} />

          <Route element={<RutaRol roles={["PATIENT", "PSYCHOLOGIST"]} />}>
            <Route path="/teleconsultas" element={<PaginaTeleconsultas />} />
            <Route path="/teleconsultas/:citaId" element={<PaginaSalaTeleconsulta />} />
          </Route>

          <Route element={<RutaRol roles={["ADMIN"]} />}>
            <Route path="/administrador" element={<PanelAdministrador />} />
            <Route path="/administrador/disponibilidad" element={<PaginaDisponibilidadAdmin />} />
          </Route>
          <Route element={<RutaRol roles={["PSYCHOLOGIST"]} />}>
            <Route path="/psicologo" element={<PanelPsicologo />} />
            <Route path="/psicologo/telemetria/:patientId" element={<DashboardPsicologo />} />
          </Route>
          <Route element={<RutaRol roles={["PATIENT"]} />}>
            <Route path="/paciente" element={<PanelPaciente />} />
            <Route path="/citas/agendar" element={<PaginaAgendarCita />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
