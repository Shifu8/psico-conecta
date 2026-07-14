import React from 'react';
import { Clock } from 'lucide-react';

const SlotSelector = ({ slots, loading, error, onSelectSlot, selectedSlot }) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-slate-400">
        <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-slate-200 border-t-blue-600 dark:border-slate-700 dark:border-t-blue-400" />
        <p className="mt-4 text-sm font-semibold">Cargando horarios disponibles...</p>
      </div>
    );
  }

  if (error) {
    return <div className="rounded-2xl bg-red-50 p-4 text-center text-sm font-semibold text-red-600 dark:bg-red-950/30 dark:text-red-300">{error}</div>;
  }

  if (!slots || slots.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-slate-400 dark:text-slate-500">
        <Clock size={32} className="mb-3 opacity-40" />
        <p className="text-sm font-semibold">No hay horarios disponibles para esta fecha.</p>
        <p className="mt-1 text-xs">Elige otra fecha; puede estar fuera del horario laboral o bloqueada por el administrador.</p>
      </div>
    );
  }

  // Separar slots por bloque: mañana (antes de 12:00) y tarde (14:00 en adelante)
  const slotsMañana = slots.filter(s => s.hora_inicio < '12:00:00');
  const slotsTarde = slots.filter(s => s.hora_inicio >= '12:00:00');

  const renderBloque = (titulo, listaSlots, colorAccent) => {
    if (listaSlots.length === 0) return null;
    return (
      <div className="mb-4 last:mb-0">
        <p className="mb-3 text-xs font-black uppercase tracking-wider text-slate-400 dark:text-slate-500">{titulo}</p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          {listaSlots.map((slot, index) => {
            const isSelected = selectedSlot && selectedSlot.hora_inicio === slot.hora_inicio;
            const disponible = slot.disponible !== false;
            const horaInicio = slot.hora_inicio.substring(0, 5);
            const horaFin = slot.hora_fin.substring(0, 5);

            return (
              <button
                key={index}
                onClick={() => disponible && onSelectSlot(slot)}
                disabled={!disponible}
                className={`group relative flex flex-col items-center rounded-2xl border-2 px-3 py-3 text-sm font-bold transition-all duration-200 ${
                  !disponible
                    ? 'cursor-not-allowed border-slate-100 bg-slate-50 text-slate-300 line-through dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-600'
                    : isSelected
                      ? `border-blue-500 bg-blue-600 text-white shadow-lg shadow-blue-500/25 dark:border-blue-400 dark:bg-blue-600`
                      : `border-slate-200 bg-white text-slate-700 hover:border-blue-300 hover:bg-blue-50 hover:shadow-md dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-blue-500 dark:hover:bg-slate-700`
                }`}
              >
                <Clock size={16} className={`mb-1.5 ${!disponible ? 'opacity-30' : isSelected ? 'text-blue-100' : 'text-slate-400 group-hover:text-blue-500 dark:text-slate-500'}`} />
                <span className="text-base font-black">{horaInicio}</span>
                <span className={`mt-0.5 text-[10px] ${!disponible ? 'text-slate-300 dark:text-slate-600' : isSelected ? 'text-blue-200' : 'text-slate-400 dark:text-slate-500'}`}>
                  {disponible ? `a ${horaFin}` : 'Ocupado'}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div>
      {renderBloque('🌅 Mañana', slotsMañana, 'blue')}
      {renderBloque('🌇 Tarde', slotsTarde, 'indigo')}
    </div>
  );
};

export default SlotSelector;
