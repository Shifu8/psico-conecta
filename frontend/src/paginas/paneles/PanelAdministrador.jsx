import {
  Activity,
  CalendarDays,
  CheckCircle2,
  CreditCard,
  Edit3,
  FileClock,
  HeartPulse,
  KeyRound,
  Search,
  Server,
  ShieldAlert,
  ShieldCheck,
  Trash2,
  UserCog,
  UserPlus,
  UserRoundCheck,
  UsersRound,
  Video,
  XCircle,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import AvatarUsuario from "../../componentes/AvatarUsuario";
import BarraProgreso from "../../componentes/BarraProgreso";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import api from "../../servicios/api";
import { capturarEvento } from "../../servicios/analitica";
import { obtenerConfiguracionGoogle } from "../../servicios/servicioAutenticacion";
import { obtenerDatosOperativos, obtenerEstadoServicios } from "../../servicios/servicioModulos";
import EncabezadoPanel from "./EncabezadoPanel";
import TablaAuditoria from "../../componentes/admin/TablaAuditoria";

const nombresRoles = { ADMIN: "Administrador", PSYCHOLOGIST: "Psicólogo", PATIENT: "Paciente" };
const estadosUsuario = { active: "Activo", inactive: "Pausado" };
const etiquetasEventos = {
  admin_user_deactivated: "Usuario desactivado",
  admin_user_status_changed: "Estado actualizado",
  admin_user_updated: "Perfil actualizado",
  google_login_failed: "Google rechazado",
  google_login_success: "Acceso con Google",
  google_register_success: "Registro con Google",
  login_blocked: "Acceso bloqueado",
  login_failed: "Inicio fallido",
  login_success: "Inicio de sesión",
  logout: "Cierre de sesión",
  password_reset_requested: "Recuperación solicitada",
  register_success: "Registro creado",
};
const estado = (item) => String(item?.estado || item?.status || "pendiente").toLowerCase();
const fechaCita = (cita) => cita.fecha || cita.fecha_inicio || cita.inicio || cita.created_at || cita.creado_en;
const esCompletado = (valor) => ["completada", "completado", "atendida", "finalizada", "finalizado", "pagado", "aprobado"].includes(valor);
const esCancelado = (valor) => ["cancelada", "cancelado", "anulada", "anulado", "fallido", "rechazado"].includes(valor);
const esPendiente = (valor) => ["pendiente", "confirmacion", "por_confirmar", "programada", "confirmada", "simulado"].includes(valor);
const contarUnicos = (items, campo) => new Set(items.map((item) => item[campo]).filter(Boolean)).size;

const formatearFecha = (valor) => {
  if (!valor) return "Sin fecha";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return "Sin fecha";
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "medium" }).format(fecha);
};

const formatearHora = (valor) => {
  if (!valor) return "-";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return "-";
  return new Intl.DateTimeFormat("es-EC", { hour: "2-digit", minute: "2-digit" }).format(fecha);
};

const formatearFechaHora = (valor) => {
  if (!valor) return "Sin fecha";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return "Sin fecha";
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(fecha);
};

const esHoy = (valor) => {
  const fecha = new Date(valor);
  return !Number.isNaN(fecha.getTime()) && fecha.toDateString() === new Date().toDateString();
};

const esFuturo = (valor) => {
  const fecha = new Date(valor);
  return !Number.isNaN(fecha.getTime()) && fecha.getTime() >= Date.now();
};

