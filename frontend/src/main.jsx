import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import Aplicacion from "./Aplicacion";
import "./index.css";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim();

const temaGuardado = localStorage.getItem("psicoconecta_tema");
const usarTemaOscuro = temaGuardado
  ? temaGuardado === "oscuro"
  : window.matchMedia("(prefers-color-scheme: dark)").matches;

document.documentElement.classList.toggle("dark", usarTemaOscuro);
document.documentElement.style.colorScheme = usarTemaOscuro ? "dark" : "light";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
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
