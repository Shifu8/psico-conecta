import React from 'react';

const SlotSelector = ({ slots, loading, error, onSelectSlot, selectedSlot }) => {
  if (loading) return <div className="text-center py-4">Cargando horarios disponibles...</div>;
  if (error) return <div className="text-red-500 text-center py-4">{error}</div>;
  if (!slots || slots.length === 0) return <div className="text-center text-gray-500 py-4">No hay horarios disponibles para esta fecha.</div>;

  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
      {slots.map((slot, index) => {
        // Asumiendo que slot.hora_inicio viene como "HH:MM:SS"
        const isSelected = selectedSlot && selectedSlot.hora_inicio === slot.hora_inicio;
        return (
          <button
            key={index}
            onClick={() => onSelectSlot(slot)}
            className={`py-2 px-3 rounded-md text-sm font-medium transition-colors border ${
              isSelected
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-blue-50 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-700'
            }`}
          >
            {slot.hora_inicio.substring(0, 5)}
          </button>
        );
      })}
    </div>
  );
};

export default SlotSelector;
