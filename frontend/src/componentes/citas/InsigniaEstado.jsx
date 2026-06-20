import React from 'react';

const ESTADO_STYLES = {
  PENDIENTE:    'bg-yellow-100 text-yellow-800 border-yellow-300',
  CONFIRMADA:   'bg-green-100  text-green-800  border-green-300',
  REPROGRAMADA: 'bg-blue-100   text-blue-800   border-blue-300',
  CANCELADA:    'bg-red-100    text-red-800    border-red-300',
  COMPLETADA:   'bg-gray-100   text-gray-700   border-gray-300',
  NO_ASISTIDA:  'bg-orange-100 text-orange-800 border-orange-300',
};

const InsigniaEstado = ({ estado }) => {
  const styles = ESTADO_STYLES[estado] || 'bg-gray-100 text-gray-800 border-gray-300';
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles}`}>
      {estado.replace('_', ' ')}
    </span>
  );
};

export default InsigniaEstado;
