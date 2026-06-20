import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { citasApi } from '../../servicios/citasApi';
import { useCitas } from '../../hooks/useCitas';
import InsigniaEstado from '../../componentes/citas/InsigniaEstado';

export default function PaginaDetalleCita() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { cambiarEstado, loading: accionLoading } = useCitas();
  const [cita, setCita] = useState(null);
  const [loading, setLoading] = useState(true);

  const cargarCita = async () => {
    try {
      const res = await citasApi.getDetalle(id);
      setCita(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCita();
  }, [id]);

  const handleCancelar = async () => {
    if (window.confirm('¿Seguro que deseas cancelar esta cita?')) {
      await cambiarEstado(id, 'cancelar', { motivo: 'Cancelación manual por el usuario' });
      cargarCita();
    }
  };

  const handleConfirmar = async () => {
    await cambiarEstado(id, 'confirmar');
    cargarCita();
  };

  if (loading) return <div className="p-8 text-center">Cargando detalles...</div>;
  if (!cita) return <div className="p-8 text-center text-red-500">Cita no encontrada</div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <button onClick={() => navigate(-1)} className="mb-4 text-blue-600 hover:underline">
        &larr; Volver
      </button>

      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-start mb-6 border-b pb-4 dark:border-gray-700">
          <div>
            <h1 className="text-2xl font-bold dark:text-white">Detalle de Cita</h1>
            <p className="text-gray-500 dark:text-gray-400">ID: {cita.id}</p>
          </div>
          <InsigniaEstado estado={cita.estado} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase">Fecha y Hora</h3>
            <p className="text-lg dark:text-white">
              {new Date(cita.fecha_hora_inicio).toLocaleString()}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase">Modalidad</h3>
            <p className="text-lg dark:text-white">{cita.modalidad}</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase">Paciente ID</h3>
            <p className="text-md font-mono dark:text-gray-300">{cita.paciente_id}</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase">Psicólogo ID</h3>
            <p className="text-md font-mono dark:text-gray-300">{cita.psicologo_id}</p>
          </div>
        </div>

        {cita.motivo_consulta && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">Motivo de consulta</h3>
            <p className="bg-gray-50 dark:bg-gray-700 p-4 rounded dark:text-gray-200">{cita.motivo_consulta}</p>
          </div>
        )}

        <div className="flex gap-4 pt-4 border-t dark:border-gray-700">
          {cita.estado === 'PENDIENTE' && (
            <button 
              onClick={handleConfirmar} disabled={accionLoading}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Confirmar Cita (Si es Psicólogo)
            </button>
          )}
          
          {['PENDIENTE', 'CONFIRMADA', 'REPROGRAMADA'].includes(cita.estado) && (
            <button 
              onClick={handleCancelar} disabled={accionLoading}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Cancelar Cita
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
