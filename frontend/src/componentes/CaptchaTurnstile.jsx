import { useEffect, useRef, useState } from "react";

const SCRIPT_ID = "psicoconecta-turnstile";
const CALLBACK_NAME = "__psicoconectaTurnstileReady";

let promesaTurnstile;

const cargarTurnstile = () => {
  if (window.turnstile) return Promise.resolve(window.turnstile);
  if (promesaTurnstile) return promesaTurnstile;

  promesaTurnstile = new Promise((resolve, reject) => {
    window[CALLBACK_NAME] = () => resolve(window.turnstile);

    const existente = document.getElementById(SCRIPT_ID);
    if (existente) return;

    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = `https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=${CALLBACK_NAME}`;
    script.async = true;
    script.defer = true;
    script.onerror = () => reject(new Error("No se pudo cargar Turnstile."));
    document.head.appendChild(script);
  });

  return promesaTurnstile;
};

export default function CaptchaTurnstile({ onVerify, onExpire, resetKey }) {
  const siteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY?.trim();
  const contenedorRef = useRef(null);
  const widgetRef = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!siteKey || !contenedorRef.current) return undefined;
    let activo = true;

    cargarTurnstile()
      .then((turnstile) => {
        if (!activo || !contenedorRef.current || widgetRef.current) return;
        widgetRef.current = turnstile.render(contenedorRef.current, {
          sitekey: siteKey,
          theme: "auto",
          callback: (token) => {
            setError("");
            onVerify(token);
          },
          "expired-callback": () => {
            onVerify("");
            onExpire?.();
          },
          "error-callback": () => {
            onVerify("");
            setError("No se pudo completar la verificación de seguridad.");
          },
        });
      })
      .catch(() => {
        if (activo) setError("No se pudo cargar la verificación de seguridad.");
      });

    return () => {
      activo = false;
      if (window.turnstile && widgetRef.current) {
        window.turnstile.remove(widgetRef.current);
        widgetRef.current = null;
      }
    };
  }, [onExpire, onVerify, siteKey]);

  useEffect(() => {
    if (window.turnstile && widgetRef.current) {
      window.turnstile.reset(widgetRef.current);
      onVerify("");
    }
  }, [onVerify, resetKey]);

  if (!siteKey) return null;

  return (
    <div className="space-y-2">
      <div ref={contenedorRef} className="min-h-[65px]" />
      {error && (
        <p className="text-xs font-semibold text-red-600 dark:text-red-300">
          {error}
        </p>
      )}
    </div>
  );
}
