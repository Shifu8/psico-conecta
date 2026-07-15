const estilos = {
  PAGADO: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200",
  REEMBOLSO_PARCIAL: "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-200",
  REEMBOLSADO: "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-100",
  CHECKOUT_ABIERTO: "bg-blue-100 text-blue-800 dark:bg-blue-950/50 dark:text-blue-200",
  PROCESANDO: "bg-violet-100 text-violet-800 dark:bg-violet-950/50 dark:text-violet-200",
  PENDIENTE: "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-200",
  FALLIDO: "bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-200",
  EXPIRADO: "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-100",
  CANCELADO: "bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-200",
  REEMBOLSO_PENDIENTE: "bg-violet-100 text-violet-800 dark:bg-violet-950/50 dark:text-violet-200",
  REPROGRAMACION_PENDIENTE: "bg-blue-100 text-blue-800 dark:bg-blue-950/50 dark:text-blue-200",
  DISPUTADO: "bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-200",
};

const etiquetas = {
  CHECKOUT_ABIERTO: "Pago iniciado",
  REEMBOLSO_PARCIAL: "Reembolso parcial",
  REEMBOLSO_PENDIENTE: "Reembolso en proceso",
  REPROGRAMACION_PENDIENTE: "Cita reprogramándose",
};

export default function EstadoPago({ estado }) {
  const valor = String(estado || "PENDIENTE").toUpperCase();
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-black ${estilos[valor] || estilos.PENDIENTE}`}>
      {etiquetas[valor] || valor.replaceAll("_", " ").toLowerCase()}
    </span>
  );
}
