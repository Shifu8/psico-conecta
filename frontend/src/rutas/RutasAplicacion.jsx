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
import PanelPaciente from "../paginas/paneles/PanelPaciente";
import PanelPsicologo from "../paginas/paneles/PanelPsicologo";
import PlantillaAutenticacion from "../plantillas/PlantillaAutenticacion";
import PlantillaPanel from "../plantillas/PlantillaPanel";

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
          <Route element={<RutaRol roles={["ADMIN"]} />}>
            <Route path="/administrador" element={<PanelAdministrador />} />
          </Route>
          <Route element={<RutaRol roles={["PSYCHOLOGIST"]} />}>
            <Route path="/psicologo" element={<PanelPsicologo />} />
          </Route>
          <Route element={<RutaRol roles={["PATIENT"]} />}>
            <Route path="/paciente" element={<PanelPaciente />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
