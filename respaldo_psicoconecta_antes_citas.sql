--
-- PostgreSQL database dump
--

\restrict kXTiWobAybK5oZwuuNbpUO6PIQVTgjLbrZGwYpZRrvOfIDIm9hwRXVvbvgcP4Nr

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: citas; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.citas (
    id integer NOT NULL,
    paciente_id integer,
    psicologo_id integer,
    fecha timestamp without time zone NOT NULL,
    estado character varying(40) DEFAULT 'pendiente'::character varying NOT NULL,
    descripcion text,
    creado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE citas_schema.citas OWNER TO postgres;

--
-- Name: citas_id_seq; Type: SEQUENCE; Schema: citas_schema; Owner: postgres
--

CREATE SEQUENCE citas_schema.citas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE citas_schema.citas_id_seq OWNER TO postgres;

--
-- Name: citas_id_seq; Type: SEQUENCE OWNED BY; Schema: citas_schema; Owner: postgres
--

ALTER SEQUENCE citas_schema.citas_id_seq OWNED BY citas_schema.citas.id;


--
-- Name: disponibilidad; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.disponibilidad (
    id uuid NOT NULL,
    psicologo_id integer NOT NULL,
    dia_semana smallint NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    duracion_slot smallint,
    activo boolean,
    fecha_creacion timestamp with time zone,
    fecha_actualizacion timestamp with time zone
);


ALTER TABLE citas_schema.disponibilidad OWNER TO postgres;

--
-- Name: excepciones_disponibilidad; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.excepciones_disponibilidad (
    id uuid NOT NULL,
    psicologo_id integer NOT NULL,
    fecha date NOT NULL,
    motivo character varying(255),
    fecha_creacion timestamp with time zone
);


ALTER TABLE citas_schema.excepciones_disponibilidad OWNER TO postgres;

--
-- Name: historial_cambios_citas; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.historial_cambios_citas (
    id uuid NOT NULL,
    cita_id uuid NOT NULL,
    estado_anterior character varying(20),
    estado_nuevo character varying(20) NOT NULL,
    cambiado_por integer NOT NULL,
    motivo text,
    fecha_cambio timestamp with time zone
);


ALTER TABLE citas_schema.historial_cambios_citas OWNER TO postgres;

--
-- Name: historial_citas; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.historial_citas (
    id integer NOT NULL,
    cita_id integer NOT NULL,
    evento character varying(255) NOT NULL,
    detalle text,
    registrado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE citas_schema.historial_citas OWNER TO postgres;

--
-- Name: historial_citas_id_seq; Type: SEQUENCE; Schema: citas_schema; Owner: postgres
--

CREATE SEQUENCE citas_schema.historial_citas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE citas_schema.historial_citas_id_seq OWNER TO postgres;

--
-- Name: historial_citas_id_seq; Type: SEQUENCE OWNED BY; Schema: citas_schema; Owner: postgres
--

ALTER SEQUENCE citas_schema.historial_citas_id_seq OWNED BY citas_schema.historial_citas.id;


--
-- Name: horarios_disponibles; Type: TABLE; Schema: citas_schema; Owner: postgres
--

CREATE TABLE citas_schema.horarios_disponibles (
    id integer NOT NULL,
    psicologo_id integer NOT NULL,
    fecha_inicio timestamp without time zone NOT NULL,
    fecha_fin timestamp without time zone NOT NULL,
    creado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE citas_schema.horarios_disponibles OWNER TO postgres;

--
-- Name: horarios_disponibles_id_seq; Type: SEQUENCE; Schema: citas_schema; Owner: postgres
--

CREATE SEQUENCE citas_schema.horarios_disponibles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE citas_schema.horarios_disponibles_id_seq OWNER TO postgres;

--
-- Name: horarios_disponibles_id_seq; Type: SEQUENCE OWNED BY; Schema: citas_schema; Owner: postgres
--

ALTER SEQUENCE citas_schema.horarios_disponibles_id_seq OWNED BY citas_schema.horarios_disponibles.id;


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
    id integer NOT NULL,
    sesion_id integer NOT NULL,
    evento character varying(255) NOT NULL,
    data jsonb,
    registrado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE teleconsulta_schema.historial_sesiones OWNER TO postgres;

--
-- Name: historial_sesiones_id_seq; Type: SEQUENCE; Schema: teleconsulta_schema; Owner: postgres
--

CREATE SEQUENCE teleconsulta_schema.historial_sesiones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE teleconsulta_schema.historial_sesiones_id_seq OWNER TO postgres;

--
-- Name: historial_sesiones_id_seq; Type: SEQUENCE OWNED BY; Schema: teleconsulta_schema; Owner: postgres
--

ALTER SEQUENCE teleconsulta_schema.historial_sesiones_id_seq OWNED BY teleconsulta_schema.historial_sesiones.id;


--
-- Name: sesiones_zoom; Type: TABLE; Schema: teleconsulta_schema; Owner: postgres
--

CREATE TABLE teleconsulta_schema.sesiones_zoom (
    id integer NOT NULL,
    cita_id integer,
    zoom_meeting_id character varying(255),
    tema character varying(255),
    enlace_acceso text,
    estado character varying(60) DEFAULT 'pendiente'::character varying NOT NULL,
    creado_en timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE teleconsulta_schema.sesiones_zoom OWNER TO postgres;

--
-- Name: sesiones_zoom_id_seq; Type: SEQUENCE; Schema: teleconsulta_schema; Owner: postgres
--

CREATE SEQUENCE teleconsulta_schema.sesiones_zoom_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE teleconsulta_schema.sesiones_zoom_id_seq OWNER TO postgres;

--
-- Name: sesiones_zoom_id_seq; Type: SEQUENCE OWNED BY; Schema: teleconsulta_schema; Owner: postgres
--

ALTER SEQUENCE teleconsulta_schema.sesiones_zoom_id_seq OWNED BY teleconsulta_schema.sesiones_zoom.id;


--
-- Name: eventos_auditoria; Type: TABLE; Schema: usuarios_schema; Owner: postgres
--

CREATE TABLE usuarios_schema.eventos_auditoria (
    id integer NOT NULL,
    event_type character varying(80) NOT NULL,
    category character varying(40) NOT NULL,
    status character varying(20) NOT NULL,
    actor_user_id integer,
    target_user_id integer,
    actor_email character varying(255),
    target_email character varying(255),
    ip_address character varying(64),
    user_agent character varying(255),
    detail text,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE usuarios_schema.eventos_auditoria OWNER TO postgres;

--
-- Name: eventos_auditoria_id_seq; Type: SEQUENCE; Schema: usuarios_schema; Owner: postgres
--

CREATE SEQUENCE usuarios_schema.eventos_auditoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE usuarios_schema.eventos_auditoria_id_seq OWNER TO postgres;

--
-- Name: eventos_auditoria_id_seq; Type: SEQUENCE OWNED BY; Schema: usuarios_schema; Owner: postgres
--

ALTER SEQUENCE usuarios_schema.eventos_auditoria_id_seq OWNED BY usuarios_schema.eventos_auditoria.id;


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
-- Name: citas id; Type: DEFAULT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.citas ALTER COLUMN id SET DEFAULT nextval('citas_schema.citas_id_seq'::regclass);


--
-- Name: historial_citas id; Type: DEFAULT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.historial_citas ALTER COLUMN id SET DEFAULT nextval('citas_schema.historial_citas_id_seq'::regclass);


--
-- Name: horarios_disponibles id; Type: DEFAULT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.horarios_disponibles ALTER COLUMN id SET DEFAULT nextval('citas_schema.horarios_disponibles_id_seq'::regclass);


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
-- Name: historial_sesiones id; Type: DEFAULT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.historial_sesiones ALTER COLUMN id SET DEFAULT nextval('teleconsulta_schema.historial_sesiones_id_seq'::regclass);


--
-- Name: sesiones_zoom id; Type: DEFAULT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.sesiones_zoom ALTER COLUMN id SET DEFAULT nextval('teleconsulta_schema.sesiones_zoom_id_seq'::regclass);


--
-- Name: eventos_auditoria id; Type: DEFAULT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.eventos_auditoria ALTER COLUMN id SET DEFAULT nextval('usuarios_schema.eventos_auditoria_id_seq'::regclass);


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

COPY citas_schema.citas (id, paciente_id, psicologo_id, fecha, estado, descripcion, creado_en) FROM stdin;
\.


--
-- Data for Name: disponibilidad; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.disponibilidad (id, psicologo_id, dia_semana, hora_inicio, hora_fin, duracion_slot, activo, fecha_creacion, fecha_actualizacion) FROM stdin;
7f1014d5-5c38-41c5-be5a-e843265f6cf5	2	0	08:00:00	12:00:00	60	t	2026-06-30 02:43:12.647212+00	2026-06-30 02:43:12.647215+00
bd146e95-4274-4ba9-a71e-f75db7782ece	2	0	14:00:00	17:00:00	60	t	2026-06-30 02:43:12.647221+00	2026-06-30 02:43:12.647221+00
1fa3cf0f-2b0f-4bde-9eb3-f64c950252a5	2	1	08:00:00	12:00:00	60	t	2026-06-30 02:43:12.647225+00	2026-06-30 02:43:12.647225+00
84891af7-7bda-496e-88ec-c9c52a032bfc	2	1	14:00:00	17:00:00	60	t	2026-06-30 02:43:12.647233+00	2026-06-30 02:43:12.647234+00
352370c5-245e-4fbb-889b-21d5b0550a0e	2	2	08:00:00	12:00:00	60	t	2026-06-30 02:43:12.647237+00	2026-06-30 02:43:12.647237+00
a3ed8248-0813-4ca9-b508-6e27211e1c73	2	2	14:00:00	17:00:00	60	t	2026-06-30 02:43:12.64724+00	2026-06-30 02:43:12.64724+00
44e065db-38fd-473e-be04-c2aa936663a6	2	3	08:00:00	12:00:00	60	t	2026-06-30 02:43:12.647242+00	2026-06-30 02:43:12.647243+00
8c3c79c1-25f0-4f88-bd8c-6e5faf35158a	2	3	14:00:00	17:00:00	60	t	2026-06-30 02:43:12.647246+00	2026-06-30 02:43:12.647247+00
92d1aaa7-b3c3-4b46-872e-443e44a48a58	2	4	08:00:00	12:00:00	60	t	2026-06-30 02:43:12.647249+00	2026-06-30 02:43:12.64725+00
6d2a377d-a08c-4b6a-9473-91142f3a273d	2	4	14:00:00	17:00:00	60	t	2026-06-30 02:43:12.647252+00	2026-06-30 02:43:12.647252+00
\.


--
-- Data for Name: excepciones_disponibilidad; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.excepciones_disponibilidad (id, psicologo_id, fecha, motivo, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: historial_cambios_citas; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.historial_cambios_citas (id, cita_id, estado_anterior, estado_nuevo, cambiado_por, motivo, fecha_cambio) FROM stdin;
\.


--
-- Data for Name: historial_citas; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.historial_citas (id, cita_id, evento, detalle, registrado_en) FROM stdin;
\.


--
-- Data for Name: horarios_disponibles; Type: TABLE DATA; Schema: citas_schema; Owner: postgres
--

COPY citas_schema.horarios_disponibles (id, psicologo_id, fecha_inicio, fecha_fin, creado_en) FROM stdin;
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

COPY teleconsulta_schema.historial_sesiones (id, sesion_id, evento, data, registrado_en) FROM stdin;
\.


--
-- Data for Name: sesiones_zoom; Type: TABLE DATA; Schema: teleconsulta_schema; Owner: postgres
--

COPY teleconsulta_schema.sesiones_zoom (id, cita_id, zoom_meeting_id, tema, enlace_acceso, estado, creado_en) FROM stdin;
\.


--
-- Data for Name: eventos_auditoria; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.eventos_auditoria (id, event_type, category, status, actor_user_id, target_user_id, actor_email, target_email, ip_address, user_agent, detail, created_at) FROM stdin;
1	login_failed	autenticacion	failure	\N	\N	ferminencaladaleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"motivo": "credenciales_invalidas", "modulo": "Usuarios", "severidad": "Media", "canal": "Web", "accion": "Inicio de sesi├│n local fallido"}	2026-06-28 16:31:33.594483
2	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/inicio-sesion", "codigo_respuesta": 400, "tiempo_respuesta_ms": 103.96, "descripcion": "Acceso a /api/usuarios/autenticacion/inicio-sesion finalizado con 400.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 16:31:33.616015
3	register_success	autenticacion	success	\N	5	\N	ferminencaladaleiva@gmail.com	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"metodo": "formulario", "modulo": "Usuarios", "severidad": "Baja", "canal": "Web", "accion": "Registro exitoso"}	2026-06-28 16:32:25.955293
4	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/registro", "codigo_respuesta": 201, "tiempo_respuesta_ms": 431.3, "descripcion": "Acceso a /api/usuarios/autenticacion/registro finalizado con 201.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:25.965606
5	login_success	autenticacion	success	5	\N	ferminencaladaleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"metodo": "correo", "modulo": "Usuarios", "severidad": "Baja", "canal": "Web", "accion": "Inicio de sesi├│n local exitoso"}	2026-06-28 16:32:36.582488
6	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/inicio-sesion", "codigo_respuesta": 200, "tiempo_respuesta_ms": 334.1, "descripcion": "Acceso a /api/usuarios/autenticacion/inicio-sesion finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:36.611819
7	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/5/foto-perfil", "codigo_respuesta": 404, "tiempo_respuesta_ms": 7.8, "descripcion": "Acceso a /api/usuarios/5/foto-perfil finalizado con 404.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 16:32:36.783363
8	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 13.06, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:36.907937
9	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 6.8, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:36.927117
10	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 10.1, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:40.066119
11	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 15.65, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:40.107579
12	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 8.48, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:42.461191
13	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 27.8, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 16:32:42.504489
15	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/3/foto-perfil", "codigo_respuesta": 404, "tiempo_respuesta_ms": 14.14, "descripcion": "Acceso a /api/usuarios/3/foto-perfil finalizado con 404.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 16:32:42.539545
14	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/2/foto-perfil", "codigo_respuesta": 404, "tiempo_respuesta_ms": 10.27, "descripcion": "Acceso a /api/usuarios/2/foto-perfil finalizado con 404.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 16:32:42.538619
16	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/autenticacion/mi-perfil", "codigo_respuesta": 200, "tiempo_respuesta_ms": 66.16, "descripcion": "Acceso a /api/usuarios/autenticacion/mi-perfil finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 17:25:01.199204
17	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/autenticacion/mi-perfil", "codigo_respuesta": 200, "tiempo_respuesta_ms": 19.66, "descripcion": "Acceso a /api/usuarios/autenticacion/mi-perfil finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 17:25:01.336743
20	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 9.13, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 17:25:01.93466
23	auth_failed	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/autenticacion/mi-perfil", "codigo_respuesta": 401, "tiempo_respuesta_ms": 7.59, "descripcion": "Acceso a /api/usuarios/autenticacion/mi-perfil finalizado con 401.", "severidad": "Media", "canal": "API", "accion": "Token inv├ílido o acceso sin auth"}	2026-06-28 20:01:51.068844
26	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/inicio-sesion", "codigo_respuesta": 400, "tiempo_respuesta_ms": 653.54, "descripcion": "Acceso a /api/usuarios/autenticacion/inicio-sesion finalizado con 400.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 20:02:03.07304
29	login_failed	autenticacion	failure	\N	\N	ferminencaladaleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"motivo": "credenciales_invalidas", "modulo": "Usuarios", "severidad": "Media", "canal": "Web", "accion": "Inicio de sesi├│n local fallido"}	2026-06-28 20:04:39.056347
31	register_success	autenticacion	success	\N	6	\N	joseferminleiva@gmail.com	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"metodo": "formulario", "modulo": "Usuarios", "severidad": "Baja", "canal": "Web", "accion": "Registro exitoso"}	2026-06-28 20:05:23.530738
34	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/inicio-sesion", "codigo_respuesta": 400, "tiempo_respuesta_ms": 459.15, "descripcion": "Acceso a /api/usuarios/autenticacion/inicio-sesion finalizado con 400.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 20:05:35.386742
36	login_success	autenticacion	success	5	\N	ferminencaladaleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"metodo": "correo", "modulo": "Usuarios", "severidad": "Baja", "canal": "Web", "accion": "Inicio de sesi├│n local exitoso"}	2026-06-28 20:06:30.253134
39	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 11.07, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 20:06:30.506588
41	logout	autenticacion	success	5	\N	ferminencaladaleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "Usuarios", "severidad": "Baja", "canal": "Web", "accion": "Cierre de sesi├│n"}	2026-06-28 20:06:34.870607
18	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/5/foto-perfil", "codigo_respuesta": 404, "tiempo_respuesta_ms": 6.03, "descripcion": "Acceso a /api/usuarios/5/foto-perfil finalizado con 404.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 17:25:01.741591
22	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/2/foto-perfil", "codigo_respuesta": 404, "tiempo_respuesta_ms": 3.2, "descripcion": "Acceso a /api/usuarios/2/foto-perfil finalizado con 404.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 17:25:02.116646
24	auth_failed	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/autenticacion/mi-perfil", "codigo_respuesta": 401, "tiempo_respuesta_ms": 0.59, "descripcion": "Acceso a /api/usuarios/autenticacion/mi-perfil finalizado con 401.", "severidad": "Media", "canal": "API", "accion": "Token inv├ílido o acceso sin auth"}	2026-06-28 20:01:51.145225
27	login_failed	autenticacion	failure	\N	\N	ferminencaladaleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"motivo": "credenciales_invalidas", "modulo": "Usuarios", "severidad": "Media", "canal": "Web", "accion": "Inicio de sesi├│n local fallido"}	2026-06-28 20:02:09.539145
30	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/inicio-sesion", "codigo_respuesta": 400, "tiempo_respuesta_ms": 335.79, "descripcion": "Acceso a /api/usuarios/autenticacion/inicio-sesion finalizado con 400.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 20:04:39.076607
32	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/registro", "codigo_respuesta": 201, "tiempo_respuesta_ms": 341.72, "descripcion": "Acceso a /api/usuarios/autenticacion/registro finalizado con 201.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 20:05:23.539357
37	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/inicio-sesion", "codigo_respuesta": 200, "tiempo_respuesta_ms": 316.47, "descripcion": "Acceso a /api/usuarios/autenticacion/inicio-sesion finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 20:06:30.275458
40	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 7.48, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 20:06:30.524286
42	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/cierre-sesion", "codigo_respuesta": 200, "tiempo_respuesta_ms": 101.4, "descripcion": "Acceso a /api/usuarios/autenticacion/cierre-sesion finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 20:06:34.894353
19	api_request	rendimiento	success	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/psicologos", "codigo_respuesta": 200, "tiempo_respuesta_ms": 10.66, "descripcion": "Acceso a /api/usuarios/psicologos finalizado con 200.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n API"}	2026-06-28 17:25:01.871298
21	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/3/foto-perfil", "codigo_respuesta": 404, "tiempo_respuesta_ms": 4.97, "descripcion": "Acceso a /api/usuarios/3/foto-perfil finalizado con 404.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 17:25:02.117898
25	login_failed	autenticacion	failure	\N	\N	ferminencaladaleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"motivo": "credenciales_invalidas", "modulo": "Usuarios", "severidad": "Media", "canal": "Web", "accion": "Inicio de sesi├│n local fallido"}	2026-06-28 20:02:03.065477
28	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/inicio-sesion", "codigo_respuesta": 400, "tiempo_respuesta_ms": 499.58, "descripcion": "Acceso a /api/usuarios/autenticacion/inicio-sesion finalizado con 400.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 20:02:09.543985
33	login_failed	autenticacion	failure	\N	\N	joseferminleiva@gmail.com	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"motivo": "credenciales_invalidas", "modulo": "Usuarios", "severidad": "Media", "canal": "Web", "accion": "Inicio de sesi├│n local fallido"}	2026-06-28 20:05:35.367304
35	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "POST", "endpoint": "/api/usuarios/autenticacion/registro", "codigo_respuesta": 400, "tiempo_respuesta_ms": 11.37, "descripcion": "Acceso a /api/usuarios/autenticacion/registro finalizado con 400.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 20:06:15.769328
38	client_error	errores	failure	\N	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 OPR/132.0.0.0	{"modulo": "usuarios", "metodo_http": "GET", "endpoint": "/api/usuarios/5/foto-perfil", "codigo_respuesta": 404, "tiempo_respuesta_ms": 8.63, "descripcion": "Acceso a /api/usuarios/5/foto-perfil finalizado con 404.", "severidad": "Baja", "canal": "API", "accion": "Petici├│n de cliente inv├ílida"}	2026-06-28 20:06:30.418085
\.


