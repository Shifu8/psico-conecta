import { Mail } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import CampoFormulario from "../../componentes/CampoFormulario";
import { solicitarRecuperacion } from "../../servicios/servicioAutenticacion";
import {
  normalizarCorreo,
  obtenerMensajeApi,
  validarCorreo,
} from "../../utilidades/validacion";

export default function RecuperarContrasena() {
  const [email, setEmail] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [procesando, setProcesando] = useState(false);
  const [tocado, setTocado] = useState(false);
  const errorEmail = validarCorreo(email);

  const enviar = async (evento) => {
    evento.preventDefault();
    if (procesando) return;
    const correo = normalizarCorreo(email);
    setEmail(correo);
    setTocado(true);
    setError("");
    setMensaje("");
    if (validarCorreo(correo)) return;
    setProcesando(true);
    try {
      const { data } = await solicitarRecuperacion(correo);
      setMensaje(data.message || "Revisa tu correo para continuar.");
    } catch (excepcion) {
      setError(obtenerMensajeApi(excepcion, "No fue posible solicitar la recuperación."));
    } finally {
      setProcesando(false);
    }
  };

  return (
    <>
      <p className="etiqueta">Recuperación segura</p>
      <h1 className="mt-3 text-3xl font-black text-slate-900 dark:text-white">Recupera tu acceso</h1>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
        Te enviaremos un enlace para restablecer tu contraseña.
      </p>
      <form onSubmit={enviar} className="mt-7 space-y-4" noValidate>
        <CampoFormulario etiqueta="Correo electrónico" type="email" value={email} onChange={(evento) => { setEmail(evento.target.value); setTocado(true); }} onBlur={() => setEmail(normalizarCorreo(email))} error={tocado ? errorEmail : ""} autoComplete="email" maxLength={255} required />
        {mensaje && <p className="rounded-xl bg-cyan-50 p-3 text-sm font-semibold text-cyan-800 dark:bg-cyan-950/50 dark:text-cyan-200">{mensaje}</p>}
        {error && <p className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 dark:bg-red-950/40 dark:text-red-200">{error}</p>}
        <button type="submit" className="boton-primario w-full" disabled={procesando}>
          <Mail size={18} />
          {procesando ? "Enviando..." : "Enviar enlace"}
        </button>
      </form>
      <Link to="/iniciar-sesion" className="mt-6 block text-center text-sm font-bold text-blue-600 dark:text-blue-300">
        Volver al inicio de sesión
      </Link>
    </>
  );
}
