const NOMBRE_VALIDO = /^[\p{L}]+(?:[ '-][\p{L}]+)*$/u;
const TELEFONO_VALIDO = /^\+?[0-9][0-9 ()-]*[0-9]$/;
const CORREO_VALIDO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARACTER_ESPECIAL = /[^\p{L}\p{N}_\s]/u;
const CONTRASENAS_DEBILES = new Set([
  "12345678",
  "admin123*",
  "contraseña123*",
  "password123*",
  "psicoconecta123*",
  "qwerty123*",
]);

export const AYUDA_CONTRASENA =
  "Usa de 8 a 15 caracteres con mayúscula, minúscula, número y carácter especial.";

export const obtenerRequisitosContrasena = (valor = "") => [
  {
    id: "longitud",
    texto: "Entre 8 y 15 caracteres",
    cumplido: valor.length >= 8 && valor.length <= 15,
  },
  {
    id: "mayuscula",
    texto: "Al menos una mayúscula",
    cumplido: /[A-ZÁÉÍÓÚÜÑ]/.test(valor),
  },
  {
    id: "minuscula",
    texto: "Al menos una minúscula",
    cumplido: /[a-záéíóúüñ]/.test(valor),
  },
  {
    id: "numero",
    texto: "Al menos un número",
    cumplido: /\d/.test(valor),
  },
  {
    id: "especial",
    texto: "Al menos un carácter especial",
    cumplido: CARACTER_ESPECIAL.test(valor),
  },
  {
    id: "sin-espacios",
    texto: "Sin espacios",
    cumplido: valor.length > 0 && !/\s/.test(valor),
  },
  {
    id: "no-comun",
    texto: "No debe ser una contraseña común",
    cumplido:
      valor.length > 0 &&
      !CONTRASENAS_DEBILES.has(valor.toLowerCase()) &&
      new Set(valor.toLowerCase()).size >= 5,
  },
];

export const normalizarEspacios = (valor = "") =>
  valor.trim().replace(/\s+/g, " ");

export const normalizarCorreo = (valor = "") => valor.trim().toLowerCase();

export const validarNombre = (valor, etiqueta) => {
  const normalizado = normalizarEspacios(valor);
  if (!normalizado) return `${etiqueta} es obligatorio.`;
  if (normalizado.length < 2) return `${etiqueta} debe tener al menos 2 caracteres.`;
  if (normalizado.length > 80) return `${etiqueta} no puede superar los 80 caracteres.`;
  if (!NOMBRE_VALIDO.test(normalizado)) {
    return "Usa únicamente letras, espacios, apóstrofes o guiones.";
  }
  return "";
};

export const validarCorreo = (valor) => {
  const normalizado = normalizarCorreo(valor);
  if (!normalizado) return "El correo electrónico es obligatorio.";
  if (normalizado.length > 255 || !CORREO_VALIDO.test(normalizado)) {
    return "Ingresa un correo electrónico válido.";
  }
  return "";
};

export const validarTelefono = (valor) => {
  const normalizado = normalizarEspacios(valor);
  if (!normalizado) return "";
  const digitos = normalizado.replace(/\D/g, "");
  if (
    normalizado.length > 20 ||
    digitos.length < 7 ||
    digitos.length > 15 ||
    !TELEFONO_VALIDO.test(normalizado)
  ) {
    return "Ingresa un teléfono válido de 7 a 15 dígitos.";
  }
  return "";
};

export const obtenerFechaMaximaAdulto = () => {
  const fecha = new Date();
  fecha.setFullYear(fecha.getFullYear() - 18);
  return fecha.toISOString().slice(0, 10);
};

export const validarFechaNacimiento = (valor) => {
  if (!valor) return "La fecha de nacimiento es obligatoria.";
  const fecha = new Date(`${valor}T00:00:00`);
  if (Number.isNaN(fecha.getTime())) {
    return "Ingresa una fecha de nacimiento valida.";
  }
  const fechaMinima = new Date();
  fechaMinima.setFullYear(fechaMinima.getFullYear() - 120);
  fechaMinima.setHours(0, 0, 0, 0);
  const fechaMaxima = new Date(`${obtenerFechaMaximaAdulto()}T00:00:00`);
  if (fecha > fechaMaxima) return "Debes ser mayor de edad para registrarte.";
  if (fecha < fechaMinima) return "Ingresa una fecha de nacimiento valida.";
  return "";
};

export const validarContrasena = (valor) => {
  if (!valor) return "La contraseña es obligatoria.";
  if (
    valor.length < 8 ||
    valor.length > 15 ||
    /\s/.test(valor) ||
    !/[A-ZÁÉÍÓÚÜÑ]/.test(valor) ||
    !/[a-záéíóúüñ]/.test(valor) ||
    !/\d/.test(valor) ||
    !CARACTER_ESPECIAL.test(valor) ||
    CONTRASENAS_DEBILES.has(valor.toLowerCase()) ||
    new Set(valor.toLowerCase()).size < 5
  ) {
    return AYUDA_CONTRASENA;
  }
  return "";
};

export const validarPasswordRequerido = (valor) => {
  if (!valor) return "La contraseña es obligatoria.";
  if (valor.length > 15) return "La contraseña no puede superar los 15 caracteres.";
  return "";
};

export const obtenerErroresApi = (excepcion) => {
  const errores = excepcion.response?.data?.errors || {};
  return Object.fromEntries(
    Object.entries(errores).map(([campo, mensajes]) => [
      campo,
      Array.isArray(mensajes) ? mensajes[0] : mensajes,
    ]),
  );
};

export const obtenerMensajeApi = (excepcion, mensajeAlternativo) =>
  excepcion.response?.data?.message || mensajeAlternativo;
