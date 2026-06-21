import React, { useEffect } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, useLocation } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import Aplicacion from "./Aplicacion";
import "./index.css";
import { capturarVistaPagina, iniciarAnalitica } from "./servicios/analitica";
import { GOOGLE_CLIENT_ID } from "./servicios/configuracionFrontend";

const googleClientId = GOOGLE_CLIENT_ID;
iniciarAnalitica();

const temaGuardado = localStorage.getItem("psicoconecta_tema");
const usarTemaOscuro = temaGuardado
  ? temaGuardado === "oscuro"
  : window.matchMedia("(prefers-color-scheme: dark)").matches;

document.documentElement.classList.toggle("dark", usarTemaOscuro);
document.documentElement.style.colorScheme = usarTemaOscuro ? "dark" : "light";

function SeguimientoAnalitica() {
  const ubicacion = useLocation();

  useEffect(() => {
    capturarVistaPagina();
  }, [ubicacion.pathname, ubicacion.search, ubicacion.hash]);

  return null;
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <SeguimientoAnalitica />
      {googleClientId ? (
        <GoogleOAuthProvider clientId={googleClientId}>
          <Aplicacion />
        </GoogleOAuthProvider>
      ) : (
        <Aplicacion />
      )}
    </BrowserRouter>
  </React.StrictMode>,
);
