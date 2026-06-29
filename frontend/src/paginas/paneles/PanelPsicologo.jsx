import {
  Activity,
  AlertTriangle,
  BookOpenCheck,
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  Clock3,
  FileText,
  HeartPulse,
  NotebookPen,
  UserCheck,
  UsersRound,
  Video,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import BarraProgreso from "../../componentes/BarraProgreso";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import { obtenerDatosOperativos } from "../../servicios/servicioModulos";
import EncabezadoPanel from "./EncabezadoPanel";

const modulos = [
  { titulo: "Próximas citas", texto: "Organiza tus próximos espacios de atención.", detalle: "Consulta tu agenda", icono: CalendarDays, ruta: "/citas" },
  { titulo: "Mis pacientes", texto: "Encuentra la información importante de cada proceso.", detalle: "Gestiona tus pacientes", icono: UsersRound },
  { titulo: "Sesiones virtuales", texto: "Accede a tus encuentros programados con comodidad.", detalle: "Revisa tus sesiones", icono: Video },
  { titulo: "Progreso emocional", texto: "Consulta el seguimiento para acompañar con continuidad.", detalle: "Observa la evolución", icono: Activity },
];

const estado = (item) => String(item?.estado || item?.status || "pendiente").toLowerCase();
const fechaCita = (cita) => cita.fecha || cita.fecha_inicio || cita.inicio || cita.created_at || cita.creado_en;
const esCompletado = (valor) => ["completada", "completado", "atendida", "finalizada", "finalizado"].includes(valor);
const esCancelado = (valor) => ["cancelada", "cancelado", "anulada", "anulado"].includes(valor);
const esHoy = (valor) => {
  const fecha = new Date(valor);
  return !Number.isNaN(fecha.getTime()) && fecha.toDateString() === new Date().toDateString();
};
const esFuturo = (valor) => {
  const fecha = new Date(valor);
  return !Number.isNaN(fecha.getTime()) && fecha.getTime() >= Date.now();
};
const formatearFecha = (valor) => {
  if (!valor) return "Sin fecha";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return "Sin fecha";
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(fecha);
};
const formatearHora = (valor) => {
  if (!valor) return "--:--";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return "--:--";
  return new Intl.DateTimeFormat("es-EC", { hour: "2-digit", minute: "2-digit" }).format(fecha);
};

const ejercicios = [
  { titulo: "Respiración", detalle: "Asignar práctica breve de regulación", icono: HeartPulse },
  { titulo: "Bitácora", detalle: "Enviar registro de pensamientos", icono: NotebookPen },
  { titulo: "Reflexión", detalle: "Programar tarea terapéutica semanal", icono: BookOpenCheck },
];

export default function PanelPsicologo() {
  const { usuario } = usarAutenticacion();
  const [datos, setDatos] = useState({ citas: [], sesiones: [], emociones: [] });
  const [cargando, setCargando] = useState(true);
  const [errores, setErrores] = useState([]);

  useEffect(() => {
    let activo = true;
    obtenerDatosOperativos()
      .then((respuesta) => {
        if (!activo) return;
        setDatos(respuesta);
        setErrores(respuesta.errores || []);
      })
      .catch(() => setErrores(["citas", "teleconsulta", "iot"]))
      .finally(() => activo && setCargando(false));
    return () => {
      activo = false;
    };
  }, []);

  const citasProfesional = useMemo(
    () => datos.citas.filter((cita) => Number(cita.psicologo_id) === Number(usuario.id)),
    [datos.citas, usuario.id],
  );
  const idsPacientes = useMemo(() => [...new Set(citasProfesional.map((cita) => cita.paciente_id).filter(Boolean))], [citasProfesional]);
  const citasHoy = citasProfesional.filter((cita) => esHoy(fechaCita(cita)) && !esCancelado(estado(cita)));
  const proximasCitas = [...citasProfesional]
    .filter((cita) => esFuturo(fechaCita(cita)) && !esCancelado(estado(cita)))
    .sort((a, b) => new Date(fechaCita(a)) - new Date(fechaCita(b)));
  const proximaCita = proximasCitas[0];
  const citasCompletadas = citasProfesional.filter((cita) => esCompletado(estado(cita))).length;
  const notasPendientes = citasProfesional.filter((cita) => esCompletado(estado(cita)) && !cita.nota_cerrada).length;
  const sesionesProfesional = datos.sesiones.filter((sesion) => Number(sesion.psicologo_id) === Number(usuario.id) || citasProfesional.some((cita) => Number(cita.id) === Number(sesion.cita_id)));
  const emocionesPacientes = datos.emociones.filter((emocion) => idsPacientes.includes(emocion.paciente_id || emocion.usuario_id || emocion.user_id));

  const pacientes = idsPacientes.map((id) => {
    const citasPaciente = citasProfesional.filter((cita) => Number(cita.paciente_id) === Number(id));
    const ultima = [...citasPaciente].sort((a, b) => new Date(fechaCita(b) || 0) - new Date(fechaCita(a) || 0))[0];
    const proxima = citasPaciente.find((cita) => esFuturo(fechaCita(cita)) && !esCancelado(estado(cita)));
    const emocionesPaciente = emocionesPacientes.filter((emocion) => Number(emocion.paciente_id || emocion.usuario_id || emocion.user_id) === Number(id));
    return {
      id,
      nombre: `Paciente #${id}`,
      ultima: ultima ? formatearFecha(fechaCita(ultima)) : "Sin citas",
      proxima: proxima ? `${formatearFecha(fechaCita(proxima))} · ${formatearHora(fechaCita(proxima))}` : "Sin próxima cita",
      registros: emocionesPaciente.length,
    };
  });

  const indicadores = [
    { etiqueta: "Sesiones completadas", valor: citasProfesional.length ? Math.round((citasCompletadas / citasProfesional.length) * 100) : 0, color: "from-blue-600 to-cyan-400" },
    { etiqueta: "Seguimientos al día", valor: pacientes.length ? Math.round((pacientes.filter((p) => p.registros > 0).length / pacientes.length) * 100) : 0, color: "from-emerald-500 to-teal-400" },
    { etiqueta: "Notas clínicas listas", valor: citasCompletadas ? Math.round(((citasCompletadas - notasPendientes) / citasCompletadas) * 100) : 0, color: "from-violet-600 to-fuchsia-400" },
  ];

  const alertas = [
    { titulo: "Sin registro emocional", valor: Math.max(pacientes.length - pacientes.filter((p) => p.registros > 0).length, 0), icono: AlertTriangle },
    { titulo: "Citas perdidas", valor: citasProfesional.filter((cita) => estado(cita) === "perdida").length, icono: CalendarDays },
    { titulo: "Notas pendientes", valor: notasPendientes, icono: FileText },
  ];

  return (
    <>
      <EncabezadoPanel
        etiqueta="Panel profesional"
        titulo="Tu jornada clínica, organizada"
        texto="Citas, pacientes, seguimiento emocional, notas y teleconsulta solo para tu cartera de atención."
      />

      {errores.length > 0 && (
        <p className="mt-6 rounded-2xl bg-amber-50 p-3 text-sm font-semibold text-amber-800 dark:bg-amber-950/30 dark:text-amber-200">
          Algunos módulos aún no respondieron: {errores.join(", ")}.
        </p>
      )}

      <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Tarjeta titulo="Citas hoy" valor={citasHoy.length} detalle={proximaCita ? `Próxima ${formatearHora(fechaCita(proximaCita))}` : "Sin próxima sesión"} icono={Clock3} />
        <Tarjeta titulo="Pacientes" valor={pacientes.length} detalle="Asignados por citas" icono={UsersRound} />
        <Tarjeta titulo="Notas pendientes" valor={notasPendientes} detalle="Observaciones por cerrar" icono={FileText} />
        <Tarjeta titulo="Teleconsultas" valor={sesionesProfesional.length} detalle="Sesiones vinculadas" icono={Video} />
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[.95fr_1.05fr]">
        <article className="overflow-hidden rounded-3xl bg-gradient-to-br from-blue-700 via-indigo-700 to-slate-950 p-6 text-white shadow-lg sm:p-8">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-blue-100">
            <Clock3 size={16} /> Jornada de hoy
          </div>
          <h2 className="mt-3 text-2xl font-black">{proximaCita ? `Próxima sesión: ${formatearHora(fechaCita(proximaCita))}` : "Sin sesión inmediata"}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-blue-100/85">
            {proximaCita ? `Paciente #${proximaCita.paciente_id || "-"} · ${proximaCita.modalidad || proximaCita.tipo || "Sesión"}` : "Cuando se registren citas con tu ID, aparecerán aquí automáticamente."}
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <DatoClaro titulo="Citas hoy" valor={citasHoy.length} />
            <DatoClaro titulo="Pacientes activos" valor={pacientes.length} />
            <DatoClaro titulo="Notas pendientes" valor={notasPendientes} />
          </div>
        </article>

        <article className="panel p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="etiqueta">Indicadores</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">Ritmo de atención</h2>
            </div>
            <span className="icono-panel"><Activity size={22} /></span>
          </div>
          <div className="mt-6 space-y-4">
            {indicadores.map((item) => <BarraProgreso key={item.etiqueta} {...item} />)}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1fr_.85fr]">
        <article className="panel overflow-hidden">
          <CabeceraSeccion titulo="Agenda" texto="Citas próximas por hora, modalidad y estado." icono={CalendarDays} />
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {proximasCitas.slice(0, 6).map((cita) => (
              <div key={cita.id || fechaCita(cita)} className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="flex items-center gap-4">
                  <span className="rounded-2xl bg-blue-50 px-3 py-2 text-sm font-black text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">{formatearHora(fechaCita(cita))}</span>
                  <div>
                    <p className="font-black text-slate-900 dark:text-white">Paciente #{cita.paciente_id || "-"}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-300">{cita.modalidad || cita.tipo || "Sesión"} · {estado(cita)}</p>
                  </div>
                </div>
                <Video size={18} className="text-slate-300 dark:text-slate-600" />
              </div>
            ))}
            {!cargando && proximasCitas.length === 0 && <Vacio texto="No hay citas próximas asignadas a tu perfil." />}
          </div>
        </article>

        <article className="panel p-6">
          <CabeceraCompacta titulo="Alertas" etiqueta="Seguimiento" icono={AlertTriangle} />
          <div className="mt-5 space-y-3">
            {alertas.map(({ titulo, valor, icono: Icono }) => (
              <div key={titulo} className="flex items-center justify-between rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
                <div className="flex items-center gap-3">
                  <Icono size={18} className="text-amber-600 dark:text-amber-300" />
                  <p className="text-sm font-bold text-slate-700 dark:text-slate-200">{titulo}</p>
                </div>
                <p className="text-lg font-black text-slate-900 dark:text-white">{valor}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
        <article className="panel overflow-hidden">
          <CabeceraSeccion titulo="Mis pacientes" texto="Ficha básica, último seguimiento, próxima cita y registros emocionales." icono={UserCheck} />
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {pacientes.slice(0, 6).map((paciente) => (
              <div key={paciente.id} className="grid gap-3 px-5 py-4 sm:grid-cols-[1fr_auto] sm:items-center">
                <div>
                  <p className="font-black text-slate-900 dark:text-white">{paciente.nombre}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-300">Última: {paciente.ultima}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-300">Próxima: {paciente.proxima}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-black text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">{paciente.registros} registros</span>
                  <Link
                    to={`/psicologo/telemetria/${paciente.id}`}
                    title="Monitorear telemetría en tiempo real"
                    className="flex items-center justify-center p-2 rounded-xl bg-blue-50 text-blue-600 hover:bg-blue-100 transition dark:bg-blue-950/40 dark:text-blue-300 dark:hover:bg-blue-900/60"
                  >
                    <Activity size={16} />
                  </Link>
                </div>
              </div>
            ))}
            {!cargando && pacientes.length === 0 && <Vacio texto="No hay pacientes asignados por citas todavía." />}
          </div>
        </article>

        <article className="panel p-6">
          <CabeceraCompacta titulo="Notas clínicas" etiqueta="Solo psicólogos" icono={ClipboardList} />
          <p className="mt-4 text-sm leading-6 text-slate-500 dark:text-slate-300">Crea, edita y cierra observaciones de sesión cuando el módulo clínico quede conectado al backend.</p>
          <div className="mt-5 grid gap-3">
            <Dato titulo="Pendientes" valor={notasPendientes} />
            <Dato titulo="Sesiones cerradas" valor={Math.max(citasCompletadas - notasPendientes, 0)} />
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-3">
        <article className="panel p-6 xl:col-span-2">
          <CabeceraCompacta titulo="Seguimiento emocional" etiqueta="Evolución" icono={Activity} />
          <div className="mt-5 grid gap-3 sm:grid-cols-4">
            {["Ánimo", "Estrés", "Sueño", "Ansiedad"].map((item, indice) => (
              <div key={item} className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
                <p className="text-xs font-bold text-slate-500 dark:text-slate-300">{item}</p>
                <p className="mt-2 text-2xl font-black text-slate-900 dark:text-white">{emocionesPacientes.length ? `${Math.max(20, 78 - indice * 9)}%` : "0%"}</p>
              </div>
            ))}
          </div>
        </article>
        <article className="panel p-6">
          <CabeceraCompacta titulo="Tareas terapéuticas" etiqueta="Asignar" icono={CheckCircle2} />
          <div className="mt-5 space-y-3">
            {ejercicios.map(({ titulo, detalle, icono: Icono }) => (
              <div key={titulo} className="rounded-2xl border border-slate-100 p-4 dark:border-slate-800">
                <Icono size={18} className="text-blue-600 dark:text-blue-300" />
                <p className="mt-3 font-black text-slate-900 dark:text-white">{titulo}</p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">{detalle}</p>
              </div>
            ))}
          </div>
        </article>
      </section>
    </>
  );
}

function Tarjeta({ titulo, valor, detalle, icono: Icono }) {
  return (
    <article className="panel p-5">
      <span className="icono-panel"><Icono size={21} /></span>
      <p className="mt-5 text-3xl font-black text-slate-900 dark:text-white">{valor}</p>
      <p className="mt-1 text-sm font-bold text-slate-700 dark:text-slate-200">{titulo}</p>
      <p className="mt-1 text-xs text-slate-400">{detalle}</p>
    </article>
  );
}

function DatoClaro({ titulo, valor }) {
  return (
    <div className="rounded-2xl bg-white/12 p-4 backdrop-blur">
      <p className="text-xs font-bold text-blue-100">{titulo}</p>
      <p className="mt-2 text-2xl font-black">{valor}</p>
    </div>
  );
}

function Dato({ titulo, valor }) {
  return (
    <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
      <p className="text-2xl font-black text-slate-900 dark:text-white">{valor}</p>
      <p className="mt-1 text-xs font-bold text-slate-500 dark:text-slate-300">{titulo}</p>
    </div>
  );
}

function CabeceraSeccion({ titulo, texto, icono: Icono }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 px-5 py-5 dark:border-slate-800">
      <div>
        <h2 className="text-lg font-black text-slate-900 dark:text-white">{titulo}</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">{texto}</p>
      </div>
      <span className="icono-panel"><Icono size={21} /></span>
    </div>
  );
}

function CabeceraCompacta({ titulo, etiqueta, icono: Icono }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <p className="etiqueta">{etiqueta}</p>
        <h2 className="mt-2 text-lg font-black text-slate-900 dark:text-white">{titulo}</h2>
      </div>
      <span className="icono-panel"><Icono size={20} /></span>
    </div>
  );
}

function Vacio({ texto }) {
  return <p className="px-5 py-8 text-sm text-slate-400">{texto}</p>;
}