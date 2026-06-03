import { GoogleLogin } from "@react-oauth/google";
import { LogIn } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import CaptchaTurnstile from "../../componentes/CaptchaTurnstile";
import CampoFormulario from "../../componentes/CampoFormulario";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import { rutaInicialPorRol } from "../../servicios/servicioAutenticacion";
import {
  normalizarCorreo,
  obtenerMensajeApi,
  validarCorreo,
  validarPasswordRequerido,
} from "../../utilidades/validacion";

const validarFormulario = (formulario) => ({
  email: validarCorreo(formulario.email),
  password: validarPasswordRequerido(formulario.password),
});

export default function InicioSesion() {
  const googleHabilitado = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim());
  const captchaHabilitado = Boolean(import.meta.env.VITE_TURNSTILE_SITE_KEY?.trim());
  const [formulario, setFormulario] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [tocados, setTocados] = useState({});
  const [procesando, setProcesando] = useState(false);
  const [captchaToken, setCaptchaToken] = useState("");
  const [captchaResetKey, setCaptchaResetKey] = useState(0);
  const [googleError, setGoogleError] = useState("");
  const { entrar, googleLogin } = usarAutenticacion();
  const navegar = useNavigate();
  const ubicacion = useLocation();

  const actualizar = ({ target }) => {
    setFormulario((actual) => ({ ...actual, [target.name]: target.value }));
    setTocados((actual) => ({ ...actual, [target.name]: true }));
  };

  const reiniciarCaptcha = () => {
    if (!captchaHabilitado) return;
    setCaptchaToken("");
    setCaptchaResetKey((actual) => actual + 1);
  };

  const navegarDespuesDeEntrar = (usuario) => {
    navegar(ubicacion.state?.from?.pathname || rutaInicialPorRol(usuario.role), {
      replace: true,
    });
  };

  const erroresFormulario = validarFormulario(formulario);

  const enviar = async (evento) => {
    evento.preventDefault();
    if (procesando) return;
    const credenciales = {
      ...formulario,
      email: normalizarCorreo(formulario.email),
      ...(captchaHabilitado ? { captcha_token: captchaToken } : {}),
    };
    const errores = validarFormulario(credenciales);
    setFormulario((actual) => ({
      ...actual,
      email: credenciales.email,
    }));
    setTocados({ email: true, password: true });
    setError("");
    if (Object.values(errores).some(Boolean)) {
      setError("Revisa tus credenciales antes de continuar.");
      return;
    }
    if (captchaHabilitado && !captchaToken) {
      setError("Completa la verificación de seguridad antes de continuar.");
      return;
    }
    setProcesando(true);
    try {
      const usuario = await entrar(credenciales);
      navegarDespuesDeEntrar(usuario);
    } catch (excepcion) {
      setError(obtenerMensajeApi(excepcion, "No fue posible iniciar sesión."));
      reiniciarCaptcha();
    } finally {
      setProcesando(false);
    }
  };

  const iniciarConGoogle = async (response) => {
    try {
      setGoogleError("");
      const usuario = await googleLogin(response.credential);
      navegarDespuesDeEntrar(usuario);
    } catch (excepcion) {
      setGoogleError(
        excepcion.response?.data?.message || "Error al iniciar sesión con Google.",
      );
    }
  };

  return (
    <>
      <p className="etiqueta">Bienvenido de vuelta</p>
      <h1 className="mt-3 text-3xl font-black text-slate-900 dark:text-white">
        Inicia sesión
      </h1>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
        Accede con tus credenciales o continúa con Google.
      </p>

      <form onSubmit={enviar} className="mt-7 space-y-4" noValidate>
        <CampoFormulario
          etiqueta="Correo electrónico"
          name="email"
          type="email"
          value={formulario.email}
          onChange={actualizar}
          onBlur={() =>
            setFormulario((actual) => ({
              ...actual,
              email: normalizarCorreo(actual.email),
            }))
          }
          error={tocados.email ? erroresFormulario.email : ""}
          autoComplete="email"
          maxLength={255}
          required
        />
        <CampoFormulario
          etiqueta="Contraseña"
          name="password"
          type="password"
          value={formulario.password}
          onChange={actualizar}
          error={tocados.password ? erroresFormulario.password : ""}
          autoComplete="current-password"
          maxLength={15}
          required
        />
        {captchaHabilitado && (
          <CaptchaTurnstile
            onVerify={setCaptchaToken}
            resetKey={captchaResetKey}
          />
        )}
        {error && (
          <p className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 dark:bg-red-950/40 dark:text-red-200">
            {error}
          </p>
        )}
        <div className="flex justify-end">
          <Link
            to="/recuperar-contrasena"
            className="text-sm font-bold text-blue-600 transition hover:text-blue-700 dark:text-blue-300 dark:hover:text-blue-200"
          >
            Olvidé mi contraseña
          </Link>
        </div>
        <button type="submit" className="boton-primario w-full" disabled={procesando}>
          <LogIn size={18} />
          {procesando ? "Ingresando..." : "Ingresar"}
        </button>
      </form>

      <div className="my-6 flex items-center gap-3">
        <span className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">o</span>
        <span className="h-px flex-1 bg-slate-200 dark:bg-slate-700" />
      </div>

      {googleError && <p className="mb-2 text-center text-xs text-red-500">{googleError}</p>}
      {googleHabilitado ? (
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={iniciarConGoogle}
            onError={() => setGoogleError("No se pudo iniciar sesión con Google.")}
            size="large"
            text="signin_with"
            shape="rectangular"
          />
        </div>
      ) : (
        <p className="text-center text-xs text-slate-500 dark:text-slate-400">
          El inicio con Google no está configurado en este entorno.
        </p>
      )}

      <p className="mt-6 text-center text-sm text-slate-600 dark:text-slate-300">
        ¿No tienes cuenta?{" "}
        <Link to="/registro" className="font-bold text-blue-600 dark:text-blue-300">
          Regístrate
        </Link>
      </p>
    </>
  );
}
