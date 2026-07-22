import React from 'react';
import { Heart, Activity, ShieldCheck, AlertCircle, Cpu } from 'lucide-react';

export default function TarjetaTelemetriaCita({ cita }) {
  if (!cita) return null;

  // Extraer datos de telemetría si están incrustados en motivo_consulta o en objeto telemetria
  const motivoStr = cita.motivo_consulta || '';
  const matchBpm = motivoStr.match(/([0-9.]+)\s*BPM/i);
  const matchEstres = motivoStr.match(/Nivel Estrés:\s*([^|\]]+)/i);
  const matchEstado = motivoStr.match(/Ritmo[^|\]]+/i);

  const bpm = matchBpm ? matchBpm[1] : (cita.telemetria?.bpm_promedio || null);
  const estres = matchEstres ? matchEstres[1].trim() : (cita.telemetria?.nivel_estres || 'Normal');
  const estado = matchEstado ? matchEstado[0].trim() : (cita.telemetria?.estado_cardiaco || 'Ritmo Cardíaco Registrado');

  // Si no hay datos de telemetría registrados en la cita, no renderizar la tarjeta
  if (!bpm && !cita.telemetria) return null;

  const esElevado = Number(bpm) > 80;

  return (
    <div className="mb-6 overflow-hidden rounded-3xl border border-pink-200 bg-gradient-to-br from-pink-50/70 via-white to-purple-50/40 p-6 shadow-sm dark:border-pink-900/50 dark:from-slate-900 dark:via-slate-850 dark:to-pink-950/20">
      <div className="flex items-center justify-between border-b border-pink-100 pb-4 dark:border-pink-900/40">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-pink-500/10 text-pink-600 dark:bg-pink-500/20 dark:text-pink-400">
            <Heart className="h-5 w-5 animate-pulse text-pink-500" />
          </span>
          <div>
            <span className="text-[10px] font-black uppercase tracking-wider text-pink-500 dark:text-pink-400 flex items-center gap-1">
              <Cpu className="h-3 w-3" /> Telemetría IoT Cardíaca (Simulación)
            </span>
            <h3 className="text-base font-black text-slate-900 dark:text-white">
              Ritmo Cardíaco Pre-Consulta
            </h3>
          </div>
        </div>
        <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-extrabold ${
          esElevado
            ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
            : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
        }`}>
          {esElevado ? <AlertCircle className="h-3.5 w-3.5" /> : <ShieldCheck className="h-3.5 w-3.5" />}
          {estado}
        </span>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {/* BPM */}
        <div className="rounded-2xl border border-pink-100 bg-white p-4 dark:border-slate-800 dark:bg-slate-800/80 shadow-xs">
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Frecuencia Cardíaca</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-3xl font-black text-pink-600 dark:text-pink-400">{bpm}</span>
            <span className="text-xs font-bold text-slate-500">BPM</span>
          </div>
        </div>

        {/* Nivel de Estrés */}
        <div className="rounded-2xl border border-pink-100 bg-white p-4 dark:border-slate-800 dark:bg-slate-800/80 shadow-xs">
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Nivel de Estrés Estimado</span>
          <div className="mt-1 flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-500" />
            <span className="text-lg font-extrabold text-slate-800 dark:text-white">{estres}</span>
          </div>
        </div>

        {/* Indicador de Gráfico sintético en mini sparkline */}
        <div className="rounded-2xl border border-pink-100 bg-white p-4 dark:border-slate-800 dark:bg-slate-800/80 shadow-xs flex flex-col justify-between">
          <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Onda Fotopletismográfica</span>
          <div className="mt-2 h-8 w-full">
            <svg className="h-full w-full stroke-pink-500 fill-none" viewBox="0 0 100 30">
              <path
                d="M 0,15 Q 10,15 15,15 Q 20,5 25,28 Q 30,2 35,18 Q 40,15 50,15 Q 60,15 65,15 Q 70,5 75,28 Q 80,2 85,18 Q 90,15 100,15"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
