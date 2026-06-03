import { Navigate, Outlet, useLocation } from "react-router-dom";
import { usarAutenticacion } from "../contexto/ContextoAutenticacion";

export default function RutaPrivada() {
  const { usuario, cargando } = usarAutenticacion();
  const ubicacion = useLocation();

  if (cargando) {
    return (
      <div className="grid min-h-screen place-items-center bg-slate-50 dark:bg-slate-950">
        <span className="h-10 w-10 animate-spin rounded-full border-4 border-blue-100 border-t-blue-600" />
      </div>
    );
  }

  return usuario ? <Outlet /> : <Navigate to="/iniciar-sesion" state={{ from: ubicacion }} replace />;
}
