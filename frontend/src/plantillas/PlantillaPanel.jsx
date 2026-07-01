import { useState } from "react";
import { LayoutDashboard, LifeBuoy, LogOut, UserRound, CalendarDays, Clock3 } from "lucide-react";
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
  const [mostrarModalSalir, setMostrarModalSalir] = useState(false);

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
          <NavLink to="/citas" className={claseEnlace}>
            <CalendarDays size={18} />
            Citas
          </NavLink>
          {usuario.role === "ADMIN" && (
            <NavLink to="/administrador/disponibilidad" className={claseEnlace}>
              <Clock3 size={18} />
              Disponibilidad
            </NavLink>
          )}

          <NavLink to="/perfil" className={claseEnlace}>
            <UserRound size={18} />
            Mi perfil
          </NavLink>
          <button
            type="button"
            onClick={() => setMostrarModalSalir(true)}
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
        <header className="flex items-center justify-end border-b border-slate-200 bg-white/75 px-5 py-4 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/70 sm:px-8">
          <div className="mr-auto flex min-w-0 items-center gap-3 lg:hidden">
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

      {mostrarModalSalir && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-3xl bg-white p-6 shadow-2xl dark:bg-slate-900 border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in duration-200">
            <div className="flex flex-col items-center text-center">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-500">
                <LogOut size={28} />
              </div>
              <h3 className="mb-2 text-xl font-bold text-slate-800 dark:text-white">
                ¿Cerrar sesión?
              </h3>
              <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
                ¿Estás seguro de que deseas salir de tu cuenta? Tendrás que volver a iniciar sesión para acceder.
              </p>
              <div className="flex w-full gap-3">
                <button
                  onClick={() => setMostrarModalSalir(false)}
                  className="flex-1 rounded-xl bg-slate-100 px-4 py-3 text-sm font-bold text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  Cancelar
                </button>
                <button
                  onClick={cerrar}
                  className="flex-1 rounded-xl bg-red-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-red-700"
                >
                  Sí, salir
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}