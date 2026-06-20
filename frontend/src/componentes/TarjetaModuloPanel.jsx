import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function TarjetaModuloPanel({ icono: Icono, titulo, texto, detalle, ruta }) {
  const content = (
    <motion.article
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      className="panel group h-full p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <span className="icono-panel transition duration-300 group-hover:bg-blue-600 group-hover:text-white">
          <Icono size={22} />
        </span>
        {ruta && <ArrowUpRight size={18} className="text-slate-300 transition group-hover:text-blue-600 dark:text-slate-600 dark:group-hover:text-blue-300" />}
      </div>
      <h2 className="mt-6 text-lg font-black text-slate-900 dark:text-white">{titulo}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-300">{texto}</p>
      {detalle && (
        <p className="mt-5 border-t border-slate-100 pt-4 text-xs font-bold text-blue-600 dark:border-slate-800 dark:text-blue-300">
          {detalle}
        </p>
      )}
    </motion.article>
  );

  if (ruta) {
    return <Link to={ruta} className="block h-full">{content}</Link>;
  }
  return content;
}
