import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CalendarDays, Clock, Search, Stethoscope, Send, MessageSquare, Video, MapPin } from 'lucide-react';
import { useDisponibilidad } from '../../hooks/useDisponibilidad';
import { useCitas } from '../../hooks/useCitas';
import SlotSelector from '../../componentes/citas/SlotSelector';
import api from '../../servicios/api';
import AvatarUsuario from '../../componentes/AvatarUsuario';
import SimuladorSensorRitmo from '../../componentes/iot/SimuladorSensorRitmo';

const fechaLocalISO = () => {
  const ahora = new Date();
  const desplazamiento = ahora.getTimezoneOffset() * 60000;
  return new Date(ahora.getTime() - desplazamiento).toISOString().slice(0, 10);
};

export default function PaginaAgendarCita() {
  const { slots, fetchSlots, limpiarSlots, loading: loadingSlots, error: errorSlots } = useDisponibilidad();
  const { agendarCita, loading: agendando } = useCitas();
  const navigate = useNavigate();

  const [fecha, setFecha] = useState('');
  const [psicologoId, setPsicologoId] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [motivo, setMotivo] = useState('');
  const [modalidad, setModalidad] = useState('VIRTUAL');
  const [psicologos, setPsicologos] = useState([]);
  const [loadingPsicologos, setLoadingPsicologos] = useState(true);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const [datosTelemetria, setDatosTelemetria] = useState(null);

  useEffect(() => {
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
      setMensaje('');
      setError('');
      fetchSlots(psicologoId, fecha);
    }
  };

  const handleSeleccionarSlot = (slot) => {
    setSelectedSlot(slot);
  };

  const handleAgendar = async () => {
    if (!selectedSlot) return;

    const fechaHoraInicio = selectedSlot.fecha_hora_inicio || `${fecha}T${selectedSlot.hora_inicio}`;

    let motivoFinal = motivo;
    if (datosTelemetria) {
      const notaIoT = `[Telemetría IoT Cardíaca: ${datosTelemetria.bpm_promedio} BPM | Nivel Estrés: ${datosTelemetria.nivel_estres} | ${datosTelemetria.estado_cardiaco}]`;
      motivoFinal = motivo ? `${motivo}\n\n${notaIoT}` : notaIoT;
    }

    try {
      await agendarCita({
        psicologo_id: Number(psicologoId),
        fecha_hora_inicio: fechaHoraInicio,
        modalidad: modalidad,
        motivo_consulta: motivoFinal
      });
      setMensaje('¡Cita agendada correctamente!');
      setError('');
      setTimeout(() => navigate('/paciente'), 1500);
    } catch (err) {
      console.error('Error al agendar cita:', err.response?.data || err);
      setError(
        err.response?.data?.mensaje ||
        err.response?.data?.message ||
        'No fue posible agendar la cita. Revisa los datos e inténtalo nuevamente.'
      );
      setMensaje('');
    }
  };

  const psicologoSeleccionado = psicologos.find(ps => String(ps.id) === String(psicologoId));

  return (
    <div className="container mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <p className="text-xs font-black uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Agendar</p>
        <h1 className="mt-2 text-3xl font-black text-slate-900 dark:text-white">Nueva Cita</h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Selecciona un profesional, una fecha y el horario que mejor te convenga.
        </p>
      </div>

      {/* Mensajes */}
      {mensaje && (
        <div className="mb-6 rounded-2xl bg-emerald-50 p-4 text-sm font-semibold text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
          {mensaje}
        </div>
      )}
      {error && (
        <div className="mb-6 rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-700 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Formulario de selección */}
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:p-8">
        <form onSubmit={handleBuscarSlots} className="space-y-5">
          {/* Psicólogo */}
          <div>
            <label className="mb-4 flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-400">
              <Stethoscope size={14} /> Selecciona un Profesional
            </label>
            {loadingPsicologos ? (
              <p className="text-sm text-slate-400">Cargando profesionales...</p>
            ) : (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {psicologos.map(ps => {
                  const isSelected = String(ps.id) === String(psicologoId);
                  return (
                    <button
                      key={ps.id}
                      type="button"
                      onClick={() => {
                        setPsicologoId(String(ps.id));
                        setSelectedSlot(null);
                        limpiarSlots();
                      }}
                      className={`group flex flex-col items-center overflow-hidden rounded-2xl border-2 p-4 text-center transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 shadow-md dark:border-blue-400 dark:bg-blue-900/20'
                          : 'border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-slate-600 dark:hover:bg-slate-750'
                      }`}
                    >
                      <AvatarUsuario 
                        usuario={ps} 
                        tamano="lg" 
                        className={`mb-3 !rounded-full transition-transform group-hover:scale-105 ${isSelected ? 'ring-4 ring-blue-200 dark:ring-blue-900' : 'shadow-sm'}`}
                      />
                      <h3 className={`text-sm font-black leading-tight ${isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-slate-900 dark:text-white'}`}>
                        {ps.first_name} {ps.last_name}
                      </h3>
                      <p className={`mt-2 text-[10px] leading-relaxed ${isSelected ? 'text-blue-600/80 dark:text-blue-400/80' : 'text-slate-500 dark:text-slate-400'}`}>
                        Especialista en psicología clínica y bienestar emocional.
                      </p>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Fecha */}
          <div>
            <label className="mb-2 flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-400">
              <CalendarDays size={14} /> Fecha de la cita
            </label>
            <input
              type="date"
              value={fecha}
              onChange={(e) => {
                setFecha(e.target.value);
                setSelectedSlot(null);
                limpiarSlots();
              }}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 outline-none transition-colors focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:border-blue-500 dark:focus:ring-blue-900/30"
              required
              min={fechaLocalISO()}
            />
          </div>

          {/* Botón buscar */}
          <button
            type="submit"
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-xl hover:shadow-blue-500/30 disabled:opacity-50 dark:from-blue-500 dark:to-indigo-500"
            disabled={!psicologoId || !fecha}
          >
            <Search size={16} /> Buscar Horarios Disponibles
          </button>
        </form>
      </div>

      {/* Selector de horarios */}
      {fecha && psicologoId && (
        <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:p-8">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-wider text-slate-400">Horarios</p>
              <h2 className="mt-1 text-xl font-black text-slate-900 dark:text-white">Seleccione un horario</h2>
            </div>
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400">
              <Clock size={20} />
            </span>
          </div>

          <SlotSelector
            slots={slots}
            loading={loadingSlots}
            onSelectSlot={handleSeleccionarSlot}
            selectedSlot={selectedSlot}
            error={errorSlots}
          />

          {/* Confirmación de cita */}
          {selectedSlot && selectedSlot.disponible !== false && (
            <div className="mt-8 space-y-5 border-t border-slate-100 pt-6 dark:border-slate-800">
              {/* Resumen */}
              <div className="rounded-2xl bg-blue-50 p-4 dark:bg-blue-950/30">
                <p className="text-xs font-black uppercase tracking-wider text-blue-500 dark:text-blue-400">Resumen de tu cita</p>
                <div className="mt-3 grid gap-2 text-sm sm:grid-cols-3">
                  <div>
                    <span className="text-slate-500 dark:text-slate-400">Profesional</span>
                    <p className="font-bold text-slate-900 dark:text-white">
                      {psicologoSeleccionado ? `${psicologoSeleccionado.first_name} ${psicologoSeleccionado.last_name}` : `Psicólogo #${psicologoId}`}
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-500 dark:text-slate-400">Fecha</span>
                    <p className="font-bold text-slate-900 dark:text-white">
                      {new Intl.DateTimeFormat('es-EC', { dateStyle: 'long' }).format(new Date(fecha + 'T12:00:00'))}
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-500 dark:text-slate-400">Horario</span>
                    <p className="font-bold text-slate-900 dark:text-white">
                      {selectedSlot.hora_inicio.substring(0, 5)} - {selectedSlot.hora_fin.substring(0, 5)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Motivo */}
              <div>
                <label className="mb-2 flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-400">
                  <MessageSquare size={14} /> Motivo de consulta (opcional)
                </label>
                <textarea
                  value={motivo}
                  onChange={(e) => setMotivo(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition-colors focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:border-blue-500 dark:focus:ring-blue-900/30"
                  rows="3"
                  placeholder="Puedes describir brevemente el motivo de tu consulta..."
                  maxLength={500}
                />
              </div>

              {/* Simulador IoT Sensor de Ritmo Cardíaco */}
              <SimuladorSensorRitmo onMedicionCompletada={(data) => setDatosTelemetria(data)} />

              {/* Modalidad */}
              <div>
                <label className="mb-2 flex items-center gap-2 text-xs font-black uppercase tracking-wider text-slate-400">
                  <MapPin size={14} /> Modalidad de la cita
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setModalidad('VIRTUAL')}
                    className={`flex items-center justify-center gap-2 rounded-xl border-2 px-4 py-3 text-sm font-bold transition-all ${
                      modalidad === 'VIRTUAL'
                        ? 'border-blue-500 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-900/30 dark:text-blue-300'
                        : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
                    }`}
                  >
                    <Video size={16} /> Virtual
                  </button>
                  <button
                    type="button"
                    onClick={() => setModalidad('PRESENCIAL')}
                    className={`flex items-center justify-center gap-2 rounded-xl border-2 px-4 py-3 text-sm font-bold transition-all ${
                      modalidad === 'PRESENCIAL'
                        ? 'border-blue-500 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-900/30 dark:text-blue-300'
                        : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
                    }`}
                  >
                    <MapPin size={16} /> Presencial
                  </button>
                </div>
              </div>

              {/* Botón Agendar */}
              <div className="space-y-4">
                <button
                  onClick={handleAgendar}
                  disabled={agendando}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-emerald-500/20 transition-all hover:shadow-xl hover:shadow-emerald-500/30 disabled:opacity-50"
                >
                  <Send size={16} /> {agendando ? 'Confirmando...' : 'Agendar Cita'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  );
}