--
-- Data for Name: permisos; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.permisos (id, name, description) FROM stdin;
1	manage_users	Crear, editar y desactivar usuarios.
2	manage_roles	Gestionar roles y permisos.
3	view_all_profiles	Consultar todos los perfiles.
4	manage_user_status	Activar o desactivar usuarios.
5	view_own_profile	Consultar el perfil propio.
6	edit_own_profile	Editar el perfil propio.
7	future_appointments	Acceder al modulo futuro de citas.
8	future_teleconsultations	Acceder al modulo futuro de teleconsultas.
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.roles (id, name, description) FROM stdin;
1	ADMIN	Rol ADMIN
2	PSYCHOLOGIST	Rol PSYCHOLOGIST
3	PATIENT	Rol PATIENT
\.


--
-- Data for Name: roles_permisos; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.roles_permisos (rol_id, permiso_id) FROM stdin;
1	3
1	4
1	2
1	1
2	5
2	7
2	6
2	8
3	5
3	7
3	6
3	8
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
1	8d0e7f17-75f2-4b81-b51c-f335ced8316b	2026-06-28 20:06:34.827803
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: usuarios_schema; Owner: postgres
--

COPY usuarios_schema.usuarios (id, cognito_sub, google_id, first_name, last_name, email, password_hash, phone, birth_date, role_id, status, created_at, updated_at) FROM stdin;
1	\N	\N	Admin	PsicoConecta	admin@psicoconecta.com	$2b$12$R4izY661mE6BT5XPhC0z3u3C/mlAOtj6o86fXQPFBRDB/DR8.rE9y	\N	\N	1	active	2026-06-28 16:24:50.556547	2026-06-28 16:24:50.556566
2	\N	\N	Psicologo	Demo	psicologo@psicoconecta.com	$2b$12$aLFK.7/4uxuKHXre0kzX3ODcOWlRIR0KSemABQqBUxps12AquKSpa	\N	\N	2	active	2026-06-28 16:24:50.923491	2026-06-28 16:24:50.923502
3	\N	\N	Laura	G├│mez	laura@psicoconecta.com	$2b$12$mgGR2JaMTkMQVp38WypH5OJk9jENcWVuGwv7Yhoq5owSFIv1kw8gq	\N	\N	2	active	2026-06-28 16:24:51.228036	2026-06-28 16:24:51.228045
4	\N	\N	Paciente	Demo	paciente@psicoconecta.com	$2b$12$OTW9tFyt8zkBBZrroAd0v.fKgipnm5mpmjoVZko4u408L4TvQR/ta	\N	\N	3	active	2026-06-28 16:24:51.604998	2026-06-28 16:24:51.605009
5	\N	\N	Jos├®	Encalada	ferminencaladaleiva@gmail.com	$2b$12$YIOCQSTbegDMaYkXjsrF0O49yq13/QivLb.jq/WjZKLGn/jiqIWt2	0981884898	2005-04-16	3	active	2026-06-28 16:32:25.93994	2026-06-28 16:32:25.939949
6	\N	\N	Jos├®	Encalada	joseferminleiva@gmail.com	$2b$12$RHglklT.khk0hIOquCNWAeq9wwUgWKY8JAdCkz41TtEJgLrPjOhmK	0981884898	2008-06-07	3	active	2026-06-28 20:05:23.523268	2026-06-28 20:05:23.523284
\.


