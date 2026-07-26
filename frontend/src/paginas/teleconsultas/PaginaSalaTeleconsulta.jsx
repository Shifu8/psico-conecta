import { ArrowLeft, CalendarDays, Clock3, ExternalLink, LoaderCircle, ShieldCheck, Video, Heart } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { mensajeErrorTeleconsulta, teleconsultasApi } from "../../servicios/servicioTeleconsultas";
import { citasApi } from "../../servicios/citasApi";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";

const fechaHora = (valor) => new Intl.DateTimeFormat("es-EC", { dateStyle: "full", timeStyle: "short" }).format(new Date(valor));

export default function PaginaSalaTeleconsulta() {
  const { citaId } = useParams();
  const { usuario } = usarAutenticacion();
  
  const [sesion, setSesion] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [ingresando, setIngresando] = useState(false);
  const [error, setError] = useState("");
  const [ahora, setAhora] = useState(Date.now());
  const [patientId, setPatientId] = useState(null);

  const esPsicologo = usuario?.role === 'PSYCHOLOGIST' || usuario?.role?.name === 'PSYCHOLOGIST';

  const cargar = async () => {
    setCargando(true);
    setError("");
    try {
      const [resSesion, resCita] = await Promise.all([
        teleconsultasApi.obtenerPorCita(citaId),
        citasApi.getDetalle(citaId)
      ]);
      setSesion(resSesion.data);
      setPatientId(resCita.data.paciente_id);
    } catch (excepcion) {
      setError(mensajeErrorTeleconsulta(excepcion, "No fue posible preparar la teleconsulta."));
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => { cargar(); }, [citaId]);
  
  useEffect(() => {
    const reloj = window.setInterval(() => setAhora(Date.now()), 30000);
    return () => window.clearInterval(reloj);
  }, []);

  useEffect(() => {
    if (!sesion || sesion.puede_ingresar || !sesion.disponible_desde) return;
    if (ahora >= new Date(sesion.disponible_desde).getTime()) cargar();
  }, [ahora, sesion?.puede_ingresar, sesion?.disponible_desde]);

  const cuentaAtras = useMemo(() => {
    if (!sesion?.disponible_desde) return "";
    const diferencia = new Date(sesion.disponible_desde).getTime() - ahora;
    if (diferencia <= 0) return "";
    const minutos = Math.ceil(diferencia / 60000);
    return `El acceso se habilitará en aproximadamente ${minutos} minuto${minutos === 1 ? "" : "s"}.`;
  }, [sesion, ahora]);

  const ingresar = async () => {
    setIngresando(true);
    setError("");
    const ventana = window.open("about:blank", "_blank");
    if (ventana) {
      ventana.opener = null;
      ventana.document.title = "Preparando Zoom...";
    }
    try {
      const { data } = await teleconsultasApi.obtenerAcceso(citaId);
      if (ventana) ventana.location.replace(data.url);
      else window.location.assign(data.url);
    } catch (excepcion) {
      if (ventana) ventana.close();
      setError(mensajeErrorTeleconsulta(excepcion, "No fue posible abrir Zoom."));
      await cargar();
    } finally {
      setIngresando(false);
    }
  };

  if (cargando) return <div className="grid min-h-[45vh] place-items-center"><LoaderCircle className="animate-spin text-blue-600" size={34} /></div>;

  const rutaTelemetria = esPsicologo 
    ? `/psicologo/telemetria/${patientId}`
    : `/paciente/telemetria/${patientId}`;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <Link to="/teleconsultas" className="inline-flex items-center gap-2 text-sm font-bold text-blue-600 hover:underline"><ArrowLeft size={17} /> Volver</Link>

      <article className="mt-6 overflow-hidden rounded-3xl bg-gradient-to-br from-blue-700 via-indigo-700 to-slate-950 p-7 text-white shadow-xl sm:p-10">
        <div className="flex items-center gap-3">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-white/15"><Video size={25} /></span>
          <div>
            <p className="text-xs font-bold uppercase tracking-[.2em] text-blue-100">Sala virtual</p>
            <h1 className="text-2xl font-black">Teleconsulta PsicoConecta</h1>
          </div>
        </div>
        
        {sesion && (
          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            <Dato icono={CalendarDays} titulo="Fecha y hora" valor={fechaHora(sesion.fecha_hora_inicio)} />
            <Dato icono={Clock3} titulo="Finalización estimada" valor={fechaHora(sesion.fecha_hora_fin)} />
          </div>
        )}
        
        <div className="mt-8 rounded-2xl bg-white/10 p-4 text-sm leading-6 text-blue-50">
          <ShieldCheck className="mr-2 inline" size={18} />
          La sala de espera está activa. El paciente no podrá iniciar la reunión y el enlace de anfitrión solo se genera para el psicólogo.
        </div>
        
        <div className="flex flex-col gap-4 mt-7">
          <button 
            onClick={ingresar} 
            disabled={ingresando || !sesion?.puede_ingresar} 
            className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-white px-5 py-3.5 font-black text-blue-800 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50 shadow-md"
          >
            {ingresando ? <LoaderCircle className="animate-spin" size={19} /> : <ExternalLink size={19} />} 
            {ingresando ? "Preparando acceso..." : "Ingresar a Zoom"}
          </button>

          {patientId && (
            <Link
              to={rutaTelemetria}
              className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-red-500 to-pink-600 px-5 py-3.5 font-black text-white transition hover:opacity-90 shadow-md"
            >
              <Heart className="h-5 w-5 animate-pulse text-white" />
              {esPsicologo ? "Monitorear Pulsos Cardíacos" : "Ver Mi Ritmo Cardíaco en Vivo"}
            </Link>
          )}
        </div>
        
        {!sesion?.puede_ingresar && (
          <p className="mt-3 text-center text-sm text-blue-100">
            {sesion?.estado === "ERROR"
              ? (sesion?.mensaje_acceso || "La reunión de Zoom no pudo prepararse.")
              : (cuentaAtras || sesion?.mensaje_acceso)}
          </p>
        )}
      </article>

      {error && <p className="mt-5 rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-700 dark:bg-red-950/30 dark:text-red-200">{error}</p>}
    </div>
  );
}

function Dato({ icono: Icono, titulo, valor }) {
  return (
    <div className="rounded-2xl bg-white/10 p-4">
      <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue-100"><Icono size={16} /> {titulo}</p>
      <p className="mt-2 font-black">{valor}</p>
    </div>
  );
}
