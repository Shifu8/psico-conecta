import { CreditCard, ExternalLink, LoaderCircle, ReceiptText, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import EstadoPago from "./EstadoPago";
import { mensajeErrorPago, pagosApi } from "../../servicios/servicioPagos";

const moneda = (pago) =>
  new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: pago?.moneda || "USD",
  }).format(Number(pago?.monto || 0));

export default function ResumenPagoCita({ cita, esPaciente }) {
  const [pago, setPago] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState("");

  const cargar = async () => {
    if (!cita?.id || cita?.estado !== "CONFIRMADA") {
      setCargando(false);
      return;
    }
    setCargando(true);
    setError("");
    try {
      setPago(await pagosApi.obtenerPorCita(cita.id));
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible consultar el pago."));
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
  }, [cita?.id, cita?.estado]);

  const pagar = async () => {
    setProcesando(true);
    setError("");
    try {
      const actualizado = await pagosApi.crearCheckout(cita.id);
      setPago(actualizado);
      if (actualizado?.estado === "PAGADO") return;
      if (!actualizado?.checkout_url) throw new Error("Stripe no devolvió un enlace de pago.");
      window.location.assign(actualizado.checkout_url);
    } catch (excepcion) {
      setError(mensajeErrorPago(excepcion, "No fue posible iniciar el pago."));
      setProcesando(false);
    }
  };

  if (cita?.estado !== "CONFIRMADA") return null;

  return (
    <section className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-900 dark:bg-emerald-950/20">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="flex items-center gap-2 font-black text-emerald-950 dark:text-emerald-100">
            <CreditCard size={19} /> Pago de la consulta
          </h3>
          {cargando ? (
            <p className="mt-2 flex items-center gap-2 text-sm text-emerald-700 dark:text-emerald-200">
              <LoaderCircle size={16} className="animate-spin" /> Consultando estado…
            </p>
          ) : pago ? (
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <p className="text-xl font-black text-emerald-950 dark:text-white">{moneda(pago)}</p>
              <EstadoPago estado={pago.estado} />
            </div>
          ) : (
            <p className="mt-2 text-sm text-emerald-700 dark:text-emerald-200">
              El pago se preparará con la tarifa configurada por el administrador.
            </p>
          )}
          {error && <p className="mt-3 text-sm font-semibold text-red-700 dark:text-red-300">{error}</p>}
        </div>
        <div className="flex flex-wrap gap-2">
          {!cargando && esPaciente && (!pago || pago.puede_pagar) && (
            <button
              type="button"
              onClick={pagar}
              disabled={procesando}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 font-black text-white hover:bg-emerald-700 disabled:opacity-60"
            >
              {procesando ? <LoaderCircle size={17} className="animate-spin" /> : <CreditCard size={17} />}
              {pago?.checkout_url ? "Continuar pago" : "Pagar consulta"}
            </button>
          )}
          {pago?.comprobante_url && esPaciente && (
            <a
              href={pago.comprobante_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-emerald-300 bg-white px-4 py-2 font-bold text-emerald-800 hover:bg-emerald-100 dark:bg-slate-900 dark:text-emerald-200"
            >
              <ReceiptText size={17} /> Comprobante <ExternalLink size={14} />
            </a>
          )}
          {!cargando && (
            <button type="button" onClick={cargar} className="rounded-xl p-2 text-emerald-700 hover:bg-emerald-100 dark:text-emerald-200">
              <RefreshCw size={18} />
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