--
-- Name: citas_id_seq; Type: SEQUENCE SET; Schema: citas_schema; Owner: postgres
--

SELECT pg_catalog.setval('citas_schema.citas_id_seq', 1, false);


--
-- Name: historial_citas_id_seq; Type: SEQUENCE SET; Schema: citas_schema; Owner: postgres
--

SELECT pg_catalog.setval('citas_schema.historial_citas_id_seq', 1, false);


--
-- Name: horarios_disponibles_id_seq; Type: SEQUENCE SET; Schema: citas_schema; Owner: postgres
--

SELECT pg_catalog.setval('citas_schema.horarios_disponibles_id_seq', 1, false);


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
-- Name: historial_sesiones_id_seq; Type: SEQUENCE SET; Schema: teleconsulta_schema; Owner: postgres
--

SELECT pg_catalog.setval('teleconsulta_schema.historial_sesiones_id_seq', 1, false);


--
-- Name: sesiones_zoom_id_seq; Type: SEQUENCE SET; Schema: teleconsulta_schema; Owner: postgres
--

SELECT pg_catalog.setval('teleconsulta_schema.sesiones_zoom_id_seq', 1, false);


--
-- Name: eventos_auditoria_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.eventos_auditoria_id_seq', 42, true);


--
-- Name: permisos_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.permisos_id_seq', 8, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.roles_id_seq', 3, true);


