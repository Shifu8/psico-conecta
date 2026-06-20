import React from 'react';
import InsigniaEstado from './InsigniaEstado';

const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const TarjetaCita = ({ cita, onClick, esPsicologo }) => {
  return (
    <div 
      className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700"
      onClick={() => onClick(cita)}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg dark:text-white">
          {formatDate(cita.fecha_hora_inicio)} a las {formatTime(cita.fecha_hora_inicio)}
        </h3>
        <InsigniaEstado estado={cita.estado} />
      </div>
      
      <div className="text-sm text-gray-600 dark:text-gray-300">
        <p className="mb-1">
          <span className="font-medium">{esPsicologo ? 'Paciente' : 'Psicólogo'}:</span>{' '}
          {esPsicologo ? cita.paciente_id : cita.psicologo_id} {/* En el futuro, resolver a nombres reales */}
        </p>
        <p>
          <span className="font-medium">Modalidad:</span> {cita.modalidad}
        </p>
      </div>
    </div>
  );
};

export default TarjetaCita;
