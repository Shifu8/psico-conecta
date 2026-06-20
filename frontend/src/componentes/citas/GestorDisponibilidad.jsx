import React, { useEffect, useState } from 'react';
import { useDisponibilidad } from '../../hooks/useDisponibilidad';
import { citasApi } from '../../servicios/citasApi';

export default function GestorDisponibilidad() {
  const { bloques, fetchBloques, loading } = useDisponibilidad();
  // Se obtiene del token decodificado normalmente, aquí mockeado
  const psicologoId = localStorage.getItem('user_id') || 'PSICOLOGO_ID_AQUI'; 
  
  const [nuevoBloque, setNuevoBloque] = useState({
    dia_semana: 0,
    hora_inicio: '09:00',
    hora_fin: '17:00',
    duracion_slot: 50
  });

  useEffect(() => {
    if (psicologoId) fetchBloques(psicologoId);
  }, [psicologoId, fetchBloques]);

  const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

  const handleCrear = async (e) => {
    e.preventDefault();
    try {
      await citasApi.crearBloque(nuevoBloque);
      fetchBloques(psicologoId);
    } catch (err) {
      alert("Error al crear disponibilidad");
    }
  };

  const handleEliminar = async (id) => {
    if(window.confirm('¿Eliminar este bloque horario?')) {
      await citasApi.eliminarBloque(id);
      fetchBloques(psicologoId);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6 dark:text-white">Gestión de Disponibilidad</h1>

      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-8">
        <h2 className="text-xl font-semibold mb-4 dark:text-white">Agregar Bloque Horario</h2>
        <form onSubmit={handleCrear} className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
          <div>
            <label className="block text-sm mb-1 dark:text-gray-300">Día</label>
            <select 
              value={nuevoBloque.dia_semana}
              onChange={e => setNuevoBloque({...nuevoBloque, dia_semana: parseInt(e.target.value)})}
              className="w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {DIAS.map((dia, i) => <option key={i} value={i}>{dia}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1 dark:text-gray-300">Hora Inicio</label>
            <input type="time" value={nuevoBloque.hora_inicio} onChange={e => setNuevoBloque({...nuevoBloque, hora_inicio: e.target.value})} className="w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white" required />
          </div>
          <div>
            <label className="block text-sm mb-1 dark:text-gray-300">Hora Fin</label>
            <input type="time" value={nuevoBloque.hora_fin} onChange={e => setNuevoBloque({...nuevoBloque, hora_fin: e.target.value})} className="w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white" required />
          </div>
          <div>
            <label className="block text-sm mb-1 dark:text-gray-300">Duración (min)</label>
            <input type="number" value={nuevoBloque.duracion_slot} onChange={e => setNuevoBloque({...nuevoBloque, duracion_slot: parseInt(e.target.value)})} className="w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white" required min="15" step="5" />
          </div>
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 h-10">
            Añadir
          </button>
        </form>
      </div>

      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold mb-4 dark:text-white">Tus Horarios Configurados</h2>
        {loading ? <p>Cargando...</p> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b dark:border-gray-700">
                  <th className="py-2 dark:text-gray-300">Día</th>
                  <th className="py-2 dark:text-gray-300">Horario</th>
                  <th className="py-2 dark:text-gray-300">Duración slot</th>
                  <th className="py-2 dark:text-gray-300">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {bloques.map(b => (
                  <tr key={b.id} className="border-b dark:border-gray-700">
                    <td className="py-3 font-medium dark:text-gray-200">{DIAS[b.dia_semana]}</td>
                    <td className="py-3 dark:text-gray-300">{b.hora_inicio.substring(0,5)} - {b.hora_fin.substring(0,5)}</td>
                    <td className="py-3 dark:text-gray-300">{b.duracion_slot} min</td>
                    <td className="py-3">
                      <button onClick={() => handleEliminar(b.id)} className="text-red-500 hover:text-red-700 text-sm font-medium">Eliminar</button>
                    </td>
                  </tr>
                ))}
                {bloques.length === 0 && (
                  <tr><td colSpan="4" className="py-4 text-center text-gray-500">No hay bloques configurados.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
