import { createContext, useContext, useEffect, useMemo, useState } from "react";

const ContextoTema = createContext(null);

export function ProveedorTema({ children }) {
  const [oscuro, setOscuro] = useState(() => {
    const temaGuardado = localStorage.getItem("psicoconecta_tema");
    if (temaGuardado) return temaGuardado === "oscuro";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", oscuro);
    document.documentElement.style.colorScheme = oscuro ? "dark" : "light";
    localStorage.setItem("psicoconecta_tema", oscuro ? "oscuro" : "claro");
  }, [oscuro]);

  const valor = useMemo(
    () => ({ oscuro, alternarTema: () => setOscuro((actual) => !actual) }),
    [oscuro],
  );

  return <ContextoTema.Provider value={valor}>{children}</ContextoTema.Provider>;
}

export function usarTema() {
  return useContext(ContextoTema);
}
