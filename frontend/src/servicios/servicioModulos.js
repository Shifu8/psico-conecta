import axios from "axios";
import api from "./api";
import { URLS_SERVICIOS } from "./configuracionFrontend";

const crearCliente = (baseURL) => {
  const cliente = axios.create({
    baseURL,
    headers: { "Content-Type": "application/json" },
    timeout: 3500,
  });

  cliente.interceptors.request.use((configuracion) => {
    const token = localStorage.getItem("psicoconecta_token");
    if (token) {
      configuracion.headers.Authorization = `Bearer ${token}`;
    }
    return configuracion;
  });

  return cliente;
};

const clientes = {
  usuarios: api,
  citas: crearCliente(URLS_SERVICIOS.citas),
  teleconsulta: crearCliente(URLS_SERVICIOS.teleconsulta),
  pagos: crearCliente(URLS_SERVICIOS.pagos),
  iot: crearCliente(URLS_SERVICIOS.iot),
  gateway: crearCliente(URLS_SERVICIOS.gateway),
};

const coleccion = async (cliente, endpoint, clave) => {
  const { data } = await cliente.get(endpoint);
  return Array.isArray(data?.[clave]) ? data[clave] : [];
};

export const obtenerCitas = async () => {
  const { data } = await clientes.citas.get("/api/citas/mis-citas");
  return Array.isArray(data) ? data : [];
};

export const obtenerSesionesTeleconsulta = async () => {
  const { data } = await clientes.teleconsulta.get("/api/teleconsultas/mis-sesiones");
  return Array.isArray(data) ? data : [];
};
export const obtenerPagos = async () => {
  const { data } = await clientes.pagos.get("/api/pagos/mis-pagos");
  return Array.isArray(data) ? data : [];
};
export const obtenerEmociones = () => Promise.resolve([]);
export const obtenerLecturasIot = () => Promise.resolve([]);

export const crearRegistroEmocional = (datos) =>
  Promise.resolve({ data: { emocion: datos } });

export const obtenerDatosOperativos = async () => {
  const resultados = await Promise.allSettled([
    obtenerCitas(),
    obtenerSesionesTeleconsulta(),
    obtenerPagos(),
    obtenerEmociones(),
    obtenerLecturasIot(),
  ]);

  const valor = (indice) =>
    resultados[indice].status === "fulfilled" ? resultados[indice].value : [];

  return {
    citas: valor(0),
    sesiones: valor(1),
    pagos: valor(2),
    emociones: valor(3),
    lecturasIot: valor(4),
    errores: resultados
      .map((resultado, indice) => ({ resultado, indice }))
      .filter(({ resultado }) => resultado.status === "rejected")
      .map(({ indice }) => ["citas", "teleconsulta", "pagos", "iot emociones", "iot lecturas"][indice]),
  };
};

const serviciosHealth = [
  ["usuarios", "Usuarios", clientes.usuarios],
  ["citas", "Citas", clientes.citas],
  ["teleconsulta", "Teleconsulta", clientes.teleconsulta],
  ["pagos", "Pagos", clientes.pagos],
  ["iot", "IoT", clientes.iot],
  ["gateway", "API Gateway", clientes.gateway],
];

export const obtenerEstadoServicios = async () => {
  const resultados = await Promise.allSettled(
    serviciosHealth.map(([, , cliente]) => cliente.get("/health")),
  );

  return serviciosHealth.map(([clave, nombre], indice) => {
    const resultado = resultados[indice];
    if (resultado.status === "fulfilled") {
      return {
        clave,
        nombre,
        estado: "ok",
        detalle: resultado.value.data?.servicio || "Disponible",
      };
    }
    return {
      clave,
      nombre,
      estado: "error",
      detalle: "Sin respuesta",
    };
  });
};
