import {
  Activity,
  CalendarDays,
  CheckCircle2,
  CreditCard,
  HeartHandshake,
  HeartPulse,
  LockKeyhole,
  Moon,
  NotebookPen,
  Save,
  Smile,
  Sparkles,
  Video,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import BarraProgreso from "../../componentes/BarraProgreso";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import { crearRegistroEmocional, obtenerDatosOperativos } from "../../servicios/servicioModulos";
import EncabezadoPanel from "./EncabezadoPanel";

const estado = (item) => String(item?.estado || item?.status || "pendiente").toLowerCase();
const fechaCita = (cita) => cita.fecha || cita.fecha_inicio || cita.inicio || cita.created_at || cita.creado_en;
const esCancelado = (valor) => ["cancelada", "cancelado", "anulada", "anulado"].includes(valor);
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

const tareas = [
  { dia: "Hoy", titulo: "Respiración guiada", detalle: "5 minutos para bajar el ritmo", icono: HeartPulse },
  { dia: "Vie", titulo: "Bitácora emocional", detalle: "Registrar estado de ánimo", icono: NotebookPen },
  { dia: "Dom", titulo: "Higiene del sueño", detalle: "Rutina breve antes de dormir", icono: Moon },
];

const opcionesAnimo = ["Muy bien", "Bien", "Regular", "Cargado", "Difícil"];

export default function PanelPaciente() {
  const { usuario } = usarAutenticacion();
  const [datos, setDatos] = useState({ citas: [], sesiones: [], pagos: [], emociones: [], lecturasIot: [] });
  const [formulario, setFormulario] = useState({ estado_animo: "Bien", estres: 4, sueno: 7, ansiedad: 3, nota: "" });
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [errores, setErrores] = useState([]);

  useEffect(() => {
    let activo = true;
    obtenerDatosOperativos()
      .then((respuesta) => {
        if (!activo) return;
        setDatos(respuesta);
        setErrores(respuesta.errores || []);
      })
      .catch(() => setErrores(["citas", "pagos", "teleconsulta", "iot"]))
      .finally(() => activo && setCargando(false));
    return () => {
      activo = false;
    };
  }, []);

  const citasPaciente = useMemo(
    () => datos.citas.filter((cita) => Number(cita.paciente_id || cita.usuario_id || cita.user_id) === Number(usuario.id)),
    [datos.citas, usuario.id],
  );
  const citasProximas = [...citasPaciente]
    .filter((cita) => esFuturo(fechaCita(cita)) && !esCancelado(estado(cita)))
    .sort((a, b) => new Date(fechaCita(a)) - new Date(fechaCita(b)));
  const citasPasadas = [...citasPaciente]
    .filter((cita) => !esFuturo(fechaCita(cita)))
    .sort((a, b) => new Date(fechaCita(b) || 0) - new Date(fechaCita(a) || 0));
  const proximaCita = citasProximas[0];
  const emocionesPaciente = datos.emociones.filter((emocion) => Number(emocion.paciente_id || emocion.usuario_id || emocion.user_id) === Number(usuario.id));
  const pagosPaciente = datos.pagos.filter((pago) => Number(pago.usuario_id || pago.user_id || pago.paciente_id) === Number(usuario.id));
  const lecturasPaciente = datos.lecturasIot.filter((lectura) => Number(lectura.usuario_id || lectura.user_id || lectura.paciente_id) === Number(usuario.id));
  const sesionesPaciente = datos.sesiones.filter((sesion) => citasPaciente.some((cita) => Number(cita.id) === Number(sesion.cita_id)) || Number(sesion.paciente_id) === Number(usuario.id));
  const sesionDisponible = sesionesPaciente.find((sesion) => ["pendiente", "programada", "confirmada"].includes(estado(sesion)));
  const ultimaLectura = lecturasPaciente[lecturasPaciente.length - 1];
  const ultimoRegistro = emocionesPaciente[emocionesPaciente.length - 1];
  const pagosPendientes = pagosPaciente.filter((pago) => ["pendiente", "simulado"].includes(estado(pago))).length;

  const guardarRegistro = async (evento) => {
    evento.preventDefault();
    setGuardando(true);
    setMensaje("");
    setError("");
    try {
      const payload = {
        ...formulario,
        paciente_id: usuario.id,
        usuario_id: usuario.id,
        fecha: new Date().toISOString(),
      };
      const { data } = await crearRegistroEmocional(payload);
      setDatos((actual) => ({ ...actual, emociones: [...actual.emociones, data.emocion || payload] }));
      setFormulario((actual) => ({ ...actual, nota: "" }));
      setMensaje("Registro emocional guardado.");
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible guardar el registro emocional.");
    } finally {
      setGuardando(false);
    }
  };

  const progreso = [
    { etiqueta: "Registro emocional", valor: Math.min(emocionesPaciente.length * 14, 100), color: "from-cyan-500 to-blue-500" },
    { etiqueta: "Asistencia a sesiones", valor: citasPaciente.length ? Math.round((citasPasadas.filter((cita) => estado(cita) !== "perdida").length / citasPaciente.length) * 100) : 0, color: "from-emerald-500 to-teal-400" },
    { etiqueta: "Tareas terapéuticas", valor: tareas.length ? 66 : 0, color: "from-violet-600 to-fuchsia-400" },
  ];

  const consejo = Number((ultimoRegistro || formulario).estres || 0) >= 7
    ? "Hoy conviene bajar el ritmo: respiración lenta, agua y una pausa breve antes de seguir."
    : "Reserva un momento breve para escribir cómo te sientes y qué necesitas hoy.";

  return (
    <>
      <EncabezadoPanel
        etiqueta="Mi bienestar"
        titulo="Un espacio para avanzar a tu ritmo"
        texto="Citas, sesión virtual, registro emocional, tareas, pagos y privacidad en un solo lugar."
      />

      {errores.length > 0 && (
        <p className="mt-6 rounded-2xl bg-amber-50 p-3 text-sm font-semibold text-amber-800 dark:bg-amber-950/30 dark:text-amber-200">
          Algunos módulos aún no respondieron: {errores.join(", ")}.
        </p>
      )}

      <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Tarjeta titulo="Próxima cita" valor={proximaCita ? formatearHora(fechaCita(proximaCita)) : "Sin cita"} detalle={proximaCita ? `${formatearFecha(fechaCita(proximaCita))} · Psicólogo #${proximaCita.psicologo_id || "-"}` : "Aún no hay agenda"} icono={CalendarDays} />
        <Tarjeta titulo="Sesión virtual" valor={sesionDisponible ? "Lista" : "Pendiente"} detalle={sesionDisponible?.enlace_acceso ? "Enlace disponible" : "Sin enlace activo"} icono={Video} />
        <Tarjeta titulo="Registro emocional" valor={emocionesPaciente.length} detalle="Entradas personales" icono={Activity} />
        <Tarjeta titulo="Pagos" valor={pagosPendientes} detalle="Pendientes" icono={CreditCard} />
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1fr_.9fr]">
        <article className="overflow-hidden rounded-3xl bg-gradient-to-br from-cyan-600 via-blue-700 to-indigo-700 p-6 text-white shadow-lg sm:p-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-100">Próxima cita</p>
              <h2 className="mt-3 text-2xl font-black">{proximaCita ? `${formatearFecha(fechaCita(proximaCita))} · ${formatearHora(fechaCita(proximaCita))}` : "Tu agenda está libre"}</h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-cyan-50/90">
                {proximaCita ? `Psicólogo #${proximaCita.psicologo_id || "-"} · ${proximaCita.modalidad || proximaCita.tipo || "Sesión"} · ${estado(proximaCita)}` : "Cuando se cree una cita con tu perfil, aparecerá aquí con su modalidad y estado."}
              </p>
            </div>
            <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-white/15"><HeartHandshake size={29} /></span>
          </div>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <DatoClaro titulo="Próximas" valor={citasProximas.length} />
            <DatoClaro titulo="Pagos pendientes" valor={pagosPendientes} />
            <DatoClaro titulo="Registros" valor={emocionesPaciente.length} />
          </div>
        </article>

        <article className="panel p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="etiqueta">Bienestar</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">Mi progreso</h2>
            </div>
            <span className="icono-panel"><Smile size={22} /></span>
          </div>
          <div className="mt-6 space-y-4">
            {progreso.map((item) => <BarraProgreso key={item.etiqueta} {...item} />)}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[.95fr_1.05fr]">
        <form onSubmit={guardarRegistro} className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="etiqueta">Registro emocional</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">¿Cómo me siento hoy?</h2>
            </div>
            <span className="icono-panel"><Activity size={22} /></span>
          </div>
          {(mensaje || error) && <p className={`mt-5 rounded-2xl p-3 text-sm font-semibold ${error ? "bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-200" : "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-200"}`}>{error || mensaje}</p>}
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <label>
              <span className="text-xs font-black uppercase tracking-wider text-slate-400">Estado de ánimo</span>
              <select className="campo mt-2" value={formulario.estado_animo} onChange={(e) => setFormulario((actual) => ({ ...actual, estado_animo: e.target.value }))}>
                {opcionesAnimo.map((opcion) => <option key={opcion}>{opcion}</option>)}
              </select>
            </label>
            <ControlNumero etiqueta="Estrés" valor={formulario.estres} onChange={(valor) => setFormulario((actual) => ({ ...actual, estres: valor }))} />
            <ControlNumero etiqueta="Sueño" valor={formulario.sueno} onChange={(valor) => setFormulario((actual) => ({ ...actual, sueno: valor }))} />
            <ControlNumero etiqueta="Ansiedad" valor={formulario.ansiedad} onChange={(valor) => setFormulario((actual) => ({ ...actual, ansiedad: valor }))} />
          </div>
          <label className="mt-4 block">
            <span className="text-xs font-black uppercase tracking-wider text-slate-400">Nota personal</span>
            <textarea className="campo mt-2 min-h-28 resize-y" value={formulario.nota} onChange={(e) => setFormulario((actual) => ({ ...actual, nota: e.target.value }))} maxLength={500} placeholder="Opcional" />
          </label>
          <button type="submit" className="boton-primario mt-5 w-full" disabled={guardando}>
            <Save size={17} /> {guardando ? "Guardando..." : "Guardar registro"}
          </button>
        </form>

        <article className="panel overflow-hidden">
          <CabeceraSeccion titulo="Mi agenda" texto="Citas próximas, pasadas y estado de cada una." icono={CalendarDays} />
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {[...citasProximas, ...citasPasadas].slice(0, 6).map((cita) => (
              <div key={cita.id || fechaCita(cita)} className="flex items-center justify-between gap-4 px-5 py-4">
                <div>
                  <p className="font-black text-slate-900 dark:text-white">{formatearFecha(fechaCita(cita))} · {formatearHora(fechaCita(cita))}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-300">Psicólogo #{cita.psicologo_id || "-"} · {cita.modalidad || cita.tipo || "Sesión"}</p>
                </div>
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-black text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">{estado(cita)}</span>
              </div>
            ))}
            {!cargando && citasPaciente.length === 0 && <p className="px-5 py-8 text-sm text-slate-400">No tienes citas registradas todavía.</p>}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-3">
        <article className="panel p-6">
          <CabeceraCompacta titulo="Tareas asignadas" etiqueta="Actividades" icono={CheckCircle2} />
          <div className="mt-5 space-y-3">
            {tareas.map(({ dia, titulo, detalle, icono: Icono }) => (
              <div key={titulo} className="rounded-2xl border border-slate-100 p-4 dark:border-slate-800">
                <div className="flex items-start justify-between gap-4">
                  <span className="rounded-2xl bg-blue-50 px-3 py-2 text-xs font-black text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">{dia}</span>
                  <Icono size={18} className="text-emerald-500" />
                </div>
                <h3 className="mt-4 font-black text-slate-900 dark:text-white">{titulo}</h3>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">{detalle}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel p-6">
          <CabeceraCompacta titulo="Pagos" etiqueta="Estado" icono={CreditCard} />
          <div className="mt-5 grid gap-3">
            <Dato titulo="Pendientes" valor={pagosPendientes} />
            <Dato titulo="Historial" valor={pagosPaciente.length} />
            <Dato titulo="Comprobantes" valor={pagosPaciente.filter((pago) => pago.url_comprobante).length} />
          </div>
        </article>

        <article className="panel p-6">
          <CabeceraCompacta titulo="Consejo personalizado" etiqueta="Hoy" icono={Sparkles} />
          <p className="mt-5 text-sm leading-6 text-slate-500 dark:text-slate-300">{consejo}</p>
          <div className="mt-5 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Último registro</p>
            <p className="mt-2 text-lg font-black text-slate-900 dark:text-white">{ultimoRegistro?.estado_animo || "Sin registro"}</p>
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[.9fr_1.1fr]">
        <article className="panel p-6">
          <CabeceraCompacta titulo="Lecturas IoT" etiqueta="Apoyo" icono={HeartPulse} />
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <Dato titulo="Pulso" valor={ultimaLectura?.pulso || ultimaLectura?.heart_rate || "--"} />
            <Dato titulo="SpO2" valor={ultimaLectura?.spo2 || ultimaLectura?.oxigeno || "--"} />
            <Dato titulo="Lecturas" valor={lecturasPaciente.length} />
            <Dato titulo="Última" valor={ultimaLectura ? formatearFecha(ultimaLectura.fecha || ultimaLectura.created_at || ultimaLectura.creado_en) : "Sin datos"} />
          </div>
        </article>

        <article className="panel p-6">
          <CabeceraCompacta titulo="Privacidad" etiqueta="Datos compartidos" icono={LockKeyhole} />
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {[
              "Datos básicos del perfil",
              "Agenda de citas y asistencia",
              "Registros emocionales enviados",
              "Lecturas IoT como apoyo, no diagnóstico",
            ].map((item) => (
              <div key={item} className="flex items-center gap-3 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
                <CheckCircle2 size={18} className="text-emerald-500" />
                <p className="text-sm font-bold text-slate-700 dark:text-slate-200">{item}</p>
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
      <p className="mt-5 text-2xl font-black text-slate-900 dark:text-white">{valor}</p>
      <p className="mt-1 text-sm font-bold text-slate-700 dark:text-slate-200">{titulo}</p>
      <p className="mt-1 text-xs text-slate-400">{detalle}</p>
    </article>
  );
}

function ControlNumero({ etiqueta, valor, onChange }) {
  return (
    <label>
      <span className="text-xs font-black uppercase tracking-wider text-slate-400">{etiqueta}: {valor}/10</span>
      <input type="range" min="0" max="10" value={valor} onChange={(e) => onChange(Number(e.target.value))} className="mt-4 w-full accent-blue-600" />
    </label>
  );
}

function DatoClaro({ titulo, valor }) {
  return (
    <div className="rounded-2xl bg-white/12 p-4 backdrop-blur">
      <p className="text-xs font-bold text-cyan-100">{titulo}</p>
      <p className="mt-2 text-xl font-black">{valor}</p>
    </div>
  );
}

function Dato({ titulo, valor }) {
  return (
    <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
      <p className="text-xl font-black text-slate-900 dark:text-white">{valor}</p>
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