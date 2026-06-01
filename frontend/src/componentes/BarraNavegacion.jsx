import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { usarAutenticacion } from "../contexto/ContextoAutenticacion";
import { rutaInicialPorRol } from "../servicios/servicioAutenticacion";
import BotonTema from "./BotonTema";
import Logo from "./Logo";

const enlaces = [
  { texto: "Inicio", href: "/#inicio" },
  { texto: "Beneficios", href: "/#beneficios" },
  { texto: "Cómo funciona", href: "/#como-funciona" },
  { texto: "Para psicólogos", href: "/#psicologos" },
];

export default function BarraNavegacion() {
  const { usuario } = usarAutenticacion();
  const [menuAbierto, setMenuAbierto] = useState(false);
  const ubicacion = useLocation();

  useEffect(() => {
    setMenuAbierto(false);
  }, [ubicacion.pathname]);

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/80">
      <nav className="contenedor flex h-20 items-center justify-between gap-3">
        <Logo />
        <div className="hidden items-center gap-6 lg:flex">
          {enlaces.map((enlace) => (
            <a key={enlace.href} href={enlace.href} className="enlace">
              {enlace.texto}
            </a>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <BotonTema compacto />
          {usuario ? (
            <Link to={rutaInicialPorRol(usuario.role)} className="boton-primario py-2.5">
              Mi panel
            </Link>
          ) : (
            <>
              <Link to="/iniciar-sesion" className="hidden text-sm font-bold text-slate-700 transition hover:text-blue-700 dark:text-slate-200 dark:hover:text-blue-300 sm:block">
                Iniciar sesión
              </Link>
              <Link to="/registro" className="boton-primario hidden py-2.5 sm:inline-flex">
                Crear cuenta
              </Link>
            </>
          )}
          <button
            type="button"
            onClick={() => setMenuAbierto((actual) => !actual)}
            className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:text-blue-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 lg:hidden"
            aria-label={menuAbierto ? "Cerrar menú" : "Abrir menú"}
            aria-expanded={menuAbierto}
          >
            {menuAbierto ? <X size={19} /> : <Menu size={19} />}
          </button>
        </div>
      </nav>
      {menuAbierto && (
        <div className="border-t border-slate-200/70 bg-white/95 px-5 py-5 shadow-lg backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/95 lg:hidden">
          <div className="mx-auto flex max-w-7xl flex-col gap-4">
            {enlaces.map((enlace) => (
              <a key={enlace.href} href={enlace.href} className="enlace" onClick={() => setMenuAbierto(false)}>
                {enlace.texto}
              </a>
            ))}
            {!usuario && (
              <div className="mt-1 flex flex-col gap-3 sm:hidden">
                <Link to="/iniciar-sesion" className="boton-secundario w-full">
                  Iniciar sesión
                </Link>
                <Link to="/registro" className="boton-primario w-full">
                  Crear cuenta
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
