import { Search, ShieldCheck, UserRoundCheck, UsersRound } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import api from "../../servicios/api";
import EncabezadoPanel from "./EncabezadoPanel";

const estadisticasIniciales = [
  { etiqueta: "Usuarios", valor: "0", icono: UsersRound },
  { etiqueta: "Activos", valor: "0", icono: UserRoundCheck },
  { etiqueta: "Perfiles disponibles", valor: "3", icono: ShieldCheck },
];

const nombresRoles = {
  ADMIN: "Administrador",
  PSYCHOLOGIST: "Psicólogo",
  PATIENT: "Paciente",
};

export default function PanelAdministrador() {
  const [usuarios, setUsuarios] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(null);

  const cargarUsuarios = async () => {
    setCargando(true);
    try {
      const { data } = await api.get("/api/usuarios");
      setUsuarios(data.users || []);
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible cargar los usuarios.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const alternarEstado = async (usuario) => {
    setProcesando(usuario.id);
    setError("");
    try {
      await api.patch(`/api/usuarios/${usuario.id}/status`, {
        status: usuario.status === "active" ? "inactive" : "active",
      });
      await cargarUsuarios();
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible actualizar el estado.");
    } finally {
      setProcesando(null);
    }
  };

  const activos = usuarios.filter((usuario) => usuario.status === "active").length;
  const estadisticas = estadisticasIniciales.map((item) => {
    if (item.etiqueta === "Usuarios") return { ...item, valor: usuarios.length };
    if (item.etiqueta === "Activos") return { ...item, valor: activos };
    return item;
  });

  const usuariosFiltrados = useMemo(() => {
    const termino = busqueda.trim().toLowerCase();
    if (!termino) return usuarios;
    return usuarios.filter((usuario) =>
      [usuario.first_name, usuario.last_name, usuario.email, nombresRoles[usuario.role]]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(termino),
    );
  }, [busqueda, usuarios]);

  return (
    <>
      <EncabezadoPanel
        etiqueta="Administración"
        titulo="Todo bajo control."
        texto="Gestiona perfiles, roles y accesos desde un espacio claro y organizado."
      />

      <section className="mt-8 grid gap-4 sm:grid-cols-3">
        {estadisticas.map(({ etiqueta, valor, icono: Icono }) => (
          <article key={etiqueta} className="panel p-5">
            <span className="icono-panel">
              <Icono size={21} />
            </span>
            <p className="mt-5 text-3xl font-black text-slate-900 dark:text-white">{valor}</p>
            <p className="mt-1 text-sm font-bold text-slate-500 dark:text-slate-300">{etiqueta}</p>
          </article>
        ))}
      </section>

      <section className="panel mt-6 overflow-hidden">
        <div className="border-b border-slate-100 px-5 py-5 dark:border-slate-800 sm:flex sm:items-center sm:justify-between sm:gap-5 sm:px-6">
          <div>
            <h2 className="text-lg font-black text-slate-900 dark:text-white">Usuarios registrados</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">
              Consulta perfiles y administra su estado de acceso.
            </p>
          </div>
          <label className="mt-4 flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950 sm:mt-0 sm:w-64">
            <Search size={17} className="text-slate-400" />
            <input
              value={busqueda}
              onChange={(evento) => setBusqueda(evento.target.value)}
              placeholder="Buscar usuario"
              className="min-w-0 flex-1 bg-transparent text-sm text-slate-700 placeholder:text-slate-400 dark:text-slate-200"
            />
          </label>
        </div>
        {error && <p className="mx-5 mt-4 rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 dark:bg-red-950/30 dark:text-red-200 sm:mx-6">{error}</p>}
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left text-sm">
            <thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-400 dark:bg-slate-800/80">
              <tr>
                <th className="px-6 py-4">Usuario</th>
                <th className="px-6 py-4">Rol</th>
                <th className="px-6 py-4">Estado</th>
                <th className="px-6 py-4">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {cargando && (
                <tr>
                  <td colSpan="4" className="px-6 py-10 text-center text-sm text-slate-400">
                    Cargando usuarios...
                  </td>
                </tr>
              )}
              {!cargando && usuariosFiltrados.map((usuario) => (
                <tr key={usuario.id} className="transition hover:bg-blue-50/50 dark:hover:bg-slate-800/45">
                  <td className="px-6 py-4">
                    <p className="font-bold text-slate-800 dark:text-slate-100">
                      {usuario.first_name} {usuario.last_name}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">{usuario.email}</p>
                  </td>
                  <td className="px-6 py-4 font-bold text-blue-600 dark:text-blue-300">
                    {nombresRoles[usuario.role] || usuario.role}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-bold ${
                      usuario.status === "active"
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                        : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300"
                    }`}>
                      {usuario.status === "active" ? "Activo" : "Pausado"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      type="button"
                      onClick={() => alternarEstado(usuario)}
                      disabled={procesando === usuario.id}
                      className="rounded-lg bg-blue-50 px-3 py-2 text-xs font-black text-blue-700 transition hover:bg-blue-100 disabled:opacity-50 dark:bg-blue-950/50 dark:text-blue-300 dark:hover:bg-blue-950"
                    >
                      {usuario.status === "active" ? "Desactivar" : "Activar"}
                    </button>
                  </td>
                </tr>
              ))}
              {!cargando && usuariosFiltrados.length === 0 && (
                <tr>
                  <td colSpan="4" className="px-6 py-10 text-center text-sm text-slate-400">
                    No encontramos usuarios para esta búsqueda.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
