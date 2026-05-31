import { Activity, CalendarDays, Clock3, UsersRound, Video } from "lucide-react";
import TarjetaModuloPanel from "../../componentes/TarjetaModuloPanel";
import EncabezadoPanel from "./EncabezadoPanel";

const modulos = [
  { titulo: "Próximas citas", texto: "Organiza tus próximos espacios de atención.", detalle: "Consulta tu agenda", icono: CalendarDays },
  { titulo: "Mis pacientes", texto: "Encuentra la información importante de cada proceso.", detalle: "Gestiona tus pacientes", icono: UsersRound },
  { titulo: "Sesiones virtuales", texto: "Accede a tus encuentros programados con comodidad.", detalle: "Revisa tus sesiones", icono: Video },
  { titulo: "Progreso emocional", texto: "Consulta el seguimiento para acompañar con continuidad.", detalle: "Observa la evolución", icono: Activity },
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
      <section className="mt-6 overflow-hidden rounded-3xl bg-gradient-to-r from-blue-700 to-indigo-700 p-6 text-white shadow-lg sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-blue-100">
              <Clock3 size={16} />
              Tu jornada
            </div>
            <h2 className="mt-3 text-2xl font-black">Acompaña cada cita con tranquilidad.</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-blue-100/85">
              Revisa tu agenda y mantén tus sesiones, pacientes y seguimientos en orden.
            </p>
          </div>
          <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-white/15">
            <CalendarDays size={28} />
          </span>
        </div>
      </section>
    </>
  );
}
