import { UserPlus } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import CampoFormulario from "../../componentes/CampoFormulario";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";
import {
  AYUDA_CONTRASENA,
  normalizarCorreo,
  normalizarEspacios,
  obtenerErroresApi,
  obtenerMensajeApi,
  validarContrasena,
  validarCorreo,
  validarNombre,
  validarTelefono,
} from "../../utilidades/validacion";

const inicial = {
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  phone: "",
};

const campos = ["first_name", "last_name", "email", "password", "phone"];

const validarFormulario = (formulario) => ({
  first_name: validarNombre(formulario.first_name, "El nombre"),
  last_name: validarNombre(formulario.last_name, "El apellido"),
  email: validarCorreo(formulario.email),
  password: validarContrasena(formulario.password),
  phone: validarTelefono(formulario.phone),
});

export default function Registro() {
  const [formulario, setFormulario] = useState(inicial);
  const [error, setError] = useState("");
  const [erroresServidor, setErroresServidor] = useState({});
  const [tocados, setTocados] = useState({});
  const [procesando, setProcesando] = useState(false);
  const { registrar } = usarAutenticacion();
  const navegar = useNavigate();

  const actualizar = ({ target }) => {
    setFormulario((actual) => ({ ...actual, [target.name]: target.value }));
    setTocados((actual) => ({ ...actual, [target.name]: true }));
    setErroresServidor((actual) => ({ ...actual, [target.name]: "" }));
  };

  const normalizar = ({ target }) => {
    if (target.name === "password") return;
    const valor = target.name === "email"
      ? normalizarCorreo(target.value)
      : normalizarEspacios(target.value);
    setFormulario((actual) => ({ ...actual, [target.name]: valor }));
  };

  const erroresFormulario = validarFormulario(formulario);
  const errorCampo = (campo) =>
    erroresServidor[campo] || (tocados[campo] ? erroresFormulario[campo] : "");

  const enviar = async (evento) => {
    evento.preventDefault();
    if (procesando) return;
    const datos = {
      ...formulario,
      first_name: normalizarEspacios(formulario.first_name),
      last_name: normalizarEspacios(formulario.last_name),
      email: normalizarCorreo(formulario.email),
      phone: normalizarEspacios(formulario.phone),
    };
    const errores = validarFormulario(datos);
    setFormulario(datos);
    setTocados(Object.fromEntries(campos.map((campo) => [campo, true])));
    setError("");
    setErroresServidor({});
    if (Object.values(errores).some(Boolean)) {
      setError("Revisa los campos marcados antes de crear tu cuenta.");
      return;
    }
    setProcesando(true);
    try {
      await registrar(datos);
      navegar("/iniciar-sesion", { replace: true });
    } catch (excepcion) {
      setErroresServidor(obtenerErroresApi(excepcion));
      setError(obtenerMensajeApi(excepcion, "No fue posible completar el registro."));
    } finally {
      setProcesando(false);
    }
  };

  return (
    <>
      <p className="etiqueta">Comienza tu proceso</p>
      <h1 className="mt-3 text-3xl font-black text-slate-900 dark:text-white">Crea tu cuenta</h1>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
        Completa tus datos para comenzar a organizar tu atención.
      </p>
      <form onSubmit={enviar} className="mt-7 grid gap-4 sm:grid-cols-2" noValidate>
        <CampoFormulario etiqueta="Nombres" name="first_name" value={formulario.first_name} onChange={actualizar} onBlur={normalizar} error={errorCampo("first_name")} autoComplete="given-name" maxLength={80} required />
        <CampoFormulario etiqueta="Apellidos" name="last_name" value={formulario.last_name} onChange={actualizar} onBlur={normalizar} error={errorCampo("last_name")} autoComplete="family-name" maxLength={80} required />
        <CampoFormulario className="sm:col-span-2" etiqueta="Correo electrónico" name="email" type="email" value={formulario.email} onChange={actualizar} onBlur={normalizar} error={errorCampo("email")} autoComplete="email" maxLength={255} required />
        <CampoFormulario className="sm:col-span-2" etiqueta="Teléfono (opcional)" name="phone" type="tel" value={formulario.phone} onChange={actualizar} onBlur={normalizar} error={errorCampo("phone")} autoComplete="tel" maxLength={20} />
        <CampoFormulario className="sm:col-span-2" etiqueta="Contraseña" name="password" type="password" value={formulario.password} onChange={actualizar} error={errorCampo("password")} autoComplete="new-password" ayuda={AYUDA_CONTRASENA} minLength={8} maxLength={128} required />
        {error && <p className="sm:col-span-2 rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700 dark:bg-red-950/40 dark:text-red-200">{error}</p>}
        <button type="submit" className="boton-primario sm:col-span-2" disabled={procesando}>
          <UserPlus size={18} />
          {procesando ? "Registrando..." : "Crear cuenta"}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-600 dark:text-slate-300">
        ¿Ya tienes cuenta?{" "}
        <Link to="/iniciar-sesion" className="font-bold text-blue-600 dark:text-blue-300">
          Inicia sesión
        </Link>
      </p>
    </>
  );
}
