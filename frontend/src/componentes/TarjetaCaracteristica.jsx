import { motion } from "framer-motion";

export default function TarjetaCaracteristica({ icono: Icono, titulo, texto, demora = 0 }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      whileHover={{ y: -6 }}
      transition={{ duration: 0.35, delay: demora }}
      className="panel h-full p-6"
    >
      <span className="icono-panel">
        <Icono size={23} />
      </span>
      <h3 className="mt-5 text-lg font-black text-slate-900 dark:text-white">{titulo}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{texto}</p>
    </motion.article>
  );
}
