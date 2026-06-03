import { Navigate, Outlet } from "react-router-dom";
import { usarAutenticacion } from "../contexto/ContextoAutenticacion";
import { rutaInicialPorRol } from "../servicios/servicioAutenticacion";

export default function RutaRol({ roles }) {
  const { usuario } = usarAutenticacion();
  return roles.includes(usuario?.role) ? (
    <Outlet />
  ) : (
    <Navigate to={rutaInicialPorRol(usuario?.role)} replace />
  );
}
