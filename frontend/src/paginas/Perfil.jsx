import { Mail, ShieldCheck, UserRound } from "lucide-react";
import { usarAutenticacion } from "../contexto/ContextoAutenticacion";
import EncabezadoPanel from "./paneles/EncabezadoPanel";

const nombresRoles = {
  ADMIN: "Administrador",
  PSYCHOLOGIST: "Psicólogo",
  PATIENT: "Paciente",
};

export default function Perfil() {
  const { usuario } = usarAutenticacion();

  return (
    <>
      <EncabezadoPanel
        etiqueta="Mi cuenta"
        titulo="Perfil personal"
        texto="Consulta la información vinculada a tu cuenta de PsicoConecta."
      />
      <section className="panel mt-8 max-w-3xl p-6 sm:p-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
          <span className="grid h-20 w-20 place-items-center rounded-3xl bg-blue-50 text-blue-600 dark:bg-blue-950/50 dark:text-blue-300">
            <UserRound size={38} />
          </span>
          <div>
            <h2 className="text-2xl font-black text-slate-900 dark:text-white">
              {usuario.first_name} {usuario.last_name}
            </h2>
            <p className="mt-1 text-sm font-bold text-blue-600 dark:text-blue-300">
              {nombresRoles[usuario.role] || usuario.role}
            </p>
          </div>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border border-blue-100 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/80">
            <Mail size={19} className="text-blue-600 dark:text-blue-300" />
            <p className="mt-3 text-xs font-bold uppercase tracking-wider text-slate-400">Correo</p>
            <p className="mt-1 break-all text-sm font-semibold">{usuario.email}</p>
          </div>
          <div className="rounded-2xl border border-blue-100 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/80">
            <ShieldCheck size={19} className="text-blue-600 dark:text-blue-300" />
            <p className="mt-3 text-xs font-bold uppercase tracking-wider text-slate-400">Estado</p>
            <p className="mt-1 text-sm font-semibold">
              {usuario.status === "active" || !usuario.status ? "Activo" : "Pausado"}
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
