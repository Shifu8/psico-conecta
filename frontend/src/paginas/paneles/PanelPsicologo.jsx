import {
  Activity,
  CalendarDays,
  Clock3,
  FileText,
  MessageSquareHeart,
  UsersRound,
  Video,
} from "lucide-react";
import BarraProgreso from "../../componentes/BarraProgreso";
import TarjetaModuloPanel from "../../componentes/TarjetaModuloPanel";
import EncabezadoPanel from "./EncabezadoPanel";

const modulos = [
  { titulo: "Próximas citas", texto: "Organiza tus próximos espacios de atención.", detalle: "Consulta tu agenda", icono: CalendarDays },
  { titulo: "Mis pacientes", texto: "Encuentra la información importante de cada proceso.", detalle: "Gestiona tus pacientes", icono: UsersRound },
  { titulo: "Sesiones virtuales", texto: "Accede a tus encuentros programados con comodidad.", detalle: "Revisa tus sesiones", icono: Video },
  { titulo: "Progreso emocional", texto: "Consulta el seguimiento para acompañar con continuidad.", detalle: "Observa la evolución", icono: Activity },
];

const indicadores = [
  { etiqueta: "Sesiones completadas", valor: 82, color: "from-blue-600 to-cyan-400" },
  { etiqueta: "Seguimientos al día", valor: 76, color: "from-indigo-600 to-violet-400" },
  { etiqueta: "Notas clínicas listas", valor: 68, color: "from-emerald-500 to-teal-400" },
];

const agenda = [
  { hora: "09:00", paciente: "Paciente Demo", tipo: "Sesión virtual" },
  { hora: "11:30", paciente: "Ana R.", tipo: "Seguimiento emocional" },
  { hora: "15:00", paciente: "Luis M.", tipo: "Primera entrevista" },
];

export default function PanelPsicologo() {
  return (
    <>
      <EncabezadoPanel
        etiqueta="Panel profesional"
        titulo="Tu atención, más organizada."
        texto="Encuentra tus herramientas de trabajo en un espacio diseñado para acompañar cada proceso con claridad."
      />
      <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {modulos.map((modulo) => <TarjetaModuloPanel key={modulo.titulo} {...modulo} />)}
      </section>

      <section className="mt-6 grid gap-5 lg:grid-cols-[.9fr_1.1fr]">
        <article className="overflow-hidden rounded-3xl bg-gradient-to-br from-blue-700 via-indigo-700 to-slate-950 p-6 text-white shadow-lg sm:p-8">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-blue-100">
            <Clock3 size={16} />
            Tu jornada
          </div>
          <h2 className="mt-3 text-2xl font-black">Acompaña cada cita con tranquilidad.</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-blue-100/85">
            Revisa tu agenda y mantén tus sesiones, pacientes y seguimientos en orden.
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {[
              ["Citas hoy", "3"],
              ["Pacientes activos", "18"],
              ["Notas pendientes", "4"],
            ].map(([titulo, valor]) => (
              <div key={titulo} className="rounded-2xl bg-white/12 p-4 backdrop-blur">
                <p className="text-xs font-bold text-blue-100">{titulo}</p>
                <p className="mt-2 text-2xl font-black">{valor}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="etiqueta">Indicadores</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">Ritmo de atención</h2>
            </div>
            <span className="icono-panel">
              <MessageSquareHeart size={22} />
            </span>
          </div>
          <div className="mt-6 space-y-4">
            {indicadores.map((item) => (
              <BarraProgreso key={item.etiqueta} {...item} />
            ))}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 lg:grid-cols-[1fr_.8fr]">
        <article className="panel overflow-hidden">
          <div className="border-b border-slate-100 px-5 py-5 dark:border-slate-800">
            <h2 className="text-lg font-black text-slate-900 dark:text-white">Agenda destacada</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">Tus próximos espacios de atención.</p>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {agenda.map((item) => (
              <div key={`${item.hora}-${item.paciente}`} className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="flex items-center gap-4">
                  <span className="rounded-2xl bg-blue-50 px-3 py-2 text-sm font-black text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
                    {item.hora}
                  </span>
                  <div>
                    <p className="font-black text-slate-900 dark:text-white">{item.paciente}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-300">{item.tipo}</p>
                  </div>
                </div>
                <Video size={18} className="text-slate-300 dark:text-slate-600" />
              </div>
            ))}
          </div>
        </article>

        <article className="panel p-6">
          <FileText size={23} className="text-blue-600 dark:text-blue-300" />
          <h2 className="mt-5 text-lg font-black text-slate-900 dark:text-white">Notas por completar</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-300">
            Mantén las observaciones al día para que cada proceso tenga continuidad.
          </p>
          <button type="button" className="boton-secundario mt-6 w-full">
            Revisar pendientes
          </button>
        </article>
      </section>
    </>
  );
}
