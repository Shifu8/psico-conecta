import { CalendarDays, Camera, Mail, Phone, Save, ShieldCheck, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import AvatarUsuario from "../componentes/AvatarUsuario";
import { usarAutenticacion } from "../contexto/ContextoAutenticacion";
import {
  actualizarPerfil,
  eliminarFotoPerfil,
  subirFotoPerfil,
} from "../servicios/servicioAutenticacion";
import EncabezadoPanel from "./paneles/EncabezadoPanel";

const nombresRoles = {
  ADMIN: "Administrador",
  PSYCHOLOGIST: "Psicologo",
  PATIENT: "Paciente",
};

const MAX_FOTO_BYTES = 2 * 1024 * 1024;
const TIPOS_FOTO = ["image/jpeg", "image/png", "image/webp"];

export default function Perfil() {
  const { usuario, setUsuario } = usarAutenticacion();
  const [formulario, setFormulario] = useState({ first_name: "", last_name: "", phone: "" });
  const [guardando, setGuardando] = useState(false);
  const [subiendoFoto, setSubiendoFoto] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!usuario) return;
    setFormulario({
      first_name: usuario.first_name || "",
      last_name: usuario.last_name || "",
      phone: usuario.phone || "",
    });
  }, [usuario]);

  if (!usuario) return null;

  const manejarCambio = (evento) => {
    const { name, value } = evento.target;
    setFormulario((actual) => ({ ...actual, [name]: value }));
  };

  const guardarPerfil = async (evento) => {
    evento.preventDefault();
    setGuardando(true);
    setMensaje("");
    setError("");
    try {
      const { data } = await actualizarPerfil(usuario.id, {
        first_name: formulario.first_name,
        last_name: formulario.last_name,
        phone: formulario.phone || null,
      });
      setUsuario(data.user);
      setMensaje("Perfil actualizado correctamente.");
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible actualizar el perfil.");
    } finally {
      setGuardando(false);
    }
  };

  const cambiarFoto = async (evento) => {
    const archivo = evento.target.files?.[0];
    evento.target.value = "";
    if (!archivo) return;
    setMensaje("");
    setError("");
    if (!TIPOS_FOTO.includes(archivo.type)) {
      setError("La foto debe ser JPG, PNG o WebP.");
      return;
    }
    if (archivo.size > MAX_FOTO_BYTES) {
      setError("La foto no debe superar 2 MB.");
      return;
    }

    setSubiendoFoto(true);
    try {
      const { data } = await subirFotoPerfil(usuario.id, archivo);
      setUsuario(data.user);
      setMensaje("Foto de perfil actualizada.");
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible subir la foto.");
    } finally {
      setSubiendoFoto(false);
    }
  };

  const quitarFoto = async () => {
    setMensaje("");
    setError("");
    setSubiendoFoto(true);
    try {
      const { data } = await eliminarFotoPerfil(usuario.id);
      setUsuario(data.user);
      setMensaje("Foto de perfil eliminada.");
    } catch (excepcion) {
      setError(excepcion.response?.data?.message || "No fue posible eliminar la foto.");
    } finally {
      setSubiendoFoto(false);
    }
  };

  return (
    <>
      <EncabezadoPanel
        etiqueta="Mi cuenta"
        titulo="Perfil personal"
        texto="Mantén tus datos principales y tu foto de perfil actualizados."
      />

      <section className="panel mt-8 max-w-5xl overflow-hidden">
        <div className="grid gap-0 lg:grid-cols-[320px_1fr]">
          <aside className="border-b border-slate-100 bg-slate-50/70 p-6 dark:border-slate-800 dark:bg-slate-900 lg:border-b-0 lg:border-r">
            <div className="flex flex-col items-center text-center">
              <AvatarUsuario usuario={usuario} tamano="xl" className="rounded-3xl" />
              <h2 className="mt-4 text-2xl font-black text-slate-900 dark:text-white">
                {usuario.first_name} {usuario.last_name}
              </h2>
              <p className="mt-1 text-sm font-bold text-blue-600 dark:text-blue-300">
                {nombresRoles[usuario.role] || usuario.role}
              </p>
            </div>

            <div className="mt-6 grid gap-3">
              <label className="boton-primario w-full cursor-pointer">
                <Camera size={18} />
                {subiendoFoto ? "Subiendo..." : "Cambiar foto"}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  className="hidden"
                  onChange={cambiarFoto}
                  disabled={subiendoFoto}
                />
              </label>
              <button
                type="button"
                onClick={quitarFoto}
                disabled={subiendoFoto}
                className="boton-secundario w-full text-red-600 hover:border-red-300 hover:text-red-700 dark:text-red-300 dark:hover:border-red-500"
              >
                <Trash2 size={17} />
                Quitar foto
              </button>
            </div>

            <div className="mt-6 space-y-3 text-sm">
              <div className="rounded-2xl border border-blue-100 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
                <Mail size={18} className="text-blue-600 dark:text-blue-300" />
                <p className="mt-3 text-xs font-bold uppercase tracking-wider text-slate-400">Correo</p>
                <p className="mt-1 break-all font-semibold text-slate-700 dark:text-slate-200">{usuario.email}</p>
              </div>
              <div className="rounded-2xl border border-blue-100 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
                <ShieldCheck size={18} className="text-blue-600 dark:text-blue-300" />
                <p className="mt-3 text-xs font-bold uppercase tracking-wider text-slate-400">Estado</p>
                <p className="mt-1 font-semibold text-slate-700 dark:text-slate-200">
                  {usuario.status === "active" || !usuario.status ? "Activo" : "Pausado"}
                </p>
              </div>
            </div>
          </aside>

          <form onSubmit={guardarPerfil} className="p-6 sm:p-8">
            <div>
              <p className="etiqueta">Información básica</p>
              <h3 className="mt-2 text-xl font-black text-slate-900 dark:text-white">
                Datos visibles de tu cuenta
              </h3>
            </div>

            {(mensaje || error) && (
              <p
                className={`mt-5 rounded-2xl p-3 text-sm font-semibold ${
                  error
                    ? "bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-200"
                    : "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-200"
                }`}
              >
                {error || mensaje}
              </p>
            )}

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-xs font-black uppercase tracking-wider text-slate-400">Nombre</span>
                <input
                  name="first_name"
                  value={formulario.first_name}
                  onChange={manejarCambio}
                  className="campo mt-2"
                  minLength={2}
                  maxLength={80}
                  required
                />
              </label>
              <label className="block">
                <span className="text-xs font-black uppercase tracking-wider text-slate-400">Apellido</span>
                <input
                  name="last_name"
                  value={formulario.last_name}
                  onChange={manejarCambio}
                  className="campo mt-2"
                  minLength={2}
                  maxLength={80}
                  required
                />
              </label>
              <label className="block">
                <span className="text-xs font-black uppercase tracking-wider text-slate-400">Teléfono</span>
                <div className="relative mt-2">
                  <Phone size={17} className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    name="phone"
                    value={formulario.phone}
                    onChange={manejarCambio}
                    className="campo pl-11"
                    maxLength={30}
                    placeholder="Opcional"
                  />
                </div>
              </label>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
                <CalendarDays size={18} className="text-blue-600 dark:text-blue-300" />
                <p className="mt-3 text-xs font-black uppercase tracking-wider text-slate-400">Fecha de nacimiento</p>
                <p className="mt-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
                  {usuario.birth_date || "No registrada"}
                </p>
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button type="submit" className="boton-primario" disabled={guardando}>
                <Save size={17} />
                {guardando ? "Guardando..." : "Guardar cambios"}
              </button>
            </div>
          </form>
        </div>
      </section>
    </>
  );
}