--
-- Name: tokens_recuperacion_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.tokens_recuperacion_id_seq', 1, false);


--
-- Name: tokens_revocados_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.tokens_revocados_id_seq', 1, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: usuarios_schema; Owner: postgres
--

SELECT pg_catalog.setval('usuarios_schema.usuarios_id_seq', 6, true);


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
-- Name: historial_citas historial_citas_pkey; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.historial_citas
    ADD CONSTRAINT historial_citas_pkey PRIMARY KEY (id);


--
-- Name: horarios_disponibles horarios_disponibles_pkey; Type: CONSTRAINT; Schema: citas_schema; Owner: postgres
--

ALTER TABLE ONLY citas_schema.horarios_disponibles
    ADD CONSTRAINT horarios_disponibles_pkey PRIMARY KEY (id);


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
-- Name: sesiones_zoom sesiones_zoom_pkey; Type: CONSTRAINT; Schema: teleconsulta_schema; Owner: postgres
--

ALTER TABLE ONLY teleconsulta_schema.sesiones_zoom
    ADD CONSTRAINT sesiones_zoom_pkey PRIMARY KEY (id);


--
-- Name: eventos_auditoria eventos_auditoria_pkey; Type: CONSTRAINT; Schema: usuarios_schema; Owner: postgres
--

