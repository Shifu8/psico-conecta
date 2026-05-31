import { Activity, CalendarDays, CreditCard, HeartHandshake, Video } from "lucide-react";
import TarjetaModuloPanel from "../../componentes/TarjetaModuloPanel";
import EncabezadoPanel from "./EncabezadoPanel";

const modulos = [
  { titulo: "Mi próxima cita", texto: "Revisa y organiza tus próximos espacios de atención.", detalle: "Consulta tu agenda", icono: CalendarDays },
  { titulo: "Sesión virtual", texto: "Ingresa a tus encuentros programados desde un solo lugar.", detalle: "Revisa tus sesiones", icono: Video },
  { titulo: "Mi bienestar", texto: "Mantén un seguimiento cercano de tu proceso emocional.", detalle: "Registra cómo te sientes", icono: Activity },
  { titulo: "Mis pagos", texto: "Consulta la información económica de tu atención con claridad.", detalle: "Revisa tus pagos", icono: CreditCard },
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
      <section className="mt-6 overflow-hidden rounded-3xl bg-gradient-to-r from-cyan-600 to-blue-700 p-6 text-white shadow-lg sm:p-8">
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
      </section>
    </>
  );
}
