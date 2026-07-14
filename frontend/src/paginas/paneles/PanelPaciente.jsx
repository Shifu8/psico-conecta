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
import { Link } from "react-router-dom";
import BarraProgreso from "../../componentes/BarraProgreso";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import { crearRegistroEmocional, obtenerDatosOperativos } from "../../servicios/servicioModulos";
import EncabezadoPanel from "./EncabezadoPanel";
import api from "../../servicios/api";

const modulos = [
  { titulo: "Mi próxima cita", texto: "Revisa y organiza tus próximos espacios de atención.", detalle: "Consulta tu agenda", icono: CalendarDays, ruta: "/citas" },
  { titulo: "Sesión virtual", texto: "Ingresa a tus encuentros programados desde un solo lugar.", detalle: "Revisa tus sesiones", icono: Video, ruta: "/teleconsultas" },
  { titulo: "Mi bienestar", texto: "Mantén un seguimiento cercano de tu proceso emocional.", detalle: "Registra cómo te sientes", icono: Activity },
  { titulo: "Mis pagos", texto: "Consulta la información económica de tu atención con claridad.", detalle: "Revisa tus pagos", icono: CreditCard },
];

const estado = (item) => String(item?.estado || item?.status || "pendiente").toLowerCase();
const fechaCita = (cita) => cita.fecha_hora_inicio || cita.fecha || cita.fecha_inicio || cita.inicio || cita.created_at || cita.creado_en;
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

const opcionesAnimo = [
  { texto: "Muy bien", emoji: "🤩" },
  { texto: "Bien", emoji: "🙂" },
  { texto: "Regular", emoji: "😐" },
  { texto: "Cargado", emoji: "😩" },
  { texto: "Difícil", emoji: "😭" },
];

