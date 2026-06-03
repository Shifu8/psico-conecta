import { motion } from "framer-motion";
import { HeartPulse, ShieldCheck, Sparkles } from "lucide-react";
import { Link, Outlet, useLocation } from "react-router-dom";
import BotonTema from "../componentes/BotonTema";
import Logo from "../componentes/Logo";

export default function PlantillaAutenticacion() {
  const ubicacion = useLocation();

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="relative hidden w-[48%] flex-col justify-between overflow-hidden bg-gradient-to-br from-slate-950 via-blue-900 to-indigo-950 p-10 text-white lg:flex">
        <div className="absolute -left-16 top-24 h-64 w-64 rounded-full bg-cyan-400/15 blur-3xl" />
        <div className="absolute -bottom-20 right-0 h-80 w-80 rounded-full bg-violet-400/20 blur-3xl" />
        <Link to="/" className="relative flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-white/20 text-white">
            <HeartPulse size={23} />
          </span>
          <span className="text-lg font-black tracking-tight">
            Psico<span className="text-cyan-300">Conecta</span>
          </span>
        </Link>
        <div className="relative max-w-md">
          <span className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">
            Tu bienestar importa
          </span>
          <h1 className="mt-5 text-4xl font-black leading-tight">
            Acompañamiento psicológico{" "}
            <span className="text-cyan-300">cercano y conectado.</span>
          </h1>
          <p className="mt-4 leading-relaxed text-blue-100/80">
            PsicoConecta reúne orientación profesional, sesiones virtuales y seguimiento
            emocional en una experiencia clara y humana.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-3">
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <ShieldCheck size={20} className="text-cyan-300" />
              <p className="mt-2 text-sm font-bold">Acceso protegido</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <Sparkles size={20} className="text-cyan-300" />
              <p className="mt-2 text-sm font-bold">Atención integral</p>
            </div>
          </div>
        </div>
        <p className="relative text-xs text-blue-200/60">
          &copy; 2026 PsicoConecta &mdash; Todos los derechos reservados.
        </p>
      </div>
      <div className="relative flex w-full items-center justify-center overflow-hidden px-5 py-10 text-slate-900 transition-colors dark:text-slate-100 lg:w-[52%]">
        <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-blue-200/45 blur-3xl dark:bg-blue-950/30" />
        <div className="relative w-full max-w-lg">
          <div className="mb-8 flex items-center justify-between">
            <div className="lg:hidden">
              <Logo />
            </div>
            <div className="ml-auto">
              <BotonTema compacto />
            </div>
          </div>
          <motion.div
            key={ubicacion.pathname}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.32 }}
            className="panel p-6 sm:p-8"
          >
            <Outlet />
          </motion.div>
        </div>
      </div>
    </div>
  );
}
