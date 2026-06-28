import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import { ResponsiveContainer, LineChart, Line, YAxis } from "recharts";
import { Activity, ArrowLeft, Wifi, WifiOff, Heart, AlertTriangle } from "lucide-react";
import EncabezadoPanel from "./EncabezadoPanel";

export default function DashboardPsicologo() {
  const { patientId } = useParams();
  const [datos, setDatos] = useState([]);
  const [estadoConexion, setEstadoConexion] = useState("conectando");
  const [esp32Conectado, setEsp32Conectado] = useState(false);
  const [bpm, setBpm] = useState(72);
  const [promedio, setPromedio] = useState(0);

  // Referencias para el buffer FIFO optimizado (desacoplado de la renderización directa de React)
  const bufferRef = useRef([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem("psicoconecta_token") || "";
    const host = window.location.hostname;
    
    // Conectamos a través del reverse proxy de Nginx en el puerto 8080
    const wsUrl = `ws://${host}:8080/api/telemetria/ws?token=${token}&patient_id=${patientId}`;
    
    console.log(`[WS] Conectando a ${wsUrl}`);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("[WS] Conexión abierta");
      setEstadoConexion("conectado");
    };

    ws.onmessage = (event) => {
      try {
        const msg = jsonParseSafe(event.data);
        if (!msg) return;

        if (msg.type === "status") {
          setEsp32Conectado(msg.status === "connected");
        } else if (msg.type === "data" && msg.data) {
          const rawValue = Number(msg.data.raw_value);
          if (Number.isNaN(rawValue)) return;

          // Añadir datos a la cola FIFO en la referencia mutable
          const nuevoPunto = {
            index: Date.now() + Math.random(),
            valor: rawValue,
          };

          bufferRef.current.push(nuevoPunto);

          // Límite estricto de 200 elementos para evitar sobrecargar la memoria
          if (bufferRef.current.length > 200) {
            bufferRef.current.shift();
          }
        }
      } catch (err) {
        console.error("[WS] Error al procesar mensaje", err);
      }
    };

    ws.onerror = (err) => {
      console.error("[WS] Error de conexión", err);
      setEstadoConexion("error");
    };

    ws.onclose = () => {
      console.log("[WS] Conexión cerrada");
      setEstadoConexion("desconectado");
      setEsp32Conectado(false);
    };

    // Frame-rate throttler: Actualizar el estado de React cada 60ms (~16 FPS)
    // para evitar que ráfagas de 50Hz saturen el hilo del renderizado del DOM
    const intervalId = setInterval(() => {
      const colaActual = [...bufferRef.current];
      setDatos(colaActual);

      // Calcular promedio dinámico de las lecturas
      if (colaActual.length > 0) {
        const sum = colaActual.reduce((acc, p) => acc + p.valor, 0);
        setPromedio(Math.round(sum / colaActual.length));
        
        // Simular cálculo de frecuencia cardíaca basada en la detección de picos en la cola
        const valores = colaActual.map(c => c.valor);
        const max = Math.max(...valores);
        const min = Math.min(...valores);
        const umbral = min + (max - min) * 0.7; // Umbral de pico del 70%

        let conteoPicos = 0;
        let sobreUmbral = false;
        for (let i = 0; i < valores.length; i++) {
          if (valores[i] > umbral) {
            if (!sobreUmbral) {
              conteoPicos++;
              sobreUmbral = true;
            }
          } else {
            sobreUmbral = false;
          }
        }

        // Teniendo 3-4 segundos de buffer (200 elems a 50Hz = 4s)
        const duracionEstimadaSegundos = (colaActual.length * 20) / 1000;
        if (duracionEstimadaSegundos > 0 && conteoPicos > 0) {
          const bpmCalculado = Math.round((conteoPicos / duracionEstimadaSegundos) * 60);
          if (bpmCalculado >= 50 && bpmCalculado <= 130) {
            setBpm(bpmCalculado);
          }
        }
      }
    }, 60);

    return () => {
      clearInterval(intervalId);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [patientId]);

  const jsonParseSafe = (str) => {
    try {
      return JSON.parse(str);
    } catch {
      return null;
    }
  };

  return (
    <>
      <div className="flex items-center gap-3 mt-4">
        <Link
          to="/psicologo"
          className="flex items-center justify-center h-10 w-10 rounded-2xl bg-white border border-slate-100 text-slate-600 hover:bg-slate-50 transition shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-700"
        >
          <ArrowLeft size={18} />
        </Link>
        <span className="text-sm font-bold text-slate-500 dark:text-slate-400">Volver al panel</span>
      </div>

      <EncabezadoPanel
        etiqueta="Monitoreo IoT en tiempo real"
        titulo={`Señales Biométricas - Paciente #${patientId}`}
        texto="Visualización de telemetría de pulsaciones cardíacas recibidas directamente desde el sensor biométrico."
      />

      {/* Alertas de Estado de Conexión */}
      <section className="mt-6 grid gap-4 md:grid-cols-3">
        <article className="panel p-5 flex items-center gap-4">
          <div className={`p-3 rounded-2xl ${estadoConexion === "conectado" ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400" : "bg-red-50 text-red-600 dark:bg-red-950/30 dark:text-red-400"}`}>
            {estadoConexion === "conectado" ? <Wifi size={24} /> : <WifiOff size={24} />}
          </div>
          <div>
            <p className="text-xs font-bold text-slate-400">Canal de Telemetría</p>
            <p className="text-lg font-black text-slate-900 dark:text-white capitalize">{estadoConexion}</p>
          </div>
        </article>

        <article className="panel p-5 flex items-center gap-4">
          <div className={`p-3 rounded-2xl ${esp32Conectado ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400" : "bg-amber-50 text-amber-600 dark:bg-amber-950/30 dark:text-amber-400"}`}>
            {esp32Conectado ? (
              <div className="h-6 w-6 relative flex items-center justify-center">
                <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </div>
            ) : (
              <AlertTriangle size={24} />
            )}
          </div>
          <div>
            <p className="text-xs font-bold text-slate-400">Placa del Sensor (ESP32)</p>
            <p className="text-lg font-black text-slate-900 dark:text-white">
              {esp32Conectado ? "Conectada" : "Desconectada / Apagada"}
            </p>
          </div>
        </article>

        <article className="panel p-5 flex items-center gap-4">
          <div className="p-3 rounded-2xl bg-red-50 text-red-500 dark:bg-red-950/30 dark:text-red-400">
            <Heart size={24} className={esp32Conectado ? "animate-pulse" : ""} />
          </div>
          <div>
            <p className="text-xs font-bold text-slate-400">Pulsaciones estimadas</p>
            <p className="text-lg font-black text-slate-900 dark:text-white">
              {esp32Conectado ? `${bpm} BPM` : "--"}
            </p>
          </div>
        </article>
      </section>

      {/* Gráfico en Tiempo Real */}
      <section className="mt-6 panel p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-2">
          <div>
            <h2 className="text-lg font-black text-slate-900 dark:text-white">Gráfico de Onda Cardíaca (ECG)</h2>
            <p className="text-xs text-slate-400">
              Frecuencia de muestreo: 50Hz (50 muestras/segundo) · Datos mostrados en ventana de 4s
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-bold text-slate-500">
            <div>
              Promedio de lectura: <span className="text-slate-900 dark:text-white font-black">{promedio}</span>
            </div>
            <div>
              Muestras en buffer: <span className="text-slate-900 dark:text-white font-black">{datos.length}/200</span>
            </div>
          </div>
        </div>

        {!esp32Conectado ? (
          <div className="h-96 rounded-2xl bg-slate-50 flex flex-col items-center justify-center p-6 border border-dashed border-slate-200 dark:bg-slate-800/40 dark:border-slate-700">
            <AlertTriangle size={48} className="text-amber-500 mb-3" />
            <h3 className="text-md font-bold text-slate-800 dark:text-slate-200">Esperando conexión de la placa ESP32</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm text-center">
              Enciende el dispositivo del paciente. Los datos de telemetría comenzarán a graficarse de forma automática en cuanto se establezca enlace.
            </p>
          </div>
        ) : (
          <div className="h-96 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={datos} margin={{ top: 20, right: 5, left: -20, bottom: 5 }}>
                <YAxis domain={["dataMin - 100", "dataMax + 100"]} hide />
                <Line
                  type="monotone"
                  dataKey="valor"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>
    </>
  );
}
