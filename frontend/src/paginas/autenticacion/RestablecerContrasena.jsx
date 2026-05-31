import { KeyRound } from "lucide-react";
import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import CampoFormulario from "../../componentes/CampoFormulario";
import { restablecerContrasena } from "../../servicios/servicioAutenticacion";

export default function RestablecerContrasena() {
  const [parametros] = useSearchParams();
  const [password, setPassword] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [procesando, setProcesando] = useState(false);
  const token = parametros.get("token") || "";

  const enviar = async (evento) => {
    evento.preventDefault();
    setError("");
    setMensaje("");
    setProcesando(true);
    try {
      const { data } = await restablecerContrasena({ token, password });
      setMensaje(data.message || "Contraseña actualizada correctamente.");
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "El enlace no es válido o ya expiró.");
    } finally {
      setProcesando(false);
    }
  };

  return (
    <>
      <p className="etiqueta">Nuevo acceso</p>
      <h1 className="mt-3 text-3xl font-black text-slate-900 dark:text-white">Crea una nueva contraseña</h1>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
        Elige una contraseña segura para volver a ingresar a tu cuenta.
      </p>
      <form onSubmit={enviar} className="mt-7 space-y-4">
        <CampoFormulario etiqueta="Nueva contraseña" type="password" value={password} onChange={(evento) => setPassword(evento.target.value)} autoComplete="new-password" ayuda="Usa al menos 8 caracteres." minLength={8} required />
        {mensaje && <p className="rounded-xl bg-cyan-50 p-3 text-sm font-semibold text-cyan-800 dark:bg-cyan-950/50 dark:text-cyan-200">{mensaje}</p>}
        {error && <p className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 dark:bg-red-950/40 dark:text-red-200">{error}</p>}
        <button type="submit" className="boton-primario w-full" disabled={procesando || !token}>
          <KeyRound size={18} />
          {procesando ? "Actualizando..." : "Actualizar contraseña"}
        </button>
      </form>
      <Link to="/iniciar-sesion" className="mt-6 block text-center text-sm font-bold text-blue-600 dark:text-blue-300">
        Volver al inicio de sesión
      </Link>
    </>
  );
}
