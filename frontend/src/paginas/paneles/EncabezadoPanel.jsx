export default function EncabezadoPanel({ etiqueta, titulo, texto }) {
  return (
    <header>
      <p className="etiqueta">{etiqueta}</p>
      <h1 className="mt-3 text-3xl font-black tracking-tight text-slate-900 dark:text-white sm:text-4xl">
        {titulo}
      </h1>
      <p className="mt-3 max-w-3xl leading-7 text-slate-600 dark:text-slate-300">{texto}</p>
    </header>
  );
}
