// Archivo: TablaAuditoria.jsx
// Descripción: Panel de Auditoría simplificado, elegante y con autocompletado inteligente.
// Módulo: Frontend

import { useState, useMemo } from "react";
import { Download, ExternalLink, Filter, Info, Search, XCircle, Activity, FileJson, FileText, CheckCircle, XOctagon, RefreshCw } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip, XAxis, YAxis, PieChart, Pie, Cell } from "recharts";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

const COLORS = ['#3b82f6', '#10b981', '#f43f5e', '#f59e0b', '#8b5cf6', '#06b6d4', '#64748b'];

const formatearFechaHora = (valor) => {
  if (!valor) return "Sin fecha";
  const valorUTC = valor.endsWith('Z') || valor.includes('+') ? valor : `${valor}Z`;
  const fecha = new Date(valorUTC);
  if (Number.isNaN(fecha.getTime())) return "Sin fecha";
  return new Intl.DateTimeFormat("es-EC", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"
  }).format(fecha);
};

export default function TablaAuditoria({ serieDiaria, eventos, onRefresh }) {
  const [filtroUsuario, setFiltroUsuario] = useState("");
  const [filtroModulo, setFiltroModulo] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [eventoAnalisis, setEventoAnalisis] = useState(null);
  const [refrescando, setRefrescando] = useState(false);

  const ejecutarRefrescar = async () => {
    if (!onRefresh) return;
    setRefrescando(true);
    try {
      await onRefresh();
    } finally {
      setRefrescando(false);
    }
  };

  const eventosFiltrados = useMemo(() => {
    if (!eventos) return [];
    return eventos.filter(evento => {
      const cumpleUsuario = !filtroUsuario || (evento.actor_email || "").toLowerCase().includes(filtroUsuario.toLowerCase());
      const cumpleModulo = !filtroModulo || evento.modulo === filtroModulo;
      const cumpleEstado = !filtroEstado || evento.status === filtroEstado;
      return cumpleUsuario && cumpleModulo && cumpleEstado;
    });
  }, [eventos, filtroUsuario, filtroModulo, filtroEstado]);

  // Lista única de correos para el datalist (Autocompletado)
  const correosUnicos = useMemo(() => {
    return Array.from(new Set((eventos || []).map(e => e.actor_email).filter(Boolean)));
  }, [eventos]);

  const modulosDisponibles = useMemo(() => {
    return Array.from(new Set((eventos || []).map(e => e.modulo).filter(Boolean)));
  }, [eventos]);

  // Gráfica: Tendencia 7 Días
  const datosGrafica = useMemo(() => {
    return [...(serieDiaria || [])].reverse().map(item => ({
      ...item,
      fechaCorta: item.fecha.slice(5)
    }));
  }, [serieDiaria]);

  // Gráfica: Distribución de Eventos
  const datosPastel = useMemo(() => {
    const conteo = {};
    eventosFiltrados.forEach(evt => {
      const etiqueta = evt.accion || evt.event_type;
      conteo[etiqueta] = (conteo[etiqueta] || 0) + 1;
    });
    return Object.entries(conteo)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6);
  }, [eventosFiltrados]);

  const descargarExcel = () => {
    if (eventosFiltrados.length === 0) return alert("No hay eventos para exportar.");
    const datosExcel = eventosFiltrados.map(evt => ({
      "ID": evt.id,
      "Fecha Local": formatearFechaHora(evt.created_at),
      "Estado": evt.status,
      "Severidad": evt.severidad || "Baja",
      "Módulo": evt.modulo || "Sistema",
      "Acción": evt.accion || evt.event_type,
      "Actor (Email)": evt.actor_email || "N/A",
      "Origen (IP)": evt.ip_address || "N/A",
      "Descripción": evt.descripcion || "-"
    }));
    const worksheet = XLSX.utils.json_to_sheet(datosExcel);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Auditoria");
    XLSX.writeFile(workbook, `Auditoria_PsicoConecta_${new Date().getTime()}.xlsx`);
  };

  const descargarPDF = () => {
    if (eventosFiltrados.length === 0) return alert("No hay eventos para exportar.");
    const doc = new jsPDF('landscape');
    doc.text("Reporte de Auditoría", 14, 15);
    doc.setFontSize(10);
    doc.text(`Fecha de emisión: ${new Date().toLocaleString()}`, 14, 22);

    const bodyData = eventosFiltrados.map(evt => [
      formatearFechaHora(evt.created_at),
      evt.status === 'success' ? 'OK' : 'Error',
      evt.severidad || 'Baja',
      evt.modulo || 'Sistema',
      evt.accion || evt.event_type,
      evt.actor_email || 'N/A'
    ]);

    doc.autoTable({
      startY: 28,
      head: [['Fecha', 'Estado', 'Severidad', 'Módulo', 'Acción', 'Usuario']],
      body: bodyData,
      theme: 'grid',
      styles: { fontSize: 8 },
      headStyles: { fillColor: [59, 130, 246] }
    });
    doc.save(`Auditoria_${new Date().getTime()}.pdf`);
  };

  const getSeveridadBadge = (sev) => {
    if(sev === "Crítica") return "bg-red-50 text-red-600 border border-red-200 dark:bg-red-900/30 dark:border-red-800 dark:text-red-400";
    if(sev === "Alta") return "bg-orange-50 text-orange-600 border border-orange-200 dark:bg-orange-900/30 dark:border-orange-800 dark:text-orange-400";
    if(sev === "Media") return "bg-yellow-50 text-yellow-600 border border-yellow-200 dark:bg-yellow-900/30 dark:border-yellow-800 dark:text-yellow-400";
    if(sev === "Informativo") return "bg-blue-50 text-blue-600 border border-blue-200 dark:bg-blue-900/30 dark:border-blue-800 dark:text-blue-400";
    return "bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300";
  };

  return (
    <section className="mt-8 flex flex-col gap-6">
      
      {/* CABECERA Y FILTROS PREMIUM */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4 p-6 rounded-[2rem] bg-white dark:bg-slate-900 shadow-sm border border-slate-100 dark:border-slate-800">
        <div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-white flex items-center gap-2">
            <Activity className="text-blue-600" /> Monitoreo y Auditoría
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Supervisa la actividad, rendimiento y seguridad en tiempo real.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          {onRefresh && (
            <button 
              onClick={ejecutarRefrescar} 
              disabled={refrescando}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/60 text-white px-5 py-2.5 rounded-2xl text-sm font-bold transition shadow-sm disabled:cursor-not-allowed"
            >
              <RefreshCw size={16} className={refrescando ? "animate-spin" : ""} />
              {refrescando ? "Refrescando..." : "Refrescar"}
            </button>
          )}
          <button onClick={descargarExcel} className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-2xl text-sm font-bold transition shadow-sm">
            <FileText size={16} /> Excel
          </button>
          <button onClick={descargarPDF} className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-5 py-2.5 rounded-2xl text-sm font-bold transition shadow-sm">
            <FileText size={16} /> PDF
          </button>
        </div>
      </div>

      {/* BARRA DE BÚSQUEDA MÁGICA Y FILTROS */}
      <div className="flex flex-col md:flex-row gap-3">
        <label className="flex items-center gap-3 flex-1 bg-white dark:bg-slate-900 px-5 py-3.5 rounded-[1.5rem] border border-slate-100 dark:border-slate-800 shadow-sm transition-all focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500">
          <Search size={18} className="text-blue-500" />
          <input 
            list="sugerencias-correos"
            value={filtroUsuario} 
            onChange={(e) => setFiltroUsuario(e.target.value)} 
            placeholder="Escribe un correo para buscar..." 
            className="bg-transparent text-base w-full outline-none text-slate-700 dark:text-slate-200 placeholder:text-slate-400" 
          />
          <datalist id="sugerencias-correos">
            {correosUnicos.map(correo => (
              <option key={correo} value={correo} />
            ))}
          </datalist>
          {filtroUsuario && (
            <button onClick={() => setFiltroUsuario("")} className="text-slate-400 hover:text-red-500 transition">
              <XCircle size={18} />
            </button>
          )}
        </label>

        <select 
          value={filtroModulo} 
          onChange={(e) => setFiltroModulo(e.target.value)} 
          className="bg-white dark:bg-slate-900 px-5 py-3.5 rounded-[1.5rem] border border-slate-100 dark:border-slate-800 shadow-sm outline-none text-sm font-bold text-slate-700 dark:text-slate-200 cursor-pointer hover:border-blue-500/50 transition-colors"
        >
          <option value="">Todos los Módulos</option>
          {modulosDisponibles.map(m => <option key={m} value={m}>{m.toUpperCase()}</option>)}
        </select>

        <select 
          value={filtroEstado} 
          onChange={(e) => setFiltroEstado(e.target.value)} 
          className="bg-white dark:bg-slate-900 px-5 py-3.5 rounded-[1.5rem] border border-slate-100 dark:border-slate-800 shadow-sm outline-none text-sm font-bold text-slate-700 dark:text-slate-200 cursor-pointer hover:border-blue-500/50 transition-colors"
        >
          <option value="">Cualquier Estado</option>
          <option value="success">Solo Exitosos</option>
          <option value="failure">Solo Fallidos/Errores</option>
        </select>
      </div>

      {/* GRÁFICAS CLÁSICAS RECUPERADAS */}
      <div className="grid lg:grid-cols-[2fr_1fr] gap-6">
        <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm">
          <h3 className="mb-6 text-sm font-black uppercase tracking-wider text-slate-400">
            Tendencia General (7 días)
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={datosGrafica} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAccesos" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/><stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRegistros" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/><stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorFallos" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3}/><stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" strokeOpacity={0.2} />
                <XAxis dataKey="fechaCorta" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <RechartsTooltip contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                <Area type="monotone" name="Accesos" dataKey="accesos" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorAccesos)" />
                <Area type="monotone" name="Registros" dataKey="registros" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorRegistros)" />
                <Area type="monotone" name="Fallos" dataKey="fallos" stroke="#f43f5e" strokeWidth={3} fillOpacity={1} fill="url(#colorFallos)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm flex flex-col">
          <h3 className="mb-2 text-sm font-black uppercase tracking-wider text-slate-400">
            Distribución de Eventos
          </h3>
          <div className="flex-1 min-h-[200px] w-full flex items-center justify-center relative">
            {datosPastel.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={datosPastel} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value" stroke="none">
                    {datosPastel.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                  </Pie>
                  <RechartsTooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : <p className="text-sm text-slate-400">Sin datos para graficar.</p>}
          </div>
        </div>
      </div>

      {/* TABLA PRINCIPAL LIMPIA Y ELEGANTE */}
      <div className="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <h3 className="text-lg font-black text-slate-900 dark:text-white">Últimos Registros</h3>
          <span className="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 px-3 py-1 rounded-full text-xs font-bold">
            Mostrando {eventosFiltrados.length} eventos
          </span>
        </div>
        <div className="overflow-x-auto min-h-[500px]">
          <table className="w-full min-w-[1000px] text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/50 text-[11px] uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-6 py-4 font-black">Estado / Severidad</th>
                <th className="px-6 py-4 font-black">Acción</th>
                <th className="px-6 py-4 font-black">Módulo</th>
                <th className="px-6 py-4 font-black">Usuario Actor</th>
                <th className="px-6 py-4 font-black">Fecha Local</th>
                <th className="px-6 py-4 text-right font-black">Detalles</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {eventosFiltrados.map((evento) => (
                <tr key={evento.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition group">
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-2 items-start">
                      <div className="flex items-center gap-1.5">
                        {evento.status === 'success' ? <CheckCircle size={14} className="text-emerald-500" /> : <XOctagon size={14} className="text-red-500" />}
                        <span className="font-bold text-[11px] uppercase text-slate-700 dark:text-slate-300">{evento.status === 'success' ? 'Exitoso' : 'Fallo'}</span>
                      </div>
                      <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full ${getSeveridadBadge(evento.severidad || 'Baja')}`}>
                        {evento.severidad || 'Baja'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <p className="font-semibold text-slate-900 dark:text-slate-100">{evento.accion || evento.event_type}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">{evento.canal || 'API'} • {evento.ip_address || 'IP Oculta'}</p>
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-2.5 py-1 rounded-lg text-xs font-bold uppercase">
                      {evento.modulo || 'Sistema'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-blue-600 dark:text-blue-400 font-bold truncate max-w-[200px]">{evento.actor_email || "Anónimo"}</p>
                    {evento.rol && <p className="text-[10px] uppercase font-black text-slate-400 mt-1">{evento.rol}</p>}
                  </td>
                  <td className="px-6 py-4 text-slate-500 dark:text-slate-400 text-xs whitespace-nowrap">
                    {formatearFechaHora(evento.created_at)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button onClick={() => setEventoAnalisis(evento)} className="inline-flex items-center gap-1.5 bg-white border border-slate-200 shadow-sm hover:bg-slate-50 hover:border-blue-300 text-slate-700 dark:bg-slate-900 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:border-blue-500/50 px-4 py-2 rounded-xl text-xs font-bold transition">
                      <ExternalLink size={14} className="text-blue-500" /> Analizar
                    </button>
                  </td>
                </tr>
              ))}
              {eventosFiltrados.length === 0 && (
                <tr><td colSpan="6" className="py-20 text-center text-slate-400 font-medium"><Search size={32} className="mx-auto mb-3 opacity-20" /> No se encontraron eventos con este filtro.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL LATERAL DE DETALLES TÉCNICOS */}
      {eventoAnalisis && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/40 backdrop-blur-sm transition-all">
          <div className="w-full max-w-lg bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col animate-in slide-in-from-right border-l border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
              <div>
                <h3 className="text-xl font-black flex items-center gap-2 dark:text-white"><FileJson className="text-blue-500"/> Ficha Técnica</h3>
                <p className="text-xs text-slate-500 mt-1">Ref ID: {eventoAnalisis.id} • {formatearFechaHora(eventoAnalisis.created_at)}</p>
              </div>
              <button onClick={() => setEventoAnalisis(null)} className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition"><XCircle size={24} className="text-slate-400" /></button>
            </div>
            
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              
              <div className="bg-blue-50 dark:bg-blue-900/20 p-5 rounded-2xl border border-blue-100 dark:border-blue-800/50">
                <p className="text-xs font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-2 flex items-center gap-2"><Info size={14}/> Recomendación</p>
                <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  {eventoAnalisis.status === 'success' 
                    ? "Evento finalizado correctamente. No se requiere intervención técnica."
                    : eventoAnalisis.severidad === 'Crítica' ? "URGENTE: Fallo grave en el servidor. Inspeccione inmediatamente los logs de backend."
                    : "Advertencia: El usuario experimentó un fallo controlable. Considere monitorear reincidencias desde la misma IP."}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <p className="text-[10px] uppercase font-black tracking-wider text-slate-400">Endpoint API</p>
                  <p className="font-mono text-xs font-bold text-slate-700 dark:text-slate-300 mt-2 truncate" title={eventoAnalisis.endpoint}>{eventoAnalisis.endpoint || 'N/A'}</p>
                </div>
                <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <p className="text-[10px] uppercase font-black tracking-wider text-slate-400">Código HTTP</p>
                  <p className="font-mono text-xs font-bold text-slate-700 dark:text-slate-300 mt-2">{eventoAnalisis.codigo_respuesta || 'N/A'}</p>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-black text-sm uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">Descripción del Evento</h4>
                <p className="text-sm font-medium text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/30 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  {eventoAnalisis.descripcion || "Sin descripción proporcionada por el controlador."}
                </p>
              </div>

              <div className="space-y-3">
                <h4 className="font-black text-sm uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">Entorno del Cliente</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800"><p className="text-[10px] font-black uppercase text-slate-400">IP ORIGEN</p><p className="font-mono text-xs font-bold mt-2 dark:text-slate-300">{eventoAnalisis.ip_address || 'N/A'}</p></div>
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800"><p className="text-[10px] font-black uppercase text-slate-400">LATENCIA</p><p className="font-mono text-xs font-bold mt-2 dark:text-slate-300">{eventoAnalisis.tiempo_respuesta_ms ? `${eventoAnalisis.tiempo_respuesta_ms} ms` : 'N/A'}</p></div>
                </div>
                <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800"><p className="text-[10px] font-black uppercase text-slate-400">USER AGENT</p><p className="font-mono text-[10px] mt-2 text-slate-500 break-words">{eventoAnalisis.user_agent || 'N/A'}</p></div>
              </div>

              <div className="space-y-3">
                <h4 className="font-black text-sm uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">Payload Raw (JSON)</h4>
                <pre className="text-[11px] font-mono text-emerald-400 bg-slate-950 p-4 rounded-xl overflow-x-auto shadow-inner">
                  {JSON.stringify(eventoAnalisis.detail || {}, null, 2)}
                </pre>
              </div>

            </div>
          </div>
        </div>
      )}
    </section>
  );
}
