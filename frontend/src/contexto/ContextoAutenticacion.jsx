import { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  cerrarSesion,
  googleLoginRequest,
  iniciarSesion,
  obtenerMiPerfil,
  registrarUsuario,
} from "../servicios/servicioAutenticacion";
import {
  capturarEvento,
  identificarUsuario,
  resetearAnalitica,
} from "../servicios/analitica";

const ContextoAutenticacion = createContext(null);

export function ProveedorAutenticacion({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("psicoconecta_token");
    if (!token) {
      setCargando(false);
      return;
    }

    obtenerMiPerfil()
      .then(({ data }) => {
        setUsuario(data.user);
        identificarUsuario(data.user);
      })
      .catch(() => localStorage.removeItem("psicoconecta_token"))
      .finally(() => setCargando(false));
  }, []);

  useEffect(() => {
    const limpiarSesion = () => setUsuario(null);
    window.addEventListener("psicoconecta:sesion-expirada", limpiarSesion);
    return () => window.removeEventListener("psicoconecta:sesion-expirada", limpiarSesion);
  }, []);

  const entrar = async (credenciales) => {
    const { data } = await iniciarSesion(credenciales);
    localStorage.setItem("psicoconecta_token", data.access_token);
    setUsuario(data.user);
    identificarUsuario(data.user);
    capturarEvento("inicio_sesion_exitoso", { rol: data.user.role });
    return data.user;
  };

  const registrar = async (datos) => {
    const { data } = await registrarUsuario(datos);
    capturarEvento("registro_usuario", { rol: data.user.role });
    return data.user;
  };

  const googleLogin = async (credential) => {
    const { data } = await googleLoginRequest(credential);
    localStorage.setItem("psicoconecta_token", data.access_token);
    setUsuario(data.user);
    identificarUsuario(data.user);
    capturarEvento("inicio_google_exitoso", { rol: data.user.role });
    return data.user;
  };

  const salir = async () => {
    try {
      capturarEvento("cierre_sesion", { rol: usuario?.role });
      await cerrarSesion();
    } finally {
      localStorage.removeItem("psicoconecta_token");
      setUsuario(null);
      resetearAnalitica();
    }
  };

  const valor = useMemo(
    () => ({ usuario, cargando, entrar, registrar, googleLogin, salir, setUsuario }),
    [usuario, cargando],
  );

  return (
    <ContextoAutenticacion.Provider value={valor}>
      {children}
    </ContextoAutenticacion.Provider>
  );
}

export function usarAutenticacion() {
  return useContext(ContextoAutenticacion);
}
