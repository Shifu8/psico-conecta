import { ProveedorAutenticacion } from "./contexto/ContextoAutenticacion";
import { ProveedorTema } from "./contexto/ContextoTema";
import RutasAplicacion from "./rutas/RutasAplicacion";

export default function Aplicacion() {
  return (
    <ProveedorTema>
      <ProveedorAutenticacion>
        <RutasAplicacion />
      </ProveedorAutenticacion>
    </ProveedorTema>
  );
}
