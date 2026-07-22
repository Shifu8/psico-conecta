import React, { useState, useEffect, useRef } from 'react';
import { Heart, Activity, CheckCircle2, RefreshCw, Play, Fingerprint, Clock, Sparkles } from 'lucide-react';

export default function SimuladorSensorRitmo({ onMedicionCompletada, datosPrevios = null }) {
  const [midiendo, setMidiendo] = useState(false);
  const [completado, setCompletado] = useState(!!datosPrevios);
  const [segundosRestantes, setSegundosRestantes] = useState(15);
  const [bpmActual, setBpmActual] = useState(0);
  const [resultado, setResultado] = useState(datosPrevios || null);

  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const duracionTotal = 15;

  useEffect(() => {
    let timer;
    if (midiendo && segundosRestantes > 0) {
      timer = setInterval(() => {
        setSegundosRestantes((prev) => prev - 1);
      }, 1000);
    } else if (segundosRestantes === 0 && midiendo) {
      finalizarMedicion();
    }
    return () => clearInterval(timer);
  }, [midiendo, segundosRestantes]);

  const iniciarMedicion = () => {
    setMidiendo(true);
    setCompletado(false);
    setSegundosRestantes(duracionTotal);
    setResultado(null);
    setBpmActual(72);
  };

  const finalizarMedicion = () => {
    setMidiendo(false);
    setCompletado(true);

    const bpmFinal = Math.floor(Math.random() * (85 - 68 + 1)) + 68;
    const estresNivel = bpmFinal > 80 ? 'Moderado' : 'Normal / Relajado';

    const datosFinales = {
      bpm_promedio: bpmFinal,
      nivel_estres: estresNivel,
      estado_cardiaco: bpmFinal > 80 ? 'Ritmo Levemente Elevado' : 'Ritmo Cardíaco Normal',
      duracion_segundos: duracionTotal,
      fecha_captura: new Date().toISOString(),
      simulado: true
    };

    setResultado(datosFinales);
    if (onMedicionCompletada) {
      onMedicionCompletada(datosFinales);
    }
  };

  // Renderizar gráfico de pulso PPG en el Canvas
  useEffect(() => {
    if (!midiendo || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let width = (canvas.width = canvas.offsetWidth);
    let height = (canvas.height = canvas.offsetHeight);

    let x = 0;
    let t = 0;
    const points = [];

    const draw = () => {
      t += 0.05;

      // Calcular valor de la onda PPG (sístole + diástole + ruido)
      const bpm = 75;
      const freq = bpm / 60;
      const phase = 2 * Math.PI * freq * t;
      const sistole = Math.exp(-Math.pow(Math.sin(phase / 2), 2) * 12);
      const dicrota = 0.35 * Math.exp(-Math.pow(Math.sin((phase - 0.8) / 2), 2) * 20);

      const yVal = height / 2 - (sistole + dicrota) * (height * 0.35);

      points.push({ x, y: yVal });
      if (points.length > width / 2) points.shift();

      ctx.clearRect(0, 0, width, height);

      // Dibujar cuadrícula tenue
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.1)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let gridX = 0; gridX < width; gridX += 20) {
        ctx.moveTo(gridX, 0);
        ctx.lineTo(gridX, height);
      }
      for (let gridY = 0; gridY < height; gridY += 20) {
        ctx.moveTo(0, gridY);
        ctx.lineTo(width, gridY);
      }
      ctx.stroke();

      // Dibujar línea de señal cardíaca
      ctx.strokeStyle = '#ec4899'; // Rosa brillante estilo electrocardiograma
      ctx.lineWidth = 3;
      ctx.shadowBlur = 8;
      ctx.shadowColor = '#ec4899';
      ctx.beginPath();

      for (let i = 0; i < points.length; i++) {
        const point = points[i];
        const currentX = width - (points.length - i) * 2;
        if (i === 0) ctx.moveTo(currentX, point.y);
        else ctx.lineTo(currentX, point.y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Actualizar ritmo cardíaco dinámico
      if (Math.random() < 0.1) {
        setBpmActual(Math.floor(70 + Math.sin(t) * 6 + Math.random() * 3));
      }

      animFrameRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [midiendo]);

  return (
    <div className="rounded-3xl border border-pink-200/60 bg-gradient-to-br from-pink-50/50 via-purple-50/30 to-blue-50/40 p-6 shadow-sm dark:border-pink-900/40 dark:from-slate-900 dark:via-pink-950/20 dark:to-slate-900">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-pink-500/10 text-pink-600 dark:bg-pink-500/20 dark:text-pink-400">
            <Heart className={`h-5 w-5 ${midiendo ? 'animate-bounce text-pink-500' : ''}`} />
          </span>
          <div>
            <h3 className="text-base font-black text-slate-900 dark:text-white flex items-center gap-2">
              Medición de Ritmo Cardíaco
              <span className="rounded-full bg-pink-100 px-2 py-0.5 text-[10px] font-bold text-pink-700 dark:bg-pink-900/60 dark:text-pink-300">
                Simulador IoT
              </span>
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Registra tu pulso cardíaco durante 15 segundos para compartirlo con tu psicólogo.
            </p>
          </div>
        </div>
      </div>

      {/* Estado: No iniciado */}
      {!midiendo && !completado && (
        <div className="mt-6 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-pink-200 bg-white/60 p-6 text-center dark:border-pink-900/40 dark:bg-slate-800/40">
          <div className="relative mb-3">
            <Fingerprint className="h-12 w-12 text-pink-400 dark:text-pink-300 animate-pulse" />
          </div>
          <p className="text-sm font-bold text-slate-700 dark:text-slate-200">
            Sensor listo para medir
          </p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 max-w-sm">
            Presiona el botón para iniciar la prueba simulada de fotopletismografía (PPG).
          </p>
          <button
            type="button"
            onClick={iniciarMedicion}
            className="mt-4 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-pink-500 to-rose-500 px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-pink-500/25 transition-all hover:scale-105 active:scale-95"
          >
            <Play className="h-4 w-4 fill-white" /> Iniciar Medición (15s)
          </button>
        </div>
      )}

      {/* Estado: Midiendo (Animación 15 segundos) */}
      {midiendo && (
        <div className="mt-6 space-y-4">
          <div className="flex items-center justify-between rounded-2xl bg-white/80 p-4 dark:bg-slate-800/80 shadow-sm">
            <div className="flex items-center gap-3">
              <Activity className="h-6 w-6 text-pink-500 animate-pulse" />
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Ritmo Cardíaco</span>
                <p className="text-2xl font-black text-pink-600 dark:text-pink-400">
                  {bpmActual} <span className="text-xs font-bold text-slate-500">BPM</span>
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" /> Tiempo
              </span>
              <p className="text-2xl font-black text-slate-800 dark:text-white">
                00:{segundosRestantes < 10 ? `0${segundosRestantes}` : segundosRestantes}
              </p>
            </div>
          </div>

          {/* Canvas electrocardiograma */}
          <div className="relative h-28 w-full overflow-hidden rounded-2xl border border-pink-200 bg-slate-950 p-2 dark:border-pink-900">
            <canvas ref={canvasRef} className="h-full w-full" />
            <div className="absolute top-2 right-3 flex items-center gap-1.5 rounded-full bg-pink-500/20 px-2 py-0.5 text-[10px] font-bold text-pink-400">
              <span className="h-2 w-2 rounded-full bg-pink-500 animate-ping" /> MEDIENDO EN VIVO
            </div>
          </div>

          {/* Barra de progreso */}
          <div className="h-2 w-full overflow-hidden rounded-full bg-pink-100 dark:bg-pink-950">
            <div
              className="h-full bg-gradient-to-r from-pink-500 to-rose-500 transition-all duration-1000"
              style={{ width: `${((duracionTotal - segundosRestantes) / duracionTotal) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Estado: Completado */}
      {completado && resultado && (
        <div className="mt-6 space-y-4 rounded-2xl bg-emerald-50/80 p-5 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300 font-black text-sm">
              <CheckCircle2 className="h-5 w-5" /> Medición Guardada Correctamente
            </div>
            <button
              type="button"
              onClick={iniciarMedicion}
              className="inline-flex items-center gap-1 text-xs font-bold text-emerald-700 hover:underline dark:text-emerald-300"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Repetir
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 text-center sm:grid-cols-3">
            <div className="rounded-xl bg-white p-3 dark:bg-slate-800 shadow-sm">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Frecuencia Cardíaca</span>
              <p className="text-lg font-black text-pink-600 dark:text-pink-400">
                {resultado.bpm_promedio} <span className="text-xs">BPM</span>
              </p>
            </div>
            <div className="rounded-xl bg-white p-3 dark:bg-slate-800 shadow-sm">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Nivel de Estrés</span>
              <p className="text-sm font-bold text-slate-800 dark:text-white">
                {resultado.nivel_estres}
              </p>
            </div>
            <div className="col-span-2 sm:col-span-1 rounded-xl bg-white p-3 dark:bg-slate-800 shadow-sm">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Estado Diagnóstico</span>
              <p className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                {resultado.estado_cardiaco}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
