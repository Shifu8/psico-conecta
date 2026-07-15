import { CreditCard, ExternalLink, LoaderCircle, ReceiptText, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import EstadoPago from "../../componentes/pagos/EstadoPago";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import { mensajeErrorPago, pagosApi } from "../../servicios/servicioPagos";

const formatoMoneda = (pago) =>
  new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: pago.moneda || "USD",
  }).format(Number(pago.monto || 0));

const formatoFecha = (valor) => {
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return "Sin fecha";
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "full",
    timeStyle: "short",
  }).format(fecha);
};

export default function PaginaPagos() {
  const { usuario } = usarAutenticacion();
  const rol = usuario?.role?.name || usuario?.role;
  const esPaciente = rol === "PATIENT";
  const [pagos, setPagos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(null);
  const [filtro, setFiltro] = useState("TODOS");
  const [error, setError] = useState("");

  const cargar = async () => {
    setCargando(true);
    setError("");
    try {
      setPagos(await pagosApi.listarMisPagos());
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible cargar los pagos."));
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const iniciarPago = async (pago) => {
    setProcesando(pago.id);
    setError("");
    try {
      const actualizado = await pagosApi.crearCheckout(pago.cita_id);
      setPagos((actuales) => actuales.map((item) => (item.id === actualizado.id ? actualizado : item)));
      if (actualizado.estado === "PAGADO") return;
      if (!actualizado.checkout_url) throw new Error("No se recibió el enlace de pago.");
      window.location.assign(actualizado.checkout_url);
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible iniciar el pago."));
      setProcesando(null);
    }
  };

  const filtrados = useMemo(() => {
    if (filtro === "TODOS") return pagos;
    if (filtro === "PAGADOS") return pagos.filter((pago) => ["PAGADO", "REEMBOLSO_PARCIAL"].includes(pago.estado));
    if (filtro === "PENDIENTES") return pagos.filter((pago) => ["PENDIENTE", "CHECKOUT_ABIERTO", "PROCESANDO"].includes(pago.estado));
    return pagos.filter((pago) => ["CANCELADO", "EXPIRADO", "FALLIDO", "REEMBOLSADO"].includes(pago.estado));
  }, [pagos, filtro]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="etiqueta">Módulo de pagos</p>
          <h1 className="mt-2 text-3xl font-black text-slate-900 dark:text-white">
            {esPaciente ? "Mis pagos" : "Pagos de mis citas"}
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-500 dark:text-slate-300">
            Consulta el estado, la tarifa, el comprobante y las devoluciones asociadas a cada cita.
          </p>
        </div>
        <button onClick={cargar} className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 font-bold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
          <RefreshCw size={17} /> Actualizar
        </button>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {["TODOS", "PENDIENTES", "PAGADOS", "OTROS"].map((item) => (
          <button
            key={item}
            onClick={() => setFiltro(item)}
            className={`rounded-full px-4 py-2 text-xs font-black ${filtro === item ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-200"}`}
          >
            {item.toLowerCase()}
          </button>
        ))}
      </div>

      {error && <p className="mt-5 rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-700 dark:bg-red-950/30 dark:text-red-200">{error}</p>}

      {cargando ? (
        <div className="mt-10 flex items-center justify-center gap-3 text-slate-500"><LoaderCircle className="animate-spin" /> Cargando pagos…</div>
      ) : (
        <div className="mt-6 grid gap-4">
          {filtrados.map((pago) => (
            <article key={pago.id} className="panel p-5">
              <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="icono-panel"><CreditCard size={20} /></span>
                    <p className="text-2xl font-black text-slate-900 dark:text-white">{formatoMoneda(pago)}</p>
                    <EstadoPago estado={pago.estado} />
                  </div>
                  <p className="mt-3 text-sm font-bold text-slate-700 dark:text-slate-200">
                    Consulta {pago.modalidad?.toLowerCase()} · {formatoFecha(pago.fecha_hora_inicio)}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">Cita {pago.cita_id}</p>
                  {pago.reembolsado_centavos > 0 && (
                    <p className="mt-2 text-sm font-semibold text-amber-700 dark:text-amber-300">
                      Reembolsado: {(pago.reembolsado_centavos / 100).toLocaleString("es-EC", { style: "currency", currency: pago.moneda })}
                    </p>
                  )}
                  {pago.ultimo_error && <p className="mt-2 text-sm font-semibold text-red-600 dark:text-red-300">{pago.ultimo_error}</p>}
                </div>
                <div className="flex flex-wrap gap-2">
                  <Link to={`/citas/${pago.cita_id}`} className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200">Ver cita</Link>
                  {esPaciente && pago.puede_pagar && (
                    <button
                      onClick={() => iniciarPago(pago)}
                      disabled={procesando === pago.id}
                      className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-black text-white hover:bg-emerald-700 disabled:opacity-60"
                    >
                      {procesando === pago.id ? <LoaderCircle size={16} className="animate-spin" /> : <CreditCard size={16} />}
                      {pago.checkout_url ? "Continuar" : "Pagar"}
                    </button>
                  )}
                  {esPaciente && pago.comprobante_url && (
                    <a href={pago.comprobante_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700">
                      <ReceiptText size={16} /> Comprobante <ExternalLink size={13} />
                    </a>
                  )}
                </div>
              </div>
            </article>
          ))}
          {filtrados.length === 0 && (
            <div className="panel p-10 text-center text-sm text-slate-500 dark:text-slate-300">No hay pagos en esta categoría.</div>
          )}
        </div>
      )}
    </div>
  );
}
