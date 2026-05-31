import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import Aplicacion from './Aplicacion'
import { ContextoAutenticacionProvider } from './contexto/ContextoAutenticacion'
import { ContextoTemaProvider } from './contexto/ContextoTema'
import './index.css'

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <GoogleOAuthProvider clientId={googleClientId}>
        <ContextoTemaProvider>
          <ContextoAutenticacionProvider>
            <Aplicacion />
          </ContextoAutenticacionProvider>
        </ContextoTemaProvider>
      </GoogleOAuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
