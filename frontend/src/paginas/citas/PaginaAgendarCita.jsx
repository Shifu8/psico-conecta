import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDisponibilidad } from '../../hooks/useDisponibilidad';
import { useCitas } from '../../hooks/useCitas';
import SlotSelector from '../../componentes/citas/SlotSelector';
import api from '../../servicios/api'; // Importamos la api general para usuarios

export default function PaginaAgendarCita() {
  const { slots, fetchSlots, loading: loadingSlots } = useDisponibilidad();
  const { agendarCita, loading: agendando } = useCitas();
  const navigate = useNavigate();

  const [fecha, setFecha] = useState('');
  const [psicologoId, setPsicologoId] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [motivo, setMotivo] = useState('');
  const [psicologos, setPsicologos] = useState([]);
  const [loadingPsicologos, setLoadingPsicologos] = useState(true);

  useEffect(() => {
    // Cargar la lista de psicólogos al montar
    const cargarPsicologos = async () => {
      try {
        const res = await api.get('/api/usuarios/psicologos');
        const filtrados = res.data.psicologos || [];
        setPsicologos(filtrados);
      } catch (error) {
        console.error("Error al cargar psicólogos", error);
      } finally {
        setLoadingPsicologos(false);
      }
    };
    cargarPsicologos();
  }, []);

  const handleBuscarSlots = (e) => {
    e.preventDefault();
    if (psicologoId && fecha) {
      setSelectedSlot(null);
      fetchSlots(psicologoId, fecha);
    }
  };

  const handleAgendar = async () => {
    if (!selectedSlot) return;
    
    // Crear objeto datetime uniendo la fecha y la hora_inicio del slot
    const fechaHoraInicio = new Date(`${fecha}T${selectedSlot.hora_inicio}`).toISOString();
    
    try {
      await agendarCita({
        psicologo_id: psicologoId,
        fecha_hora_inicio: fechaHoraInicio,
        modalidad: 'VIRTUAL',
        motivo_consulta: motivo
      });
      navigate('/citas');
    } catch (err) {
      console.error(err);
      alert('Error al agendar la cita');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6 dark:text-white">Agendar Nueva Cita</h1>
      
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <form onSubmit={handleBuscarSlots} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-gray-300">Psicólogo</label>
            {loadingPsicologos ? (
              <p className="text-sm text-gray-500">Cargando profesionales...</p>
            ) : (
              <select 
                value={psicologoId}
                onChange={(e) => setPsicologoId(e.target.value)}
                className="w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                required
              >
                <option value="">-- Seleccione un profesional --</option>
                {psicologos.map(ps => (
                  <option key={ps.id} value={ps.id}>
                    {ps.first_name} {ps.last_name}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-gray-300">Fecha de la Cita</label>
            <input 
              type="date" 
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              className="w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              required
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
          <button type="submit" className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900 w-full" disabled={!psicologoId}>
            Buscar Horarios Disponibles
          </button>
        </form>
      </div>

      {fecha && psicologoId && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Seleccione un horario</h2>
          <SlotSelector 
            slots={slots} 
            loading={loadingSlots} 
            onSelectSlot={setSelectedSlot} 
            selectedSlot={selectedSlot}
          />

          {selectedSlot && (
            <div className="mt-6 space-y-4 border-t pt-4 dark:border-gray-700">
              <div>
                <label className="block text-sm font-medium mb-1 dark:text-gray-300">Motivo de consulta (opcional)</label>
                <textarea 
                  value={motivo}
                  onChange={(e) => setMotivo(e.target.value)}
                  className="w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  rows="3"
                ></textarea>
              </div>
              <button 
                onClick={handleAgendar}
                disabled={agendando}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full disabled:opacity-50"
              >
                {agendando ? 'Agendando...' : 'Confirmar Cita'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
