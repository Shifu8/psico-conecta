import { useState, useEffect } from "react";
import { citasApi } from "../../servicios/citasApi";
import api from "../../servicios/api";
import EncabezadoPanel from "../paneles/EncabezadoPanel";
import { CalendarX2, Trash2 } from "lucide-react";

export default function PaginaDisponibilidadAdmin() {
  const [psicologos, setPsicologos] = useState([]);
  const [psicologoId, setPsicologoId] = useState("");
  const [excepciones, setExcepciones] = useState([]);
  const [cargando, setCargando] = useState(false);
  
  // Formulario nueva excepción
  const [fecha, setFecha] = useState("");
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    cargarPsicologos();
  }, []);

  useEffect(() => {
    if (psicologoId) {
      cargarExcepciones();
    } else {
      setExcepciones([]);
    }
  }, [psicologoId]);

  const cargarPsicologos = async () => {
    try {
      const res = await api.get("/api/usuarios/psicologos");
      setPsicologos(res.data.psicologos || []);
    } catch (err) {
      console.error("Error al cargar psicólogos", err);
    }
  };

  const cargarExcepciones = async () => {
    setCargando(true);
    try {
      const res = await citasApi.getExcepciones(psicologoId);
      setExcepciones(res.data);
    } catch (err) {
      console.error("Error al cargar excepciones", err);
    } finally {
      setCargando(false);
    }
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();
    if (!psicologoId) {
      setError("Selecciona un psicólogo primero.");
      return;
    }
    if (!fecha) {
      setError("Debes seleccionar una fecha.");
      return;
    }
    setError("");

    try {
      await citasApi.crearExcepcion(psicologoId, { fecha, motivo });
      setFecha("");
      setMotivo("");
      cargarExcepciones();
    } catch (err) {
      setError(err.response?.data?.error || "Ocurrió un error al crear el bloqueo.");
    }
  };

  const eliminarExcepcion = async (id) => {
    if (!window.confirm("¿Estás seguro de eliminar este bloqueo?")) return;
    try {
      await citasApi.eliminarExcepcion(id);
      cargarExcepciones();
    } catch (err) {
      console.error("Error al eliminar excepción", err);
    }
  };

  return (
    <>
      <EncabezadoPanel
        titulo="Gestión de Disponibilidad"
        descripcion="Bloquea fechas específicas para los profesionales (vacaciones, emergencias, etc)."
      />

      <div className="mt-8 flex flex-col gap-8 lg:flex-row">
        {/* Selector y Formulario */}
        <div className="flex w-full flex-col gap-6 lg:w-1/3">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <h2 className="mb-4 text-lg font-bold text-slate-800 dark:text-white">Psicólogo</h2>
            <select
              value={psicologoId}
              onChange={(e) => setPsicologoId(e.target.value)}
              className="campo mb-4 w-full text-slate-700 dark:text-slate-200"
            >
              <option value="">Selecciona un profesional...</option>
              {psicologos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.first_name} {p.last_name}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <h2 className="mb-4 text-lg font-bold text-slate-800 dark:text-white">Bloquear Fecha</h2>
            <form onSubmit={manejarSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300">Fecha</label>
                <input
                  type="date"
                  value={fecha}
                  onChange={(e) => setFecha(e.target.value)}
                  className="campo mt-1 w-full text-slate-700 dark:text-slate-200"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300">Motivo (Opcional)</label>
                <input
                  type="text"
                  placeholder="Ej: Vacaciones"
                  value={motivo}
                  onChange={(e) => setMotivo(e.target.value)}
                  className="campo mt-1 w-full text-slate-700 dark:text-slate-200"
                />
              </div>
              {error && <p className="mb-4 text-sm font-semibold text-red-500">{error}</p>}
              <button
                type="submit"
                disabled={!psicologoId}
                className="w-full rounded-xl bg-blue-600 px-4 py-3 font-bold text-white transition hover:bg-blue-700 disabled:opacity-50"
              >
                Añadir Bloqueo
              </button>
            </form>
          </div>
        </div>

        {/* Lista de Excepciones */}
        <div className="flex w-full flex-col gap-6 lg:w-2/3">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <h2 className="mb-6 text-lg font-bold text-slate-800 dark:text-white">Fechas Bloqueadas</h2>
            
            {!psicologoId ? (
              <p className="text-center text-slate-500 dark:text-slate-400">Selecciona un psicólogo para ver sus bloqueos.</p>
            ) : cargando ? (
              <p className="text-center text-slate-500 dark:text-slate-400">Cargando...</p>
            ) : excepciones.length === 0 ? (
              <div className="flex flex-col items-center py-10 text-slate-400">
                <CalendarX2 size={48} className="mb-4 opacity-20" />
                <p>No hay fechas bloqueadas para este profesional.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-500 dark:text-slate-400">
                  <thead className="border-b border-slate-200 uppercase text-slate-700 dark:border-slate-700 dark:text-slate-300">
                    <tr>
                      <th className="px-4 py-3">Fecha</th>
                      <th className="px-4 py-3">Motivo</th>
                      <th className="px-4 py-3 text-right">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {excepciones.map((exc) => (
                      <tr key={exc.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                        <td className="px-4 py-3 font-bold text-slate-800 dark:text-slate-200">{exc.fecha}</td>
                        <td className="px-4 py-3">{exc.motivo || "Sin motivo especificado"}</td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => eliminarExcepcion(exc.id)}
                            className="text-red-500 hover:text-red-700"
                            title="Eliminar bloqueo"
                          >
                            <Trash2 size={18} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
