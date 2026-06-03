import { CheckCircle2, Circle } from "lucide-react";
import { obtenerRequisitosContrasena } from "../utilidades/validacion";

export default function RequisitosContrasena({ valor }) {
  const requisitos = obtenerRequisitosContrasena(valor);

  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-3 dark:border-slate-800 dark:bg-slate-950/60">
      <p className="text-xs font-bold text-slate-600 dark:text-slate-300">
        Tu contraseña debe incluir:
      </p>
      <ul className="mt-2 grid gap-1.5 text-xs sm:grid-cols-2">
        {requisitos.map((requisito) => {
          const Icono = requisito.cumplido ? CheckCircle2 : Circle;
          return (
            <li
              key={requisito.id}
              className={
                requisito.cumplido
                  ? "flex items-center gap-2 font-semibold text-emerald-700 dark:text-emerald-300"
                  : "flex items-center gap-2 text-slate-500 dark:text-slate-400"
              }
            >
              <Icono size={14} />
              <span>{requisito.texto}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
