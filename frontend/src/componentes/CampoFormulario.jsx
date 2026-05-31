export default function CampoFormulario({
  etiqueta,
  error,
  ayuda,
  className = "",
  ...propiedades
}) {
  return (
    <label className={`block space-y-2 ${className}`}>
      <span className="text-sm font-bold text-slate-700 dark:text-slate-200">
        {etiqueta}
      </span>
      <input
        className={`campo ${error ? "border-red-400 focus:border-red-500 focus:ring-red-500/10" : ""}`}
        aria-invalid={Boolean(error)}
        {...propiedades}
      />
      {ayuda && !error && <span className="block text-xs text-slate-400">{ayuda}</span>}
      {error && <span className="block text-xs font-semibold text-red-600 dark:text-red-300">{error}</span>}
    </label>
  );
}
