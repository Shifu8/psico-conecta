import {
  Activity,
  CalendarDays,
  CheckCircle2,
  CreditCard,
  HeartHandshake,
  Smile,
  Sparkles,
  Video,
} from "lucide-react";
import BarraProgreso from "../../componentes/BarraProgreso";
import TarjetaModuloPanel from "../../componentes/TarjetaModuloPanel";
import EncabezadoPanel from "./EncabezadoPanel";

const modulos = [
  { titulo: "Mi próxima cita", texto: "Revisa y organiza tus próximos espacios de atención.", detalle: "Consulta tu agenda", icono: CalendarDays },
  { titulo: "Sesión virtual", texto: "Ingresa a tus encuentros programados desde un solo lugar.", detalle: "Revisa tus sesiones", icono: Video },
  { titulo: "Mi bienestar", texto: "Mantén un seguimiento cercano de tu proceso emocional.", detalle: "Registra cómo te sientes", icono: Activity },
  { titulo: "Mis pagos", texto: "Consulta la información económica de tu atención con claridad.", detalle: "Revisa tus pagos", icono: CreditCard },
];

const habitos = [
  { etiqueta: "Registro emocional", valor: 72, color: "from-cyan-500 to-blue-500" },
  { etiqueta: "Asistencia a sesiones", valor: 88, color: "from-emerald-500 to-teal-400" },
  { etiqueta: "Tareas terapéuticas", valor: 64, color: "from-indigo-500 to-violet-500" },
];

const agenda = [
  { dia: "Hoy", titulo: "Respiración guiada", detalle: "5 minutos para bajar el ritmo" },
  { dia: "Vie", titulo: "Sesión de seguimiento", detalle: "Videollamada programada" },
  { dia: "Dom", titulo: "Bitácora emocional", detalle: "Registrar estado de ánimo" },
];

export default function PanelPaciente() {
  return (
    <>
      <EncabezadoPanel
        etiqueta="Mi bienestar"
        titulo="Un espacio para avanzar a tu ritmo."
        texto="Encuentra tus citas, sesiones y herramientas personales para mantener tu proceso organizado."
      />
      <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {modulos.map((modulo) => <TarjetaModuloPanel key={modulo.titulo} {...modulo} />)}
      </section>

      <section className="mt-6 grid gap-5 lg:grid-cols-[1fr_.9fr]">
        <article className="overflow-hidden rounded-3xl bg-gradient-to-br from-cyan-600 via-blue-700 to-indigo-700 p-6 text-white shadow-lg sm:p-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-100">Tu proceso importa</p>
              <h2 className="mt-3 text-2xl font-black">Pequeños pasos también son avances.</h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-cyan-50/90">
                Mantén tu seguimiento al día y encuentra la información de tu atención cuando la necesites.
              </p>
            </div>
            <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-white/15">
              <HeartHandshake size={29} />
            </span>
          </div>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {[
              ["Próxima sesión", "Viernes 10:30"],
              ["Estado promedio", "Estable"],
              ["Avance semanal", "72%"],
            ].map(([titulo, valor]) => (
              <div key={titulo} className="rounded-2xl bg-white/12 p-4 backdrop-blur">
                <p className="text-xs font-bold text-cyan-100">{titulo}</p>
                <p className="mt-2 text-lg font-black">{valor}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="etiqueta">Bienestar</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">Seguimiento semanal</h2>
            </div>
            <span className="icono-panel">
              <Smile size={22} />
            </span>
          </div>
          <div className="mt-6 space-y-4">
            {habitos.map((item) => (
              <BarraProgreso key={item.etiqueta} {...item} />
            ))}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 lg:grid-cols-3">
        {agenda.map((item) => (
          <article key={item.titulo} className="panel p-5">
            <div className="flex items-start justify-between gap-4">
              <span className="rounded-2xl bg-blue-50 px-3 py-2 text-xs font-black text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
                {item.dia}
              </span>
              <CheckCircle2 size={19} className="text-emerald-500" />
            </div>
            <h3 className="mt-5 font-black text-slate-900 dark:text-white">{item.titulo}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-300">{item.detalle}</p>
          </article>
        ))}
        <article className="panel bg-gradient-to-br from-white to-blue-50 p-5 dark:from-slate-900 dark:to-blue-950/30">
          <Sparkles size={22} className="text-blue-600 dark:text-blue-300" />
          <h3 className="mt-5 font-black text-slate-900 dark:text-white">Consejo del día</h3>
          <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-300">
            Reserva un momento breve para escribir cómo te sientes y qué necesitas hoy.
          </p>
        </article>
      </section>
    </>
  );
}
