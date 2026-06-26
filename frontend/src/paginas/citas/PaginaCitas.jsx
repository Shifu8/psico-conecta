import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCitas } from '../../hooks/useCitas';
import TarjetaCita from '../../componentes/citas/TarjetaCita';
import { usarAutenticacion } from '../../contexto/ContextoAutenticacion';
import api from '../../servicios/api';
import { useState } from 'react';

export default function PaginaCitas() {
  const { citas, loading, error, fetchMisCitas, fetchTodasLasCitas } = useCitas();
  const navigate = useNavigate();
  const { usuario } = usarAutenticacion();
  const esPsicologo = usuario?.role === "PSYCHOLOGIST" || usuario?.role?.name === "PSYCHOLOGIST";
  const esAdmin = usuario?.role === "ADMIN" || usuario?.role?.name === "ADMIN";

  const [psicologos, setPsicologos] = useState([]);
  const [pacientes, setPacientes] = useState([]);

  useEffect(() => {
    if (esAdmin) {
      fetchTodasLasCitas({ estado: 'CONFIRMADA' });
    } else {
      fetchMisCitas();
    }
    
    let activo = true;
    if (esAdmin) {
      api.get('/api/usuarios')
        .then(res => {
          if (activo) {
            const usuarios = res.data.users || [];
            setPsicologos(usuarios.filter(u => u.role === 'PSYCHOLOGIST'));
            setPacientes(usuarios.filter(u => u.role === 'PATIENT'));
          }
        })
        .catch(console.error);
    } else {
      api.get('/api/usuarios/psicologos')
        .then(res => activo && setPsicologos(res.data.psicologos || []))
        .catch(console.error);
    }
    return () => { activo = false; };
  }, [fetchMisCitas, fetchTodasLasCitas, esAdmin]);

  const obtenerNombrePsicologo = (id) => {
    const psi = psicologos.find(p => String(p.id) === String(id));
    return psi ? `${psi.first_name} ${psi.last_name}` : `Psicólogo #${id}`;
  };

  const obtenerNombrePaciente = (id) => {
    const pac = pacientes.find(p => String(p.id) === String(id));
    return pac ? `${pac.first_name} ${pac.last_name}` : `Paciente #${id}`;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold dark:text-white">{esAdmin ? 'Citas Confirmadas' : 'Mis Citas'}</h1>
        {!esPsicologo && !esAdmin && (
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
          {esAdmin ? 'No hay citas confirmadas en el sistema actualmente.' : 'No tienes citas programadas actualmente.'}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {citas.map(cita => (
          <TarjetaCita 
            key={cita.id} 
            cita={{...cita, nombrePsicologo: obtenerNombrePsicologo(cita.psicologo_id), nombrePaciente: obtenerNombrePaciente(cita.paciente_id)}} 
            esPsicologo={esPsicologo}
            esAdmin={esAdmin}
            onClick={() => navigate(`/citas/${cita.id}`)}
          />
        ))}
      </div>
    </div>
  );
}
