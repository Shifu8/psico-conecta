import { KeyRound } from "lucide-react";
import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import CampoFormulario from "../../componentes/CampoFormulario";
import RequisitosContrasena from "../../componentes/RequisitosContrasena";
import { restablecerContrasena } from "../../servicios/servicioAutenticacion";
import {
  AYUDA_CONTRASENA,
  obtenerMensajeApi,
  validarContrasena,
} from "../../utilidades/validacion";

export default function RestablecerContrasena() {
  const [parametros] = useSearchParams();
  const [password, setPassword] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [procesando, setProcesando] = useState(false);
  const [tocado, setTocado] = useState(false);
  const token = parametros.get("token") || "";
  const errorPassword = validarContrasena(password);

  const enviar = async (evento) => {
    evento.preventDefault();
    if (procesando) return;
    setTocado(true);
    setError("");
    setMensaje("");
    if (!token) {
      setError("El enlace de recuperación no contiene un token válido.");
      return;
    }
    if (errorPassword) return;
    setProcesando(true);
    try {
      const { data } = await restablecerContrasena({ token, password });
      setMensaje(data.message || "Contraseña actualizada correctamente.");
    } catch (excepcion) {
      setError(obtenerMensajeApi(excepcion, "El enlace no es válido o ya expiró."));
    } finally {
      setProcesando(false);
    }
  };

  return (
    <>
      <p className="etiqueta">Nuevo acceso</p>
      <h1 className="mt-3 text-3xl font-black text-slate-900 dark:text-white">
        Crea una nueva contraseña
      </h1>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
        Elige una contraseña segura para volver a ingresar a tu cuenta.
      </p>
      <form onSubmit={enviar} className="mt-7 space-y-4" noValidate>
        <CampoFormulario
          etiqueta="Nueva contraseña"
          type="password"
          value={password}
          onChange={(evento) => {
            setPassword(evento.target.value);
            setTocado(true);
          }}
          error={tocado ? errorPassword : ""}
          autoComplete="new-password"
          ayuda={AYUDA_CONTRASENA}
          minLength={8}
          maxLength={128}
          required
        />
        <RequisitosContrasena valor={password} />
        {mensaje && (
          <p className="rounded-xl bg-cyan-50 p-3 text-sm font-semibold text-cyan-800 dark:bg-cyan-950/50 dark:text-cyan-200">
            {mensaje}
          </p>
        )}
        {error && (
          <p className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 dark:bg-red-950/40 dark:text-red-200">
            {error}
          </p>
        )}
        <button type="submit" className="boton-primario w-full" disabled={procesando || !token}>
          <KeyRound size={18} />
          {procesando ? "Actualizando..." : "Actualizar contraseña"}
        </button>
      </form>
      <Link
        to="/iniciar-sesion"
        className="mt-6 block text-center text-sm font-bold text-blue-600 dark:text-blue-300"
      >
        Volver al inicio de sesión
      </Link>
    </>
  );
}