export default function PanelAdministrador() {
  const { usuario } = usarAutenticacion();
  const [usuarios, setUsuarios] = useState([]);
  const [datos, setDatos] = useState({ citas: [], sesiones: [], pagos: [], emociones: [], lecturasIot: [] });
  const [servicios, setServicios] = useState([]);
  const [auditoria, setAuditoria] = useState(null);
  const [googleOAuth, setGoogleOAuth] = useState(null);
  const [modulosErrores, setModulosErrores] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(null);
  const [editando, setEditando] = useState(null);
  const [formulario, setFormulario] = useState({ first_name: "", last_name: "", phone: "", role: "PATIENT" });

  const cargarDatos = async () => {
    setCargando(true);
    setError("");
    const [usuariosRes, modulosRes, serviciosRes, googleRes, auditoriaRes] = await Promise.allSettled([
      api.get("/api/usuarios"),
      obtenerDatosOperativos(),
      obtenerEstadoServicios(),
      obtenerConfiguracionGoogle(),
      api.get("/api/usuarios/auditoria/resumen?dias=7&limite=100"),
    ]);

    if (usuariosRes.status === "fulfilled") {
      setUsuarios(usuariosRes.value.data.users || []);
    } else {
      setError(usuariosRes.reason?.response?.data?.message || "No fue posible cargar usuarios.");
    }

    if (modulosRes.status === "fulfilled") {
      setDatos(modulosRes.value);
      setModulosErrores(modulosRes.value.errores || []);
    } else {
      setModulosErrores(["citas", "teleconsulta", "pagos", "iot"]);
    }

    if (serviciosRes.status === "fulfilled") setServicios(serviciosRes.value);
    if (googleRes.status === "fulfilled") setGoogleOAuth(googleRes.value.data);
    if (auditoriaRes.status === "fulfilled") setAuditoria(auditoriaRes.value.data);
    setCargando(false);
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const alternarEstado = async (item) => {
    setProcesando(item.id);
    setError("");
    try {
      const estadoNuevo = item.status === "active" ? "inactive" : "active";
      await api.patch(`/api/usuarios/${item.id}/status`, { status: estadoNuevo });
      capturarEvento("admin_usuario_estado_actualizado", {
        estado_nuevo: estadoNuevo,
        rol_objetivo: item.role,
      });
      await cargarDatos();
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible actualizar el estado.");
    } finally {
      setProcesando(null);
    }
  };

  const abrirEdicion = (item) => {
    setEditando(item);
    setFormulario({ first_name: item.first_name || "", last_name: item.last_name || "", phone: item.phone || "", role: item.role || "PATIENT" });
  };

  const guardarEdicion = async (evento) => {
    evento.preventDefault();
    if (!editando) return;
    setProcesando(editando.id);
    setError("");
    try {
      await api.put(`/api/usuarios/${editando.id}`, {
        first_name: formulario.first_name,
        last_name: formulario.last_name,
        phone: formulario.phone || null,
        role: formulario.role,
      });
      capturarEvento("admin_usuario_editado", {
        rol_nuevo: formulario.role,
        rol_anterior: editando.role,
      });
      setEditando(null);
      await cargarDatos();
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible editar el usuario.");
    } finally {
      setProcesando(null);
    }
  };

  const eliminarUsuario = async (item) => {
    if (item.id === usuario.id) return;
    if (!window.confirm(`¿Desactivar el acceso de ${item.full_name || item.email}?`)) return;
    setProcesando(item.id);
    setError("");
    try {
      await api.delete(`/api/usuarios/${item.id}`);
      capturarEvento("admin_usuario_desactivado", { rol_objetivo: item.role });
      await cargarDatos();
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible desactivar el usuario.");
    } finally {
      setProcesando(null);
    }
  };

  const { citas, sesiones, pagos, emociones, lecturasIot } = datos;
  const activos = usuarios.filter((item) => item.status === "active").length;
  const inactivos = usuarios.length - activos;
  const psicologos = usuarios.filter((item) => item.role === "PSYCHOLOGIST");
  const pacientes = usuarios.filter((item) => item.role === "PATIENT");
  const administradores = usuarios.filter((item) => item.role === "ADMIN");
  const totalUsuarios = Math.max(usuarios.length, 1);
  const metricasAuditoria = auditoria?.metricas || {};
  const eventosAuditoria = auditoria?.eventos_recientes || [];
  const serieAuditoria = auditoria?.serie_diaria || [];
  const maximoSerieAuditoria = Math.max(
    ...serieAuditoria.map((item) => item.accesos + item.fallos + item.registros + item.administracion),
    1,
  );

  const usuariosFiltrados = useMemo(() => {
    const termino = busqueda.trim().toLowerCase();
    if (!termino) return usuarios;
    return usuarios.filter((item) => [item.first_name, item.last_name, item.email, nombresRoles[item.role], estadosUsuario[item.status]]
      .filter(Boolean).join(" ").toLowerCase().includes(termino));
  }, [busqueda, usuarios]);

  const conteoRoles = ["ADMIN", "PSYCHOLOGIST", "PATIENT"].map((rol) => ({
    rol,
    etiqueta: nombresRoles[rol],
    valor: usuarios.filter((item) => item.role === rol).length,
  }));

  const citasStats = {
    hoy: citas.filter((cita) => esHoy(fechaCita(cita))).length,
    proximas: citas.filter((cita) => esFuturo(fechaCita(cita)) && !esCancelado(estado(cita))).length,
    pendientes: citas.filter((cita) => esPendiente(estado(cita))).length,
    completadas: citas.filter((cita) => esCompletado(estado(cita))).length,
    canceladas: citas.filter((cita) => esCancelado(estado(cita))).length,
  };

  const sesionesStats = {
    creadas: sesiones.length,
    pendientes: sesiones.filter((sesion) => esPendiente(estado(sesion))).length,
    finalizadas: sesiones.filter((sesion) => esCompletado(estado(sesion))).length,
    problemas: sesiones.filter((sesion) => ["error", "fallida", "fallido", "conexion"].includes(estado(sesion))).length,
  };

  const pagosStats = {
    pendientes: pagos.filter((pago) => esPendiente(estado(pago))).length,
    aprobados: pagos.filter((pago) => ["aprobado", "pagado", "completado"].includes(estado(pago))).length,
    fallidos: pagos.filter((pago) => ["fallido", "rechazado", "cancelado"].includes(estado(pago))).length,
    total: pagos.reduce((suma, pago) => suma + Number(pago.monto || pago.amount || 0), 0),
  };

  const lecturasHoy = lecturasIot.filter((lectura) => esHoy(lectura.creado_en || lectura.created_at || lectura.fecha)).length;
  const alertasBienestar = emociones.filter((item) => Number(item.estres || item.stress || 0) >= 8).length +
    lecturasIot.filter((item) => Number(item.pulso || item.heart_rate || 0) >= 110).length;

  const psicologosResumen = psicologos.map((psicologo) => {
    const citasPsicologo = citas.filter((cita) => Number(cita.psicologo_id) === Number(psicologo.id));
    return { ...psicologo, pacientesAsignados: contarUnicos(citasPsicologo, "paciente_id"), citasAtendidas: citasPsicologo.filter((cita) => esCompletado(estado(cita))).length };
  });

  const pacientesResumen = pacientes.map((paciente) => {
    const citasPaciente = citas.filter((cita) => Number(cita.paciente_id) === Number(paciente.id));
    const ultima = [...citasPaciente].sort((a, b) => new Date(fechaCita(b) || 0) - new Date(fechaCita(a) || 0))[0];
    const proxima = citasPaciente.find((cita) => esFuturo(fechaCita(cita)) && !esCancelado(estado(cita)));
    return { ...paciente, ultimaCita: ultima ? formatearFecha(fechaCita(ultima)) : "Sin citas", seguimiento: proxima ? "Programado" : "Pendiente" };
  });
  const resumen = [
    { etiqueta: "Usuarios", valor: usuarios.length, detalle: "Cuentas registradas", icono: UsersRound },
    { etiqueta: "Pacientes", valor: pacientes.length, detalle: "Perfiles de atención", icono: UserRoundCheck },
    { etiqueta: "Psicólogos", valor: psicologos.length, detalle: "Profesionales", icono: HeartPulse },
    { etiqueta: "Administradores", valor: administradores.length, detalle: "Control del sistema", icono: UserCog },
  ];

  const operacion = [
    { titulo: "Citas hoy", valor: citasStats.hoy, detalle: `${citasStats.proximas} próximas`, icono: CalendarDays },
    { titulo: "Teleconsultas", valor: sesionesStats.creadas, detalle: `${sesionesStats.pendientes} pendientes`, icono: Video },
    { titulo: "Pagos", valor: `$${pagosStats.total.toFixed(2)}`, detalle: `${pagosStats.pendientes} pendientes`, icono: CreditCard },
    { titulo: "Bienestar IoT", valor: emociones.length + lecturasIot.length, detalle: `${alertasBienestar} alertas`, icono: Activity },
  ];



  const citasOrdenadas = [...citas].sort((a, b) => new Date(fechaCita(a) || 0) - new Date(fechaCita(b) || 0)).slice(0, 5);

  return (
    <>
      <EncabezadoPanel
        etiqueta="Administración"
        titulo="Control general del sistema"
        texto="Usuarios, operación, seguridad y módulos preparados sin exponer notas clínicas sensibles."
      />

      <section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {resumen.map(({ etiqueta, valor, detalle, icono: Icono }) => (
          <article key={etiqueta} className="panel p-5">
            <div className="flex items-start justify-between gap-4">
              <span className="icono-panel"><Icono size={21} /></span>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-black text-slate-500 dark:bg-slate-800 dark:text-slate-300">{detalle}</span>
            </div>
            <p className="mt-5 text-3xl font-black text-slate-900 dark:text-white">{valor}</p>
            <p className="mt-1 text-sm font-bold text-slate-500 dark:text-slate-300">{etiqueta}</p>
          </article>
        ))}
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1fr_.95fr]">
        <article className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="etiqueta">Resumen general</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">Usuarios por rol</h2>
            </div>
            <span className="icono-panel"><UsersRound size={22} /></span>
          </div>
          <div className="mt-6 space-y-4">
            {conteoRoles.map((item, indice) => (
              <BarraProgreso
                key={item.rol}
                etiqueta={`${item.etiqueta} (${item.valor})`}
                valor={item.valor}
                total={totalUsuarios}
                color={["from-amber-500 to-orange-400", "from-violet-600 to-fuchsia-400", "from-emerald-500 to-teal-400"][indice]}
              />
            ))}
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <Dato titulo="Usuarios activos" valor={activos} tono="emerald" />
            <Dato titulo="Usuarios inactivos" valor={inactivos} />
          </div>
        </article>

        <article className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="etiqueta">Operación</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">Módulos preparados</h2>
            </div>
            <span className="icono-panel"><Server size={22} /></span>
          </div>
          {modulosErrores.length > 0 && (
            <p className="mt-5 rounded-2xl bg-amber-50 p-3 text-sm font-semibold text-amber-800 dark:bg-amber-950/30 dark:text-amber-200">
              Algunos módulos no respondieron: {modulosErrores.join(", ")}.
            </p>
          )}
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {operacion.map(({ titulo, valor, detalle, icono: Icono }) => (
              <div key={titulo} className="rounded-2xl border border-slate-100 p-4 dark:border-slate-800">
                <Icono size={19} className="text-blue-600 dark:text-blue-300" />
                <p className="mt-3 text-2xl font-black text-slate-900 dark:text-white">{valor}</p>
                <p className="text-sm font-bold text-slate-700 dark:text-slate-200">{titulo}</p>
                <p className="mt-1 text-xs text-slate-400">{detalle}</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="panel mt-6 overflow-hidden">
        <div className="border-b border-slate-100 px-5 py-5 dark:border-slate-800 sm:flex sm:items-center sm:justify-between sm:gap-5 sm:px-6">
          <div>
            <h2 className="text-lg font-black text-slate-900 dark:text-white">Gestión de usuarios</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">Busca, edita, activa, pausa o desactiva perfiles.</p>
          </div>
          <label className="mt-4 flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950 sm:mt-0 sm:w-72">
            <Search size={17} className="text-slate-400" />
            <input value={busqueda} onChange={(evento) => setBusqueda(evento.target.value)} placeholder="Buscar usuario" className="min-w-0 flex-1 bg-transparent text-sm text-slate-700 placeholder:text-slate-400 dark:text-slate-200" />
          </label>
        </div>
        {error && <p className="mx-5 mt-4 rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 dark:bg-red-950/30 dark:text-red-200 sm:mx-6">{error}</p>}
        <div className="overflow-x-auto">
          <table className="w-full min-w-[920px] text-left text-sm">
            <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-400 dark:bg-slate-800/80">
              <tr>
                <th className="px-6 py-4">Usuario</th>
                <th className="px-6 py-4">Rol</th>
                <th className="px-6 py-4">Estado</th>
                <th className="px-6 py-4">Creación</th>
                <th className="px-6 py-4 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {cargando && <tr><td colSpan="5" className="px-6 py-10 text-center text-sm text-slate-400">Cargando usuarios...</td></tr>}
              {!cargando && usuariosFiltrados.map((item) => (
                <tr key={item.id} className="transition hover:bg-blue-50/50 dark:hover:bg-slate-800/45">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <AvatarUsuario usuario={item} tamano="sm" className="rounded-xl" />
                      <div>
                        <p className="font-bold text-slate-800 dark:text-slate-100">{item.first_name} {item.last_name}</p>
                        <p className="mt-1 text-xs text-slate-400">{item.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-bold text-blue-600 dark:text-blue-300">{nombresRoles[item.role] || item.role}</td>
                  <td className="px-6 py-4"><EstadoUsuario estado={item.status} /></td>
                  <td className="px-6 py-4 text-slate-500 dark:text-slate-300">{formatearFecha(item.created_at)}</td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-2">
                      <button type="button" onClick={() => abrirEdicion(item)} className="rounded-lg bg-slate-100 p-2 text-slate-600 transition hover:bg-blue-50 hover:text-blue-700 dark:bg-slate-800 dark:text-slate-300" title="Editar perfil"><Edit3 size={16} /></button>
                      <button type="button" onClick={() => alternarEstado(item)} disabled={procesando === item.id} className="rounded-lg bg-blue-50 px-3 py-2 text-xs font-black text-blue-700 transition hover:bg-blue-100 disabled:opacity-50 dark:bg-blue-950/50 dark:text-blue-300">
                        {item.status === "active" ? "Pausar" : "Activar"}
                      </button>
                      <button type="button" onClick={() => eliminarUsuario(item)} disabled={procesando === item.id || item.id === usuario.id} className="rounded-lg bg-red-50 p-2 text-red-600 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-red-950/30 dark:text-red-300" title="Desactivar usuario"><Trash2 size={16} /></button>
                    </div>
                  </td>
                </tr>
              ))}
              {!cargando && usuariosFiltrados.length === 0 && <tr><td colSpan="5" className="px-6 py-10 text-center text-sm text-slate-400">No encontramos usuarios para esta búsqueda.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
      <section className="mt-6 grid gap-5 xl:grid-cols-2">
        <ListaPersonas
          titulo="Psicólogos"
          texto="Disponibilidad, pacientes asignados y citas atendidas."
          items={psicologosResumen.slice(0, 5)}
          vacio="No hay psicólogos registrados."
          renderDetalle={(item) => `${item.pacientesAsignados} pacientes · ${item.citasAtendidas} citas atendidas`}
        />
        <ListaPersonas
          titulo="Pacientes"
          texto="Actividad, última cita y seguimiento pendiente sin notas clínicas."
          items={pacientesResumen.slice(0, 5)}
          vacio="No hay pacientes registrados."
          renderDetalle={(item) => `Última cita: ${item.ultimaCita}`}
          renderEstado={(item) => item.seguimiento}
        />
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-1">
        <article className="panel p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="etiqueta">Citas del sistema</p>
              <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">Estado de agenda</h2>
            </div>
            <span className="icono-panel"><CalendarDays size={22} /></span>
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-5">
            {[["Hoy", citasStats.hoy], ["Próximas", citasStats.proximas], ["Pendientes", citasStats.pendientes], ["Completadas", citasStats.completadas], ["Canceladas", citasStats.canceladas]].map(([titulo, valor]) => (
              <Dato key={titulo} titulo={titulo} valor={valor} />
            ))}
          </div>
          <div className="mt-5 divide-y divide-slate-100 dark:divide-slate-800">
            {citasOrdenadas.map((cita) => (
              <div key={cita.id || `${fechaCita(cita)}-${cita.paciente_id}`} className="flex items-center justify-between gap-4 py-3 text-sm">
                <div>
                  <p className="font-bold text-slate-800 dark:text-slate-100">Paciente #{cita.paciente_id || "-"} con psicólogo #{cita.psicologo_id || "-"}</p>
                  <p className="text-xs text-slate-400">{formatearFecha(fechaCita(cita))} · {formatearHora(fechaCita(cita))}</p>
                </div>
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-black text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">{estado(cita)}</span>
              </div>
            ))}
            {citasOrdenadas.length === 0 && <p className="py-8 text-sm text-slate-400">Todavía no hay citas registradas.</p>}
          </div>
        </article>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-3">
        <ModuloResumen icono={Video} titulo="Teleconsultas" tono="blue" datos={[["Creadas", sesionesStats.creadas], ["Pendientes", sesionesStats.pendientes], ["Finalizadas", sesionesStats.finalizadas], ["Problemas", sesionesStats.problemas]]} />
        <ModuloResumen icono={CreditCard} titulo="Pagos" tono="emerald" datos={[["Pendientes", pagosStats.pendientes], ["Aprobados", pagosStats.aprobados], ["Fallidos", pagosStats.fallidos], ["Recaudado", `$${pagosStats.total.toFixed(2)}`]]} />
        <ModuloResumen icono={HeartPulse} titulo="IoT / bienestar" tono="rose" datos={[["Emociones", emociones.length], ["Lecturas hoy", lecturasHoy], ["Alertas", alertasBienestar], ["Lecturas", lecturasIot.length]]} />
      </section>



      <TablaAuditoria serieDiaria={serieAuditoria} eventos={eventosAuditoria} onRefresh={cargarDatos} />

      {editando && (
        <div className="fixed inset-0 z-40 grid place-items-center bg-slate-950/50 px-4 py-8 backdrop-blur-sm">
          <form onSubmit={guardarEdicion} className="panel w-full max-w-2xl p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="etiqueta">Editar usuario</p>
                <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">{editando.full_name}</h2>
              </div>
              <button type="button" onClick={() => setEditando(null)} className="rounded-xl bg-slate-100 p-2 text-slate-500 hover:text-slate-800 dark:bg-slate-800 dark:text-slate-300"><XCircle size={18} /></button>
            </div>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <CampoEdicion etiqueta="Nombre" valor={formulario.first_name} onChange={(valor) => setFormulario((actual) => ({ ...actual, first_name: valor }))} />
              <CampoEdicion etiqueta="Apellido" valor={formulario.last_name} onChange={(valor) => setFormulario((actual) => ({ ...actual, last_name: valor }))} />
              <CampoEdicion etiqueta="Teléfono" valor={formulario.phone} onChange={(valor) => setFormulario((actual) => ({ ...actual, phone: valor }))} requerido={false} />
              <label>
                <span className="text-xs font-black uppercase tracking-wider text-slate-400">Rol</span>
                <select className="campo mt-2" value={formulario.role} onChange={(e) => setFormulario((actual) => ({ ...actual, role: e.target.value }))}>
                  <option value="ADMIN">Administrador</option>
                  <option value="PSYCHOLOGIST">Psicólogo</option>
                  <option value="PATIENT">Paciente</option>
                </select>
              </label>
            </div>
            <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <button type="button" onClick={() => setEditando(null)} className="boton-secundario">Cancelar</button>
              <button type="submit" disabled={procesando === editando.id} className="boton-primario"><Edit3 size={17} /> Guardar perfil</button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}


function Dato({ titulo, valor, detalle, tono, icono: Icono }) {
  const clase = tono === "emerald" ? "bg-emerald-50 dark:bg-emerald-950/30" : "bg-slate-50 dark:bg-slate-800/70";
  return (
    <div className={`rounded-2xl p-4 ${clase}`}>
      {Icono && <Icono size={18} className="mb-3 text-blue-600 dark:text-blue-300" />}
      <p className="text-xl font-black text-slate-900 dark:text-white">{valor}</p>
      <p className="mt-1 text-xs font-bold text-slate-500 dark:text-slate-300">{titulo}</p>
      {detalle && <p className="mt-1 text-xs text-slate-400">{detalle}</p>}
    </div>
  );
}

function EstadoUsuario({ estado }) {
  const activo = estado === "active";
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-bold ${activo ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300" : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300"}`}>
      {estadosUsuario[estado] || estado}
    </span>
  );
}

function ListaPersonas({ titulo, texto, items, vacio, renderDetalle, renderEstado }) {
  return (
    <article className="panel overflow-hidden">
      <div className="border-b border-slate-100 px-5 py-5 dark:border-slate-800">
        <h2 className="text-lg font-black text-slate-900 dark:text-white">{titulo}</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">{texto}</p>
      </div>
      <div className="divide-y divide-slate-100 dark:divide-slate-800">
        {items.map((item) => (
          <div key={item.id} className="flex items-center justify-between gap-4 px-5 py-4">
            <div className="flex items-center gap-3">
              <AvatarUsuario usuario={item} tamano="sm" className="rounded-xl" />
              <div>
                <p className="font-black text-slate-900 dark:text-white">{item.full_name}</p>
                <p className="text-sm text-slate-500 dark:text-slate-300">{renderDetalle(item)}</p>
              </div>
            </div>
            {renderEstado ? (
              <span className={`rounded-full px-3 py-1 text-xs font-black ${renderEstado(item) === "Programado" ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300" : "bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-200"}`}>{renderEstado(item)}</span>
            ) : (
              <EstadoUsuario estado={item.status} />
            )}
          </div>
        ))}
        {items.length === 0 && <p className="px-5 py-8 text-sm text-slate-400">{vacio}</p>}
      </div>
    </article>
  );
}

function ModuloResumen({ icono: Icono, titulo, datos, tono }) {
  const color = tono === "emerald" ? "text-emerald-600 dark:text-emerald-300" : tono === "rose" ? "text-rose-600 dark:text-rose-300" : "text-blue-600 dark:text-blue-300";
  return (
    <article className="panel p-6">
      <Icono size={22} className={color} />
      <h2 className="mt-4 text-lg font-black text-slate-900 dark:text-white">{titulo}</h2>
      <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
        {datos.map(([dato, valor]) => <Dato key={dato} titulo={dato} valor={valor} />)}
      </div>
    </article>
  );
}

function CampoEdicion({ etiqueta, valor, onChange, requerido = true }) {
  return (
    <label>
      <span className="text-xs font-black uppercase tracking-wider text-slate-400">{etiqueta}</span>
      <input className="campo mt-2" value={valor} onChange={(e) => onChange(e.target.value)} required={requerido} minLength={requerido ? 2 : undefined} />
    </label>
  );
}
