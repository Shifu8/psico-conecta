import { Navigate, Outlet } from "react-router-dom";
import { usarAutenticacion } from "../contexto/ContextoAutenticacion";
import { rutaInicialPorRol } from "../servicios/servicioAutenticacion";

export default function RutaRol({ roles }) {
  const { usuario } = usarAutenticacion();
  const rolNombre = typeof usuario?.role === "object" ? usuario?.role?.name : usuario?.role;
  return roles.includes(rolNombre) ? (
    <Outlet />
  ) : (
    <Navigate to={rutaInicialPorRol(rolNombre)} replace />
  );
}