ALTER TABLE ONLY usuarios_schema.eventos_auditoria
    ADD CONSTRAINT eventos_auditoria_pkey PRIMARY KEY (id);


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
-- Name: ix_usuarios_schema_eventos_auditoria_actor_user_id; Type: INDEX; Schema: usuarios_schema; Owner: postgres
--

CREATE INDEX ix_usuarios_schema_eventos_auditoria_actor_user_id ON usuarios_schema.eventos_auditoria USING btree (actor_user_id);


--
-- Name: ix_usuarios_schema_eventos_auditoria_category; Type: INDEX; Schema: usuarios_schema; Owner: postgres
--

CREATE INDEX ix_usuarios_schema_eventos_auditoria_category ON usuarios_schema.eventos_auditoria USING btree (category);


--
-- Name: ix_usuarios_schema_eventos_auditoria_created_at; Type: INDEX; Schema: usuarios_schema; Owner: postgres
--

CREATE INDEX ix_usuarios_schema_eventos_auditoria_created_at ON usuarios_schema.eventos_auditoria USING btree (created_at);


--
-- Name: ix_usuarios_schema_eventos_auditoria_event_type; Type: INDEX; Schema: usuarios_schema; Owner: postgres
--

CREATE INDEX ix_usuarios_schema_eventos_auditoria_event_type ON usuarios_schema.eventos_auditoria USING btree (event_type);


--
-- Name: ix_usuarios_schema_eventos_auditoria_status; Type: INDEX; Schema: usuarios_schema; Owner: postgres
--

CREATE INDEX ix_usuarios_schema_eventos_auditoria_status ON usuarios_schema.eventos_auditoria USING btree (status);


--
-- Name: ix_usuarios_schema_eventos_auditoria_target_user_id; Type: INDEX; Schema: usuarios_schema; Owner: postgres
--

CREATE INDEX ix_usuarios_schema_eventos_auditoria_target_user_id ON usuarios_schema.eventos_auditoria USING btree (target_user_id);


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

\unrestrict kXTiWobAybK5oZwuuNbpUO6PIQVTgjLbrZGwYpZRrvOfIDIm9hwRXVvbvgcP4Nr

