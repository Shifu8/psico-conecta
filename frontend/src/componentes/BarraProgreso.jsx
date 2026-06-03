export default function BarraProgreso({
  etiqueta,
  valor,
  total = 100,
  color = "from-blue-500 to-cyan-400",
}) {
  const porcentaje = total > 0 ? Math.min(100, Math.round((valor / total) * 100)) : 0;

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3 text-xs font-bold">
        <span className="text-slate-600 dark:text-slate-300">{etiqueta}</span>
        <span className="text-slate-400">{porcentaje}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color}`}
          style={{ width: `${porcentaje}%` }}
        />
      </div>
    </div>
  );
}
