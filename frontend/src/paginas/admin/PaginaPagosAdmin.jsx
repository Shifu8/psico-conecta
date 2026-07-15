import { CreditCard, LoaderCircle, Plus, ReceiptText, RefreshCw, RotateCcw, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import EstadoPago from "../../componentes/pagos/EstadoPago";
import { mensajeErrorPago, pagosApi } from "../../servicios/servicioPagos";

const dinero = (centavos, moneda = "USD") =>
  (Number(centavos || 0) / 100).toLocaleString("es-EC", { style: "currency", currency: moneda });

const fecha = (valor) => {
  const dato = new Date(valor);
  return Number.isNaN(dato.getTime()) ? "Sin fecha" : dato.toLocaleString("es-EC");
};

export default function PaginaPagosAdmin() {
  const [pagos, setPagos] = useState([]);
  const [tarifas, setTarifas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(null);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [formulario, setFormulario] = useState({ psicologo_id: "", modalidad: "TODAS", monto: "30.00", moneda: "USD" });

  const cargar = async () => {
    setCargando(true);
    setError("");
    try {
      const [pagosResultado, tarifasResultado] = await Promise.all([
        pagosApi.listarTodos(),
        pagosApi.listarTarifas(),
      ]);
      setPagos(pagosResultado);
      setTarifas(tarifasResultado);
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible cargar la administración de pagos."));
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => { cargar(); }, []);

  const resumen = useMemo(() => {
    const cobrados = pagos.filter((item) => ["PAGADO", "REEMBOLSO_PARCIAL", "REEMBOLSADO"].includes(item.estado));
    return {
      total: pagos.length,
      pendientes: pagos.filter((item) => ["PENDIENTE", "CHECKOUT_ABIERTO", "PROCESANDO"].includes(item.estado)).length,
      pagados: pagos.filter((item) => ["PAGADO", "REEMBOLSO_PARCIAL"].includes(item.estado)).length,
      neto: cobrados.reduce((suma, item) => suma + item.monto_centavos - item.reembolsado_centavos, 0),
    };
  }, [pagos]);

  const sincronizarCitas = async () => {
    setProcesando("sincronizar-citas");
    setError("");
    setMensaje("");
    try {
      const resultado = await pagosApi.sincronizarCitas();
      setMensaje(`Sincronización terminada: ${resultado.creadas_o_actualizadas} pagos preparados de ${resultado.procesadas} citas confirmadas.`);
      await cargar();
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible sincronizar las citas existentes."));
    } finally {
      setProcesando(null);
    }
  };

  const crearTarifa = async (evento) => {
    evento.preventDefault();
    const monto = Number(formulario.monto);
    if (!Number.isFinite(monto) || monto < 1) {
      setError("La tarifa debe ser de al menos 1,00 USD.");
      return;
    }
    setProcesando("tarifa-nueva");
    setError("");
    setMensaje("");
    try {
      await pagosApi.crearTarifa({
        psicologo_id: formulario.psicologo_id ? Number(formulario.psicologo_id) : null,
        modalidad: formulario.modalidad,
        monto_centavos: Math.round(monto * 100),
        moneda: formulario.moneda.toUpperCase(),
      });
      setMensaje("Tarifa activada. Las tarifas anteriores del mismo alcance se desactivaron.");
      await cargar();
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible crear la tarifa."));
    } finally {
      setProcesando(null);
    }
  };

  const desactivarTarifa = async (tarifa) => {
    if (!window.confirm("¿Desactivar esta tarifa? Los pagos ya creados conservarán su monto.")) return;
    setProcesando(tarifa.id);
    try {
      await pagosApi.desactivarTarifa(tarifa.id);
      await cargar();
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion));
    } finally {
      setProcesando(null);
    }
  };

  const reembolsar = async (pago) => {
    const maximo = pago.saldo_reembolsable_centavos / 100;
    const entrada = window.prompt(`Monto a reembolsar en ${pago.moneda}. Máximo: ${maximo.toFixed(2)}`, maximo.toFixed(2));
    if (entrada === null) return;
    const monto = Number(String(entrada).replace(",", "."));
    if (!Number.isFinite(monto) || monto <= 0 || monto > maximo) {
      setError("El monto del reembolso no es válido.");
      return;
    }
    const nota = window.prompt("Motivo interno del reembolso (opcional):", "Cancelación solicitada por el paciente") || null;
    setProcesando(pago.id);
    setError("");
    try {
      const actualizado = await pagosApi.reembolsar(pago.id, {
        monto_centavos: Math.round(monto * 100),
        razon: "requested_by_customer",
        nota,
      });
      setPagos((actuales) => actuales.map((item) => (item.id === actualizado.id ? actualizado : item)));
      setMensaje("Stripe aceptó la solicitud de reembolso.");
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible procesar el reembolso."));
    } finally {
      setProcesando(null);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="etiqueta">Administración</p>
          <h1 className="mt-2 text-3xl font-black text-slate-900 dark:text-white">Pagos, tarifas y reembolsos</h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-300">Los montos se definen en el servidor y los datos de tarjeta se procesan en Stripe Checkout.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={sincronizarCitas} disabled={procesando === "sincronizar-citas"} className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 font-black text-white hover:bg-blue-700 disabled:opacity-60"><RefreshCw size={17} className={procesando === "sincronizar-citas" ? "animate-spin" : ""} /> Sincronizar citas</button>
          <button onClick={cargar} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 font-bold text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"><RefreshCw size={17} /> Actualizar</button>
        </div>
      </div>

      {error && <p className="mt-5 rounded-xl bg-red-50 p-4 text-sm font-semibold text-red-700 dark:bg-red-950/30 dark:text-red-200">{error}</p>}
      {mensaje && <p className="mt-5 rounded-xl bg-emerald-50 p-4 text-sm font-semibold text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-200">{mensaje}</p>}

      <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          ["Registros", resumen.total],
          ["Pendientes", resumen.pendientes],
          ["Pagados", resumen.pagados],
          ["Recaudación neta", dinero(resumen.neto)],
        ].map(([titulo, valor]) => <article key={titulo} className="panel p-5"><CreditCard size={20} className="text-blue-600" /><p className="mt-4 text-2xl font-black dark:text-white">{valor}</p><p className="text-sm font-bold text-slate-500">{titulo}</p></article>)}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1.5fr_.8fr]">
        <article className="panel overflow-hidden">
          <div className="border-b border-slate-100 p-5 dark:border-slate-800"><h2 className="text-xl font-black dark:text-white">Transacciones</h2></div>
          {cargando ? <p className="flex items-center justify-center gap-2 p-10 text-slate-500"><LoaderCircle className="animate-spin" /> Cargando…</p> : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[920px] text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-400 dark:bg-slate-800"><tr><th className="p-4">Cita</th><th className="p-4">Paciente / psicólogo</th><th className="p-4">Monto</th><th className="p-4">Estado</th><th className="p-4">Fecha</th><th className="p-4">Acciones</th></tr></thead>
                <tbody>
                  {pagos.map((pago) => (
                    <tr key={pago.id} className="border-t border-slate-100 dark:border-slate-800">
                      <td className="p-4 font-mono text-xs">{pago.cita_id}</td>
                      <td className="p-4"><p>Paciente #{pago.paciente_id}</p><p className="text-xs text-slate-400">Psicólogo #{pago.psicologo_id}</p></td>
                      <td className="p-4 font-black">{dinero(pago.monto_centavos, pago.moneda)}{pago.reembolsado_centavos > 0 && <p className="text-xs font-semibold text-amber-600">Devuelto {dinero(pago.reembolsado_centavos, pago.moneda)}</p>}</td>
                      <td className="p-4"><EstadoPago estado={pago.estado} /></td>
                      <td className="p-4 text-xs">{fecha(pago.fecha_hora_inicio)}</td>
                      <td className="p-4"><div className="flex gap-2">{pago.comprobante_url && <a href={pago.comprobante_url} target="_blank" rel="noreferrer" title="Comprobante" className="rounded-lg bg-blue-50 p-2 text-blue-700"><ReceiptText size={16} /></a>}{pago.puede_reembolsar && <button onClick={() => reembolsar(pago)} disabled={procesando === pago.id} title="Reembolsar" className="rounded-lg bg-amber-50 p-2 text-amber-700 disabled:opacity-50"><RotateCcw size={16} /></button>}</div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {pagos.length === 0 && <p className="p-10 text-center text-slate-500">Todavía no hay pagos.</p>}
            </div>
          )}
        </article>

        <article className="panel p-5">
          <h2 className="text-xl font-black dark:text-white">Nueva tarifa</h2>
          <p className="mt-1 text-sm text-slate-500">Déjala sin psicólogo para que sea global.</p>
          <form onSubmit={crearTarifa} className="mt-5 space-y-4">
            <label className="block"><span className="text-xs font-black uppercase text-slate-400">ID psicólogo (opcional)</span><input className="campo mt-2" type="number" min="1" value={formulario.psicologo_id} onChange={(e) => setFormulario({ ...formulario, psicologo_id: e.target.value })} /></label>
            <label className="block"><span className="text-xs font-black uppercase text-slate-400">Modalidad</span><select className="campo mt-2" value={formulario.modalidad} onChange={(e) => setFormulario({ ...formulario, modalidad: e.target.value })}><option value="TODAS">Todas</option><option value="VIRTUAL">Virtual</option><option value="PRESENCIAL">Presencial</option></select></label>
            <div className="grid grid-cols-[1fr_90px] gap-3"><label><span className="text-xs font-black uppercase text-slate-400">Monto</span><input className="campo mt-2" type="number" min="1" step="0.01" required value={formulario.monto} onChange={(e) => setFormulario({ ...formulario, monto: e.target.value })} /></label><label><span className="text-xs font-black uppercase text-slate-400">Moneda</span><input className="campo mt-2" maxLength="3" required value={formulario.moneda} onChange={(e) => setFormulario({ ...formulario, moneda: e.target.value.toUpperCase() })} /></label></div>
            <button disabled={procesando === "tarifa-nueva"} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 font-black text-white hover:bg-blue-700 disabled:opacity-60"><Plus size={17} /> Crear tarifa</button>
          </form>

          <h3 className="mt-8 font-black dark:text-white">Historial de tarifas</h3>
          <div className="mt-3 space-y-3">
            {tarifas.map((tarifa) => <div key={tarifa.id} className="rounded-xl border border-slate-100 p-3 dark:border-slate-800"><div className="flex items-start justify-between gap-3"><div><p className="font-black dark:text-white">{dinero(tarifa.monto_centavos, tarifa.moneda)}</p><p className="text-xs text-slate-500">{tarifa.psicologo_id ? `Psicólogo #${tarifa.psicologo_id}` : "Tarifa global"} · {tarifa.modalidad.toLowerCase()}</p><p className={`mt-1 text-xs font-bold ${tarifa.activa ? "text-emerald-600" : "text-slate-400"}`}>{tarifa.activa ? "Activa" : "Inactiva"}</p></div>{tarifa.activa && <button onClick={() => desactivarTarifa(tarifa)} disabled={procesando === tarifa.id} className="rounded-lg bg-red-50 p-2 text-red-600"><Trash2 size={15} /></button>}</div></div>)}
            {tarifas.length === 0 && <p className="text-sm text-slate-400">Se usará la tarifa general del archivo .env.</p>}
          </div>
        </article>
      </section>
    </div>
  );
}
