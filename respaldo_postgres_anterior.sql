--
-- PostgreSQL database dump
--

\restrict ual5twuE46eWt9EKOvu3Ww0Jc3agZLQPeu4bahPCzSk6F4Jf8koLtzsqcEW43kf

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: citas_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA citas_schema;


ALTER SCHEMA citas_schema OWNER TO postgres;

--
-- Name: pagos_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pagos_schema;


ALTER SCHEMA pagos_schema OWNER TO postgres;

--
-- Name: teleconsulta_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA teleconsulta_schema;


ALTER SCHEMA teleconsulta_schema OWNER TO postgres;

--
-- Name: usuarios_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA usuarios_schema;


ALTER SCHEMA usuarios_schema OWNER TO postgres;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: citas; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.citas (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    paciente_id integer NOT NULL,
    psicologo_id integer NOT NULL,
    fecha_hora_inicio timestamp with time zone NOT NULL,
    fecha_hora_fin timestamp with time zone NOT NULL,
    estado character varying(20) DEFAULT 'PENDIENTE'::character varying NOT NULL,
    modalidad character varying(15) DEFAULT 'VIRTUAL'::character varying NOT NULL,
    motivo_consulta text,
    notas_psicologo text,
    motivo_cancelacion text,
    cancelado_por integer,
    reprogramada_desde uuid,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL,
    fecha_actualizacion timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_citas_estado CHECK (((estado)::text = ANY ((ARRAY['PENDIENTE'::character varying, 'CONFIRMADA'::character varying, 'REPROGRAMADA'::character varying, 'CANCELADA'::character varying, 'COMPLETADA'::character varying, 'NO_ASISTIDA'::character varying])::text[]))),
    CONSTRAINT ck_citas_modalidad CHECK (((modalidad)::text = ANY ((ARRAY['VIRTUAL'::character varying, 'PRESENCIAL'::character varying])::text[]))),
    CONSTRAINT ck_citas_rango_fecha CHECK ((fecha_hora_fin > fecha_hora_inicio))
);


ALTER TABLE citas_schema.citas OWNER TO postgres;

--
-- Name: disponibilidad; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.disponibilidad (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    psicologo_id integer NOT NULL,
    dia_semana smallint NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    duracion_slot smallint DEFAULT 50 NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL,
    fecha_actualizacion timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_disponibilidad_dia CHECK (((dia_semana >= 0) AND (dia_semana <= 6))),
    CONSTRAINT ck_disponibilidad_duracion CHECK (((duracion_slot >= 15) AND (duracion_slot <= 180))),
    CONSTRAINT ck_disponibilidad_horas CHECK ((hora_fin > hora_inicio))
);


ALTER TABLE citas_schema.disponibilidad OWNER TO postgres;