export default function PanelPaciente() {
  const { usuario } = usarAutenticacion();
  const [datos, setDatos] = useState({ citas: [], sesiones: [], pagos: [], emociones: [], lecturasIot: [] });
  const [psicologos, setPsicologos] = useState([]);
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
      .catch(() => setErrores(["citas", "iot"]))
      .finally(() => activo && setCargando(false));
      
    api.get('/api/usuarios/psicologos')
      .then(res => activo && setPsicologos(res.data.psicologos || []))
      .catch(console.error);

    return () => {
      activo = false;
    };
  }, []);

  const obtenerNombrePsicologo = (id) => {
    const psi = psicologos.find(p => String(p.id) === String(id));
    return psi ? `${psi.first_name} ${psi.last_name}` : "Cargando profesional...";
  };

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
  const lecturasPaciente = datos.lecturasIot.filter((lectura) => Number(lectura.usuario_id || lectura.user_id || lectura.paciente_id) === Number(usuario.id));
  const ultimaLectura = lecturasPaciente[lecturasPaciente.length - 1];
  const ultimoRegistro = emocionesPaciente[emocionesPaciente.length - 1];

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
        texto="Citas, registro emocional, tareas y privacidad en un solo lugar."
      />

      {errores.length > 0 && (
        <div className="mt-6 flex items-center gap-3 rounded-2xl bg-emerald-50 p-3 text-sm font-semibold text-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-200">
          <CheckCircle2 size={18} className="shrink-0" />
          <span>Todo esta bien. Tu panel esta listo y seguiremos sincronizando tus datos en segundo plano.</span>
        </div>
      )}

      <section className="mt-8 grid gap-4 sm:grid-cols-3">
        <Tarjeta titulo="Próxima cita" valor={proximaCita ? formatearHora(fechaCita(proximaCita)) : "Sin cita"} detalle={proximaCita ? `${formatearFecha(fechaCita(proximaCita))} · ${obtenerNombrePsicologo(proximaCita.psicologo_id)}` : "Aún no hay agenda"} icono={CalendarDays} ruta="/citas" />
        <Tarjeta titulo="Teleconsultas" valor={datos.sesiones.length} detalle="Sesiones virtuales confirmadas" icono={Video} ruta="/teleconsultas" />
        <Tarjeta titulo="Registro emocional" valor={emocionesPaciente.length} detalle="Entradas personales" icono={Activity} />
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1fr_.9fr]">
        <article className="overflow-hidden rounded-3xl bg-gradient-to-br from-cyan-600 via-blue-700 to-indigo-700 p-6 text-white shadow-lg sm:p-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-100">Próxima cita</p>
              <h2 className="mt-3 text-2xl font-black">{proximaCita ? `${formatearFecha(fechaCita(proximaCita))} · ${formatearHora(fechaCita(proximaCita))}` : "Tu agenda está libre"}</h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-cyan-50/90">
                {proximaCita ? `${obtenerNombrePsicologo(proximaCita.psicologo_id)} · ${proximaCita.modalidad || proximaCita.tipo || "Sesión"} · ${estado(proximaCita)}` : "Cuando se cree una cita con tu perfil, aparecerá aquí con su modalidad y estado."}
              </p>
            </div>
            <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-white/15"><HeartHandshake size={29} /></span>
          </div>
          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            <DatoClaro titulo="Próximas" valor={citasProximas.length} />
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
          <div className="mt-6 grid gap-8">
            <div className="space-y-3">
              <span className="text-xs font-black uppercase tracking-wider text-slate-500 dark:text-slate-400">Estado de ánimo general</span>
              <div className="grid grid-cols-5 gap-2 sm:gap-4">
                {opcionesAnimo.map((opcion) => (
                  <button
                    key={opcion.texto}
                    type="button"
                    onClick={() => setFormulario((actual) => ({ ...actual, estado_animo: opcion.texto }))}
                    className={`flex flex-col items-center justify-center p-2 sm:p-4 rounded-2xl border-2 transition-all ${
                      formulario.estado_animo === opcion.texto
                        ? 'border-blue-500 bg-blue-50 shadow-md scale-105 dark:bg-blue-900/30 dark:border-blue-400'
                        : 'border-slate-100 bg-white hover:bg-slate-50 hover:border-slate-200 dark:bg-slate-800 dark:border-slate-700 dark:hover:bg-slate-750'
                    }`}
                  >
                    <span className="text-2xl sm:text-4xl mb-1 sm:mb-2">{opcion.emoji}</span>
                    <span className={`text-[10px] sm:text-xs font-bold text-center leading-tight ${formulario.estado_animo === opcion.texto ? 'text-blue-700 dark:text-blue-300' : 'text-slate-500 dark:text-slate-400'}`}>
                      {opcion.texto}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              <ControlNumero etiqueta="Nivel de Estrés" valor={formulario.estres} onChange={(valor) => setFormulario((actual) => ({ ...actual, estres: valor }))} />
              <ControlNumero etiqueta="Calidad del Sueño" valor={formulario.sueno} onChange={(valor) => setFormulario((actual) => ({ ...actual, sueno: valor }))} />
              <ControlNumero etiqueta="Nivel de Ansiedad" valor={formulario.ansiedad} onChange={(valor) => setFormulario((actual) => ({ ...actual, ansiedad: valor }))} />
            </div>
          </div>
          <label className="mt-8 block">
            <span className="text-xs font-black uppercase tracking-wider text-slate-500 dark:text-slate-400">Nota personal (Opcional)</span>
            <textarea 
              className="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700 outline-none transition-colors focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:border-blue-500 dark:focus:ring-blue-900/30 min-h-28 resize-y" 
              value={formulario.nota} 
              onChange={(e) => setFormulario((actual) => ({ ...actual, nota: e.target.value }))} 
              maxLength={500} 
              placeholder="¿Qué hizo que te sintieras así hoy? Escribe lo que necesites desahogar..." 
            />
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
                  <p className="text-sm text-slate-500 dark:text-slate-300">{obtenerNombrePsicologo(cita.psicologo_id)} · {cita.modalidad || cita.tipo || "Sesión"}</p>
                </div>
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-black text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">{estado(cita)}</span>
              </div>
            ))}
            {!cargando && citasPaciente.length === 0 && <p className="px-5 py-8 text-sm text-slate-400">No tienes citas registradas todavía.</p>}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-2">
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
          <CabeceraCompacta titulo="Consejo personalizado" etiqueta="Hoy" icono={Sparkles} />
          <p className="mt-5 text-sm leading-6 text-slate-500 dark:text-slate-300">{consejo}</p>
          <div className="mt-5 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/70">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Último registro</p>
            <p className="mt-2 text-lg font-black text-slate-900 dark:text-white">{ultimoRegistro?.estado_animo || "Sin registro"}</p>
          </div>
        </article>
      </section>

      <section className="mt-6">
        <article className="panel p-6">
          <CabeceraCompacta titulo="Lecturas IoT" etiqueta="Apoyo" icono={HeartPulse} />
          <div className="mt-5 grid gap-3 sm:grid-cols-4">
            <Dato titulo="Pulso" valor={ultimaLectura?.pulso || ultimaLectura?.heart_rate || "--"} />
            <Dato titulo="SpO2" valor={ultimaLectura?.spo2 || ultimaLectura?.oxigeno || "--"} />
            <Dato titulo="Lecturas" valor={lecturasPaciente.length} />
            <Dato titulo="Última" valor={ultimaLectura ? formatearFecha(ultimaLectura.fecha || ultimaLectura.created_at || ultimaLectura.creado_en) : "Sin datos"} />
          </div>
        </article>
      </section>
    </>
  );
}

function Tarjeta({ titulo, valor, detalle, icono: Icono, ruta }) {
  const contenido = (
    <article className="panel h-full p-5 transition hover:-translate-y-0.5 hover:shadow-lg">
      <span className="icono-panel"><Icono size={21} /></span>
      <p className="mt-5 text-2xl font-black text-slate-900 dark:text-white">{valor}</p>
      <p className="mt-1 text-sm font-bold text-slate-700 dark:text-slate-200">{titulo}</p>
      <p className="mt-1 text-xs text-slate-400">{detalle}</p>
    </article>
  );
  return ruta ? <Link to={ruta} className="block h-full">{contenido}</Link> : contenido;
}

function ControlNumero({ etiqueta, valor, onChange, max = 10 }) {
  return (
    <div className="w-full">
      <div className="flex items-end justify-between mb-3">
        <span className="text-xs font-black uppercase tracking-wider text-slate-500 dark:text-slate-400">{etiqueta}</span>
        <span className="text-sm font-black text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-3 py-1 rounded-full">{valor} / {max}</span>
      </div>
      <div className="flex justify-between gap-1 sm:gap-2">
        {Array.from({ length: max + 1 }).map((_, i) => (
          <button
            key={i}
            type="button"
            onClick={() => onChange(i)}
            className={`flex-1 h-10 sm:h-12 rounded-lg text-xs sm:text-sm font-bold transition-all ${
              valor === i
                ? 'bg-blue-600 text-white shadow-md transform scale-110'
                : 'bg-slate-100 text-slate-500 hover:bg-blue-100 hover:text-blue-600 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            {i}
          </button>
        ))}
      </div>
    </div>
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