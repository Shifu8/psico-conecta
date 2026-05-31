import { UserPlus } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import CampoFormulario from "../../componentes/CampoFormulario";
import { usarAutenticacion } from "../../contexto/ContextoAutenticacion";

const inicial = {
  first_name: "",
  last_name: "",
  email: "",
  password: "",
};

export default function Registro() {
  const [formulario, setFormulario] = useState(inicial);
  const [error, setError] = useState("");
  const [procesando, setProcesando] = useState(false);
  const { registrar } = usarAutenticacion();
  const navegar = useNavigate();

  const actualizar = ({ target }) => {
    setFormulario((actual) => ({ ...actual, [target.name]: target.value }));
  };

  const enviar = async (evento) => {
    evento.preventDefault();
    setError("");
    setProcesando(true);
    try {
      await registrar(formulario);
      navegar("/iniciar-sesion", { replace: true });
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible completar el registro.");
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
      <form onSubmit={enviar} className="mt-7 grid gap-4 sm:grid-cols-2">
        <CampoFormulario etiqueta="Nombres" name="first_name" value={formulario.first_name} onChange={actualizar} autoComplete="given-name" required />
        <CampoFormulario etiqueta="Apellidos" name="last_name" value={formulario.last_name} onChange={actualizar} autoComplete="family-name" required />
        <CampoFormulario className="sm:col-span-2" etiqueta="Correo electrónico" name="email" type="email" value={formulario.email} onChange={actualizar} autoComplete="email" required />
        <CampoFormulario className="sm:col-span-2" etiqueta="Contraseña" name="password" type="password" value={formulario.password} onChange={actualizar} autoComplete="new-password" ayuda="Usa al menos 8 caracteres." minLength={8} required />
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
