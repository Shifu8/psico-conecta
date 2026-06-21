import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCitas } from '../../hooks/useCitas';
import TarjetaCita from '../../componentes/citas/TarjetaCita';
import { usarAutenticacion } from '../../contexto/ContextoAutenticacion';
import api from '../../servicios/api';
import { useState } from 'react';

export default function PaginaCitas() {
  const { citas, loading, error, fetchMisCitas } = useCitas();
  const navigate = useNavigate();
  const { usuario } = usarAutenticacion();
  const esPsicologo = usuario?.role === "PSYCHOLOGIST" || usuario?.role?.name === "PSYCHOLOGIST";

  const [psicologos, setPsicologos] = useState([]);

  useEffect(() => {
    fetchMisCitas();
    let activo = true;
    api.get('/api/usuarios/psicologos')
      .then(res => activo && setPsicologos(res.data.psicologos || []))
      .catch(console.error);
    return () => { activo = false; };
  }, [fetchMisCitas]);

  const obtenerNombrePsicologo = (id) => {
    const psi = psicologos.find(p => String(p.id) === String(id));
    return psi ? `${psi.first_name} ${psi.last_name}` : `Psicólogo #${id}`;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold dark:text-white">Mis Citas</h1>
        {!esPsicologo && (
          <button 
            onClick={() => navigate('/citas/agendar')}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            Agendar Nueva Cita
          </button>
        )}
      </div>

      {loading && <p>Cargando citas...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && citas.length === 0 && (
        <div className="bg-gray-50 dark:bg-gray-800 p-8 rounded-lg text-center text-gray-500">
          No tienes citas programadas actualmente.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {citas.map(cita => (
          <TarjetaCita 
            key={cita.id} 
            cita={{...cita, nombrePsicologo: obtenerNombrePsicologo(cita.psicologo_id)}} 
            esPsicologo={esPsicologo}
            onClick={() => navigate(`/citas/${cita.id}`)}
          />
        ))}
      </div>
    </div>
  );
}