--
-- Name: excepciones_disponibilidad; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.excepciones_disponibilidad (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    psicologo_id integer NOT NULL,
    fecha date NOT NULL,
    motivo character varying(255),
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE citas_schema.excepciones_disponibilidad OWNER TO postgres;

--
-- Name: historial_cambios_citas; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.historial_cambios_citas (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cita_id uuid NOT NULL,
    accion character varying(40) DEFAULT 'CAMBIO_ESTADO'::character varying NOT NULL,
    estado_anterior character varying(20),
    estado_nuevo character varying(20) NOT NULL,
    cambiado_por integer NOT NULL,
    motivo text,
    datos_anteriores jsonb,
    datos_nuevos jsonb,
    fecha_cambio timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE citas_schema.historial_cambios_citas OWNER TO postgres;

--
-- Name: comprobantes; Type: TABLE; Schema: pagos_schema; Owner: postgres
--

CREATE TABLE pagos_schema.comprobantes (
    id integer NOT NULL,
    pago_id integer NOT NULL,
    url_comprobante text,
    creado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE pagos_schema.comprobantes OWNER TO postgres;

--
-- Name: comprobantes_id_seq; Type: SEQUENCE; Schema: pagos_schema; Owner: postgres
--

CREATE SEQUENCE pagos_schema.comprobantes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pagos_schema.comprobantes_id_seq OWNER TO postgres;

--
-- Name: comprobantes_id_seq; Type: SEQUENCE OWNED BY; Schema: pagos_schema; Owner: postgres
--

ALTER SEQUENCE pagos_schema.comprobantes_id_seq OWNED BY pagos_schema.comprobantes.id;


--
-- Name: pagos; Type: TABLE; Schema: pagos_schema; Owner: postgres
--

CREATE TABLE pagos_schema.pagos (
    id integer NOT NULL,
    usuario_id integer,
    monto numeric(12,2) NOT NULL,
    moneda character varying(10) DEFAULT 'USD'::character varying NOT NULL,
    estado character varying(60) DEFAULT 'pendiente'::character varying NOT NULL,
    creado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE pagos_schema.pagos OWNER TO postgres;

--
-- Name: pagos_id_seq; Type: SEQUENCE; Schema: pagos_schema; Owner: postgres
--

CREATE SEQUENCE pagos_schema.pagos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pagos_schema.pagos_id_seq OWNER TO postgres;

--
-- Name: pagos_id_seq; Type: SEQUENCE OWNED BY; Schema: pagos_schema; Owner: postgres
--

ALTER SEQUENCE pagos_schema.pagos_id_seq OWNED BY pagos_schema.pagos.id;


--
-- Name: transacciones; Type: TABLE; Schema: pagos_schema; Owner: postgres
--

CREATE TABLE pagos_schema.transacciones (
    id integer NOT NULL,
    pago_id integer NOT NULL,
    proveedor character varying(80) NOT NULL,
    proveedor_id character varying(255),
    monto numeric(12,2),
    estado character varying(80) NOT NULL,
    registrado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE pagos_schema.transacciones OWNER TO postgres;

--
-- Name: transacciones_id_seq; Type: SEQUENCE; Schema: pagos_schema; Owner: postgres
--

CREATE SEQUENCE pagos_schema.transacciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pagos_schema.transacciones_id_seq OWNER TO postgres;

--
-- Name: transacciones_id_seq; Type: SEQUENCE OWNED BY; Schema: pagos_schema; Owner: postgres
--

ALTER SEQUENCE pagos_schema.transacciones_id_seq OWNED BY pagos_schema.transacciones.id;


--
-- Name: historial_sesiones; Type: TABLE; Schema: teleconsulta_schema; Owner: postgres
--

CREATE TABLE teleconsulta_schema.historial_sesiones (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    sesion_id uuid NOT NULL,
    evento character varying(80) NOT NULL,
    actor_id integer,
    data jsonb,
    registrado_en timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE teleconsulta_schema.historial_sesiones OWNER TO postgres;

--
-- Name: sesiones_zoom; Type: TABLE; Schema: teleconsulta_schema; Owner: postgres
--

CREATE TABLE teleconsulta_schema.sesiones_zoom (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cita_id uuid NOT NULL,
    paciente_id integer NOT NULL,
    psicologo_id integer NOT NULL,
    zoom_meeting_id character varying(32),
    zoom_meeting_uuid character varying(255),
    zoom_host_user_id character varying(255),
    tema character varying(255) DEFAULT 'Teleconsulta PsicoConecta'::character varying NOT NULL,
    enlace_acceso text,
    contrasena character varying(64),
    fecha_hora_inicio timestamp with time zone NOT NULL,
    fecha_hora_fin timestamp with time zone NOT NULL,
    estado character varying(20) DEFAULT 'PROGRAMADA'::character varying NOT NULL,
    ultimo_error text,
    ultima_sincronizacion_zoom timestamp with time zone,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_sesiones_zoom_estado CHECK (((estado)::text = ANY ((ARRAY['PROGRAMADA'::character varying, 'EN_CURSO'::character varying, 'FINALIZADA'::character varying, 'CANCELADA'::character varying, 'ERROR'::character varying])::text[]))),
    CONSTRAINT ck_sesiones_zoom_rango CHECK ((fecha_hora_fin > fecha_hora_inicio))
);


ALTER TABLE teleconsulta_schema.sesiones_zoom OWNER TO postgres;

--
-- Name: permisos; Type: TABLE; Schema: usuarios_schema; Owner: postgres
--

CREATE TABLE usuarios_schema.permisos (
    id integer NOT NULL,
    name character varying(80) NOT NULL,
    description character varying(255) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE usuarios_schema.permisos OWNER TO postgres;

--
-- Name: permisos_id_seq; Type: SEQUENCE; Schema: usuarios_schema; Owner: postgres
--

CREATE SEQUENCE usuarios_schema.permisos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE usuarios_schema.permisos_id_seq OWNER TO postgres;

--
-- Name: permisos_id_seq; Type: SEQUENCE OWNED BY; Schema: usuarios_schema; Owner: postgres
--

ALTER SEQUENCE usuarios_schema.permisos_id_seq OWNED BY usuarios_schema.permisos.id;


--
-- Name: roles; Type: TABLE; Schema: usuarios_schema; Owner: postgres
--

CREATE TABLE usuarios_schema.roles (
    id integer NOT NULL,
    name character varying(40) NOT NULL,
    description character varying(255) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE usuarios_schema.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: usuarios_schema; Owner: postgres
--

CREATE SEQUENCE usuarios_schema.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE usuarios_schema.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: usuarios_schema; Owner: postgres
--

ALTER SEQUENCE usuarios_schema.roles_id_seq OWNED BY usuarios_schema.roles.id;


--
-- Name: roles_permisos; Type: TABLE; Schema: usuarios_schema; Owner: postgres
--

CREATE TABLE usuarios_schema.roles_permisos (
    rol_id integer NOT NULL,
    permiso_id integer NOT NULL
);


ALTER TABLE usuarios_schema.roles_permisos OWNER TO postgres;

--
-- Name: tokens_recuperacion; Type: TABLE; Schema: usuarios_schema; Owner: postgres
--

CREATE TABLE usuarios_schema.tokens_recuperacion (
    id integer NOT NULL,
    token_hash character varying(64) NOT NULL,
    user_id integer NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    used_at timestamp without time zone
);


ALTER TABLE usuarios_schema.tokens_recuperacion OWNER TO postgres;

--
-- Name: tokens_recuperacion_id_seq; Type: SEQUENCE; Schema: usuarios_schema; Owner: postgres
--

CREATE SEQUENCE usuarios_schema.tokens_recuperacion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE usuarios_schema.tokens_recuperacion_id_seq OWNER TO postgres;

--
-- Name: tokens_recuperacion_id_seq; Type: SEQUENCE OWNED BY; Schema: usuarios_schema; Owner: postgres
--

ALTER SEQUENCE usuarios_schema.tokens_recuperacion_id_seq OWNED BY usuarios_schema.tokens_recuperacion.id;


--
-- Name: tokens_revocados; Type: TABLE; Schema: usuarios_schema; Owner: postgres
--

CREATE TABLE usuarios_schema.tokens_revocados (
    id integer NOT NULL,
    jti character varying(64) NOT NULL,
    revoked_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE usuarios_schema.tokens_revocados OWNER TO postgres;

--
-- Name: tokens_revocados_id_seq; Type: SEQUENCE; Schema: usuarios_schema; Owner: postgres
--

CREATE SEQUENCE usuarios_schema.tokens_revocados_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE usuarios_schema.tokens_revocados_id_seq OWNER TO postgres;

--
-- Name: tokens_revocados_id_seq; Type: SEQUENCE OWNED BY; Schema: usuarios_schema; Owner: postgres
--

ALTER SEQUENCE usuarios_schema.tokens_revocados_id_seq OWNED BY usuarios_schema.tokens_revocados.id;


--
-- Name: usuarios; Type: TABLE; Schema: usuarios_schema; Owner: postgres
--

CREATE TABLE usuarios_schema.usuarios (
    id integer NOT NULL,
    cognito_sub character varying(255),
    google_id character varying(255),
    first_name character varying(80) NOT NULL,
    last_name character varying(80) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    phone character varying(30),
    birth_date date,
    role_id integer NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE usuarios_schema.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: usuarios_schema; Owner: postgres
--

CREATE SEQUENCE usuarios_schema.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE usuarios_schema.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: usuarios_schema; Owner: postgres
--

ALTER SEQUENCE usuarios_schema.usuarios_id_seq OWNED BY usuarios_schema.usuarios.id;


--
-- Name: comprobantes id; Type: DEFAULT; Schema: pagos_schema; Owner: postgres
--

ALTER TABLE ONLY pagos_schema.comprobantes ALTER COLUMN id SET DEFAULT nextval('pagos_schema.comprobantes_id_seq'::regclass);


--
-- Name: pagos id; Type: DEFAULT; Schema: pagos_schema; Owner: postgres
--

ALTER TABLE ONLY pagos_schema.pagos ALTER COLUMN id SET DEFAULT nextval('pagos_schema.pagos_id_seq'::regclass);


--
-- Name: transacciones id; Type: DEFAULT; Schema: pagos_schema; Owner: postgres
--

ALTER TABLE ONLY pagos_schema.transacciones ALTER COLUMN id SET DEFAULT nextval('pagos_schema.transacciones_id_seq'::regclass);


--
-- Name: permisos id; Type: DEFAULT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.permisos ALTER COLUMN id SET DEFAULT nextval('usuarios_schema.permisos_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.roles ALTER COLUMN id SET DEFAULT nextval('usuarios_schema.roles_id_seq'::regclass);


--
-- Name: tokens_recuperacion id; Type: DEFAULT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.tokens_recuperacion ALTER COLUMN id SET DEFAULT nextval('usuarios_schema.tokens_recuperacion_id_seq'::regclass);


--
-- Name: tokens_revocados id; Type: DEFAULT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.tokens_revocados ALTER COLUMN id SET DEFAULT nextval('usuarios_schema.tokens_revocados_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.usuarios ALTER COLUMN id SET DEFAULT nextval('usuarios_schema.usuarios_id_seq'::regclass);


--
-- Data for Name: citas; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.citas (id, paciente_id, psicologo_id, fecha_hora_inicio, fecha_hora_fin, estado, modalidad, motivo_consulta, notas_psicologo, motivo_cancelacion, cancelado_por, reprogramada_desde, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: disponibilidad; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.disponibilidad (id, psicologo_id, dia_semana, hora_inicio, hora_fin, duracion_slot, activo, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: excepciones_disponibilidad; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.excepciones_disponibilidad (id, psicologo_id, fecha, motivo, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: historial_cambios_citas; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.historial_cambios_citas (id, cita_id, accion, estado_anterior, estado_nuevo, cambiado_por, motivo, datos_anteriores, datos_nuevos, fecha_cambio) FROM stdin;
\.


--
-- Data for Name: comprobantes; Type: TABLE DATA; Schema: pagos_schema; Owner: postgres
--

COPY pagos_schema.comprobantes (id, pago_id, url_comprobante, creado_en) FROM stdin;
\.


--
-- Data for Name: pagos; Type: TABLE DATA; Schema: pagos_schema; Owner: postgres
--

COPY pagos_schema.pagos (id, usuario_id, monto, moneda, estado, creado_en) FROM stdin;
\.


--
-- Data for Name: transacciones; Type: TABLE DATA; Schema: pagos_schema; Owner: postgres
--

COPY pagos_schema.transacciones (id, pago_id, proveedor, proveedor_id, monto, estado, registrado_en) FROM stdin;
\.


--
-- Data for Name: historial_sesiones; Type: TABLE DATA; Schema: teleconsulta_schema; Owner: postgres
--

COPY teleconsulta_schema.historial_sesiones (id, sesion_id, evento, actor_id, data, registrado_en) FROM stdin;
\.


--
-- Data for Name: sesiones_zoom; Type: TABLE DATA; Schema: teleconsulta_schema; Owner: postgres
--

COPY teleconsulta_schema.sesiones_zoom (id, cita_id, paciente_id, psicologo_id, zoom_meeting_id, zoom_meeting_uuid, zoom_host_user_id, tema, enlace_acceso, contrasena, fecha_hora_inicio, fecha_hora_fin, estado, ultimo_error, ultima_sincronizacion_zoom, creado_en, actualizado_en) FROM stdin;
\.


--
-- Data for Name: permisos; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.permisos (id, name, description) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.roles (id, name, description) FROM stdin;
\.


--
-- Data for Name: roles_permisos; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.roles_permisos (rol_id, permiso_id) FROM stdin;
\.


--
-- Data for Name: tokens_recuperacion; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.tokens_recuperacion (id, token_hash, user_id, expires_at, used_at) FROM stdin;
\.


--
-- Data for Name: tokens_revocados; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.tokens_revocados (id, jti, revoked_at) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.usuarios (id, cognito_sub, google_id, first_name, last_name, email, password_hash, phone, birth_date, role_id, status, created_at, updated_at) FROM stdin;
\.


--
-- Name: comprobantes_id_seq; Type: SEQUENCE SET; Schema: pagos_schema; Owner: postgres
--

SELECT pg_catalog.setval('pagos_schema.comprobantes_id_seq', 1, false);


--
-- Name: pagos_id_seq; Type: SEQUENCE SET; Schema: pagos_schema; Owner: postgres
--

SELECT pg_catalog.setval('pagos_schema.pagos_id_seq', 1, false);


--
-- Name: transacciones_id_seq; Type: SEQUENCE SET; Schema: pagos_schema; Owner: postgres
--

SELECT pg_catalog.setval('pagos_schema.transacciones_id_seq', 1, false);


--
-- Name: permisos_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.permisos_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.roles_id_seq', 1, false);


--
-- Name: tokens_recuperacion_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.tokens_recuperacion_id_seq', 1, false);


--
-- Name: tokens_revocados_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.tokens_revocados_id_seq', 1, false);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.usuarios_id_seq', 1, false);


--
-- Name: citas citas_pkey; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.citas
    ADD CONSTRAINT citas_pkey PRIMARY KEY (id);


--
-- Name: disponibilidad disponibilidad_pkey; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.disponibilidad
    ADD CONSTRAINT disponibilidad_pkey PRIMARY KEY (id);


--
-- Name: excepciones_disponibilidad excepciones_disponibilidad_pkey; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.excepciones_disponibilidad
    ADD CONSTRAINT excepciones_disponibilidad_pkey PRIMARY KEY (id);


--
-- Name: historial_cambios_citas historial_cambios_citas_pkey; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.historial_cambios_citas
    ADD CONSTRAINT historial_cambios_citas_pkey PRIMARY KEY (id);


--
-- Name: disponibilidad uq_disponibilidad_bloque; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.disponibilidad
    ADD CONSTRAINT uq_disponibilidad_bloque UNIQUE (psicologo_id, dia_semana, hora_inicio, hora_fin);


--
-- Name: excepciones_disponibilidad uq_excepcion_psicologo_fecha; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.excepciones_disponibilidad
    ADD CONSTRAINT uq_excepcion_psicologo_fecha UNIQUE (psicologo_id, fecha);


--
-- Name: comprobantes comprobantes_pkey; Type: CONSTRAINT; Schema: pagos_schema; Owner: postgres
--

ALTER TABLE ONLY pagos_schema.comprobantes
    ADD CONSTRAINT comprobantes_pkey PRIMARY KEY (id);


--
-- Name: pagos pagos_pkey; Type: CONSTRAINT; Schema: pagos_schema; Owner: postgres
--

ALTER TABLE ONLY pagos_schema.pagos
    ADD CONSTRAINT pagos_pkey PRIMARY KEY (id);


--
-- Name: transacciones transacciones_pkey; Type: CONSTRAINT; Schema: pagos_schema; Owner: postgres
--

ALTER TABLE ONLY pagos_schema.transacciones
    ADD CONSTRAINT transacciones_pkey PRIMARY KEY (id);


--
-- Name: historial_sesiones historial_sesiones_pkey; Type: CONSTRAINT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.historial_sesiones
    ADD CONSTRAINT historial_sesiones_pkey PRIMARY KEY (id);


--
-- Name: sesiones_zoom sesiones_zoom_cita_id_key; Type: CONSTRAINT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.sesiones_zoom
    ADD CONSTRAINT sesiones_zoom_cita_id_key UNIQUE (cita_id);


--
-- Name: sesiones_zoom sesiones_zoom_pkey; Type: CONSTRAINT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.sesiones_zoom
    ADD CONSTRAINT sesiones_zoom_pkey PRIMARY KEY (id);


--
-- Name: sesiones_zoom sesiones_zoom_zoom_meeting_id_key; Type: CONSTRAINT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.sesiones_zoom
    ADD CONSTRAINT sesiones_zoom_zoom_meeting_id_key UNIQUE (zoom_meeting_id);


--
-- Name: permisos permisos_name_key; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.permisos
    ADD CONSTRAINT permisos_name_key UNIQUE (name);


--
-- Name: permisos permisos_pkey; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.permisos
    ADD CONSTRAINT permisos_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles_permisos roles_permisos_pkey; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.roles_permisos
    ADD CONSTRAINT roles_permisos_pkey PRIMARY KEY (rol_id, permiso_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: tokens_recuperacion tokens_recuperacion_pkey; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.tokens_recuperacion
    ADD CONSTRAINT tokens_recuperacion_pkey PRIMARY KEY (id);


--
-- Name: tokens_recuperacion tokens_recuperacion_token_hash_key; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.tokens_recuperacion
    ADD CONSTRAINT tokens_recuperacion_token_hash_key UNIQUE (token_hash);


--
-- Name: tokens_revocados tokens_revocados_jti_key; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.tokens_revocados
    ADD CONSTRAINT tokens_revocados_jti_key UNIQUE (jti);


--
-- Name: tokens_revocados tokens_revocados_pkey; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.tokens_revocados
    ADD CONSTRAINT tokens_revocados_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_cognito_sub_key; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.usuarios
    ADD CONSTRAINT usuarios_cognito_sub_key UNIQUE (cognito_sub);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_google_id_key; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.usuarios
    ADD CONSTRAINT usuarios_google_id_key UNIQUE (google_id);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: ix_citas_estado; Type: INDEX; Schema: citas_schema; Owner: postgres
--

CREATE INDEX ix_citas_estado ON citas_schema.citas USING btree (estado);


--
-- Name: ix_citas_paciente_inicio; Type: INDEX; Schema: citas_schema; Owner: postgres
--

CREATE INDEX ix_citas_paciente_inicio ON citas_schema.citas USING btree (paciente_id, fecha_hora_inicio);


--
-- Name: ix_citas_psicologo_inicio; Type: INDEX; Schema: citas_schema; Owner: postgres
--

CREATE INDEX ix_citas_psicologo_inicio ON citas_schema.citas USING btree (psicologo_id, fecha_hora_inicio);


--
-- Name: ix_disponibilidad_psicologo_dia; Type: INDEX; Schema: citas_schema; Owner: postgres
--

CREATE INDEX ix_disponibilidad_psicologo_dia ON citas_schema.disponibilidad USING btree (psicologo_id, dia_semana);


--
-- Name: ix_excepcion_psicologo_fecha; Type: INDEX; Schema: citas_schema; Owner: postgres
--

CREATE INDEX ix_excepcion_psicologo_fecha ON citas_schema.excepciones_disponibilidad USING btree (psicologo_id, fecha);


--
-- Name: ix_historial_cita_fecha; Type: INDEX; Schema: citas_schema; Owner: postgres
--

CREATE INDEX ix_historial_cita_fecha ON citas_schema.historial_cambios_citas USING btree (cita_id, fecha_cambio);


--
-- Name: ix_historial_sesion_fecha; Type: INDEX; Schema: teleconsulta_schema; Owner: postgres
--

CREATE INDEX ix_historial_sesion_fecha ON teleconsulta_schema.historial_sesiones USING btree (sesion_id, registrado_en);


--
-- Name: ix_sesiones_zoom_cita; Type: INDEX; Schema: teleconsulta_schema; Owner: postgres
--

CREATE INDEX ix_sesiones_zoom_cita ON teleconsulta_schema.sesiones_zoom USING btree (cita_id);


--
-- Name: ix_sesiones_zoom_estado; Type: INDEX; Schema: teleconsulta_schema; Owner: postgres
--

CREATE INDEX ix_sesiones_zoom_estado ON teleconsulta_schema.sesiones_zoom USING btree (estado);


--
-- Name: ix_sesiones_zoom_paciente_inicio; Type: INDEX; Schema: teleconsulta_schema; Owner: postgres
--

CREATE INDEX ix_sesiones_zoom_paciente_inicio ON teleconsulta_schema.sesiones_zoom USING btree (paciente_id, fecha_hora_inicio);


--
-- Name: ix_sesiones_zoom_psicologo_inicio; Type: INDEX; Schema: teleconsulta_schema; Owner: postgres
--

CREATE INDEX ix_sesiones_zoom_psicologo_inicio ON teleconsulta_schema.sesiones_zoom USING btree (psicologo_id, fecha_hora_inicio);


--
-- Name: historial_sesiones fk_historial_sesion; Type: FK CONSTRAINT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.historial_sesiones
    ADD CONSTRAINT fk_historial_sesion FOREIGN KEY (sesion_id) REFERENCES teleconsulta_schema.sesiones_zoom(id) ON DELETE CASCADE;


--
-- Name: roles_permisos roles_permisos_permiso_id_fkey; Type: FK CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.roles_permisos
    ADD CONSTRAINT roles_permisos_permiso_id_fkey FOREIGN KEY (permiso_id) REFERENCES usuarios_schema.permisos(id);


--
-- Name: roles_permisos roles_permisos_rol_id_fkey; Type: FK CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.roles_permisos
    ADD CONSTRAINT roles_permisos_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES usuarios_schema.roles(id);


--
-- Name: tokens_recuperacion tokens_recuperacion_user_id_fkey; Type: FK CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.tokens_recuperacion
    ADD CONSTRAINT tokens_recuperacion_user_id_fkey FOREIGN KEY (user_id) REFERENCES usuarios_schema.usuarios(id);


--
-- Name: usuarios usuarios_role_id_fkey; Type: FK CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.usuarios
    ADD CONSTRAINT usuarios_role_id_fkey FOREIGN KEY (role_id) REFERENCES usuarios_schema.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict ual5twuE46eWt9EKOvu3Ww0Jc3agZLQPeu4bahPCzSk6F4Jf8koLtzsqcEW43kf

