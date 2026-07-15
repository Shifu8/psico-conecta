import { CheckCircle2, LoaderCircle, ReceiptText, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import EstadoPago from "../../componentes/pagos/EstadoPago";
import { mensajeErrorPago, pagosApi } from "../../servicios/servicioPagos";

export default function PaginaResultadoPago() {
  const [parametros] = useSearchParams();
  const sessionId = parametros.get("session_id");
  const [pago, setPago] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let activo = true;
    if (!sessionId) {
      setError("No se recibió el identificador de la sesión de pago.");
      setCargando(false);
      return undefined;
    }
    pagosApi.sincronizarCheckout(sessionId)
      .then((resultado) => activo && setPago(resultado))
      .catch((excepcion) => activo && setError(mensajeErrorPago(excepcion, "No fue posible verificar el pago.")))
      .finally(() => activo && setCargando(false));
    return () => { activo = false; };
  }, [sessionId]);

  const exitoso = pago?.estado === "PAGADO" || pago?.estado === "REEMBOLSO_PARCIAL";

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <article className="panel p-8 text-center">
        {cargando ? (
          <><LoaderCircle size={52} className="mx-auto animate-spin text-blue-600" /><h1 className="mt-5 text-2xl font-black dark:text-white">Verificando el pago…</h1></>
        ) : error ? (
          <><XCircle size={52} className="mx-auto text-red-500" /><h1 className="mt-5 text-2xl font-black dark:text-white">No pudimos verificarlo</h1><p className="mt-3 text-sm text-red-600 dark:text-red-300">{error}</p></>
        ) : (
          <>
            {exitoso ? <CheckCircle2 size={58} className="mx-auto text-emerald-500" /> : <LoaderCircle size={58} className="mx-auto text-amber-500" />}
            <h1 className="mt-5 text-3xl font-black text-slate-900 dark:text-white">{exitoso ? "Pago confirmado" : "Pago en procesamiento"}</h1>
            <div className="mt-4 flex justify-center"><EstadoPago estado={pago?.estado} /></div>
            <p className="mt-4 text-lg font-black text-slate-800 dark:text-slate-100">
              {Number(pago?.monto || 0).toLocaleString("es-EC", { style: "currency", currency: pago?.moneda || "USD" })}
            </p>
            {pago?.comprobante_url && (
              <a href={pago.comprobante_url} target="_blank" rel="noreferrer" className="mx-auto mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 font-black text-white hover:bg-blue-700">
                <ReceiptText size={17} /> Abrir comprobante
              </a>
            )}
          </>
        )}
        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Link to="/pagos" className="rounded-xl bg-slate-900 px-5 py-2.5 font-black text-white dark:bg-white dark:text-slate-900">Ir a mis pagos</Link>
          {pago?.cita_id && <Link to={`/citas/${pago.cita_id}`} className="rounded-xl border border-slate-200 px-5 py-2.5 font-bold text-slate-700 dark:border-slate-700 dark:text-slate-200">Ver cita</Link>}
        </div>
      </article>
    </div>
  );
}
