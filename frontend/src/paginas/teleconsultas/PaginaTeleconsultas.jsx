import { CalendarDays, Clock3, RefreshCw, ShieldCheck, Video } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { mensajeErrorTeleconsulta, teleconsultasApi } from "../../servicios/servicioTeleconsultas";

const fecha = (valor) => new Intl.DateTimeFormat("es-EC", { dateStyle: "full" }).format(new Date(valor));
const hora = (valor) => new Intl.DateTimeFormat("es-EC", { hour: "2-digit", minute: "2-digit" }).format(new Date(valor));

export default function PaginaTeleconsultas() {
  const [sesiones, setSesiones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargar = async () => {
    setCargando(true);
    setError("");
    try {
      const { data } = await teleconsultasApi.misSesiones();
      setSesiones(Array.isArray(data) ? data : []);
    } catch (excepcion) {
      setError(mensajeErrorTeleconsulta(excepcion, "No fue posible cargar las teleconsultas."));
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => { cargar(); }, []);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-black uppercase tracking-[.2em] text-blue-600">Zoom seguro</p>
          <h1 className="mt-2 text-3xl font-black text-slate-900 dark:text-white">Mis teleconsultas</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-600 dark:text-slate-300">
            Solo se muestran citas virtuales confirmadas. El acceso se habilita pocos minutos antes de la hora acordada.
          </p>
        </div>
        <button onClick={cargar} disabled={cargando} className="boton-secundario inline-flex items-center gap-2">
          <RefreshCw size={17} className={cargando ? "animate-spin" : ""} /> Actualizar
        </button>
      </div>

      {error && <p className="mt-6 rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-700 dark:bg-red-950/30 dark:text-red-200">{error}</p>}

      <div className="mt-8 grid gap-5">
        {sesiones.map((sesion) => (
          <article key={sesion.id} className="panel p-6">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex gap-4">
                <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300"><Video size={23} /></span>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-black text-slate-900 dark:text-white">Teleconsulta PsicoConecta</h2>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">{sesion.estado}</span>
                  </div>
                  <p className="mt-2 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300"><CalendarDays size={16} /> {fecha(sesion.fecha_hora_inicio)}</p>
                  <p className="mt-1 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300"><Clock3 size={16} /> {hora(sesion.fecha_hora_inicio)} – {hora(sesion.fecha_hora_fin)}</p>
                  <p className="mt-2 flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400"><ShieldCheck size={15} /> Sala de espera y contraseña administradas por Zoom.</p>
                </div>
              </div>
              <div className="sm:text-right">
                <Link to={`/teleconsultas/${sesion.cita_id}`} className="boton-primario inline-flex items-center gap-2">
                  <Video size={17} /> Ver sesión
                </Link>
                {!sesion.puede_ingresar && sesion.mensaje_acceso && (
                  <p className="mt-2 max-w-xs text-xs text-slate-500 dark:text-slate-400">{sesion.mensaje_acceso}</p>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>

      {!cargando && !error && sesiones.length === 0 && (
        <div className="mt-8 rounded-3xl border border-dashed border-slate-300 p-10 text-center dark:border-slate-700">
          <Video className="mx-auto text-slate-400" size={34} />
          <h2 className="mt-4 font-black text-slate-800 dark:text-white">No tienes teleconsultas programadas</h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Una cita virtual aparecerá aquí después de ser confirmada por el psicólogo.</p>
        </div>
      )}
    </div>
  );
}
