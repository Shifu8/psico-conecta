import { LayoutDashboard, LifeBuoy, LogOut, UserRound } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import AvatarUsuario from "../componentes/AvatarUsuario";
import BotonTema from "../componentes/BotonTema";
import Logo from "../componentes/Logo";
import { usarAutenticacion } from "../contexto/ContextoAutenticacion";
import { rutaInicialPorRol } from "../servicios/servicioAutenticacion";

const roles = {
  ADMIN: "Administracion",
  PSYCHOLOGIST: "Profesional",
  PATIENT: "Paciente",
};

const claseEnlace = ({ isActive }) =>
  `flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-bold transition ${
    isActive
      ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/15"
      : "text-slate-600 hover:bg-blue-50 hover:text-blue-700 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-blue-300"
  }`;

export default function PlantillaPanel() {
  const { usuario, salir } = usarAutenticacion();
  const navegar = useNavigate();

  const cerrar = async () => {
    await salir();
    navegar("/iniciar-sesion", { replace: true });
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 lg:grid lg:grid-cols-[270px_1fr]">
      <aside className="border-b border-slate-200 bg-white/85 px-5 py-5 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/85 lg:flex lg:min-h-screen lg:flex-col lg:border-b-0 lg:border-r">
        <Logo />
        <div className="mt-7 hidden rounded-2xl bg-blue-50 p-4 dark:bg-blue-950/35 lg:block">
          <div className="flex items-center gap-3">
            <AvatarUsuario usuario={usuario} tamano="md" />
            <div className="min-w-0">
              <p className="truncate text-sm font-black text-slate-800 dark:text-white">
                {usuario.first_name} {usuario.last_name}
              </p>
              <p className="mt-0.5 text-xs font-bold uppercase tracking-[0.14em] text-blue-600 dark:text-blue-300">
                {roles[usuario.role] || "Mi cuenta"}
              </p>
            </div>
          </div>
        </div>
        <nav className="mt-6 flex gap-2 overflow-x-auto pb-1 lg:flex-col lg:overflow-visible">
          <NavLink to={rutaInicialPorRol(usuario.role)} className={claseEnlace}>
            <LayoutDashboard size={18} />
            Resumen
          </NavLink>
          <NavLink to="/perfil" className={claseEnlace}>
            <UserRound size={18} />
            Mi perfil
          </NavLink>
          <button
            type="button"
            onClick={cerrar}
            className="flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-bold text-slate-600 transition hover:bg-red-50 hover:text-red-700 dark:text-slate-300 dark:hover:bg-red-950/30 dark:hover:text-red-300"
          >
            <LogOut size={18} />
            Cerrar sesion
          </button>
        </nav>
        <div className="mt-auto hidden items-center gap-3 border-t border-slate-100 pt-5 text-xs text-slate-400 dark:border-slate-800 lg:flex">
          <LifeBuoy size={16} />
          soporte@psicoconecta.ec
        </div>
      </aside>

      <main className="min-w-0">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white/75 px-5 py-4 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/70 sm:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <AvatarUsuario usuario={usuario} tamano="sm" className="rounded-xl" />
            <div className="min-w-0">
              <p className="text-xs font-black uppercase tracking-[0.2em] text-blue-600 dark:text-blue-300">
                {roles[usuario.role] || "Mi cuenta"}
              </p>
              <p className="mt-1 truncate text-sm font-bold text-slate-700 dark:text-slate-200">
                {usuario.first_name} {usuario.last_name}
              </p>
            </div>
          </div>
          <BotonTema />
        </header>
        <div className="px-5 py-7 sm:px-8 lg:px-10 lg:py-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}