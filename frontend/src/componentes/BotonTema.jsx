import { AnimatePresence, motion } from "framer-motion";
import { Moon, Sun } from "lucide-react";
import { usarTema } from "../contexto/ContextoTema";

export default function BotonTema({ compacto = false }) {
  const { oscuro, alternarTema } = usarTema();
  const etiqueta = oscuro ? "Usar modo claro" : "Usar modo oscuro";

  return (
    <motion.button
      type="button"
      onClick={alternarTema}
      whileTap={{ scale: 0.94 }}
      className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white/80 px-3 py-2 text-xs font-bold text-slate-600 shadow-sm transition hover:border-blue-200 hover:text-blue-700 dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-200 dark:hover:border-blue-700 dark:hover:text-blue-300"
      aria-label={etiqueta}
      title={etiqueta}
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={oscuro ? "claro" : "oscuro"}
          initial={{ opacity: 0, rotate: -90, scale: 0.7 }}
          animate={{ opacity: 1, rotate: 0, scale: 1 }}
          exit={{ opacity: 0, rotate: 90, scale: 0.7 }}
          transition={{ duration: 0.18 }}
        >
          {oscuro ? <Sun size={16} /> : <Moon size={16} />}
        </motion.span>
      </AnimatePresence>
      {!compacto && <span>{oscuro ? "Claro" : "Oscuro"}</span>}
    </motion.button>
  );
}
