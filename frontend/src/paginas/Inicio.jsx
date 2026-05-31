import { motion } from "framer-motion";
import {
  Activity,
  ArrowRight,
  BadgeCheck,
  CalendarCheck2,
  CalendarHeart,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  CreditCard,
  HeartHandshake,
  HeartPulse,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Sparkles,
  UserRoundCheck,
  UsersRound,
  Video,
} from "lucide-react";
import { Link } from "react-router-dom";
import BarraNavegacion from "../componentes/BarraNavegacion";
import Logo from "../componentes/Logo";
import TarjetaCaracteristica from "../componentes/TarjetaCaracteristica";

const beneficiosPacientes = [
  {
    icono: CalendarHeart,
    titulo: "Agenda tus citas fácilmente",
    texto: "Organiza tus espacios de atención desde una experiencia clara y sencilla.",
  },
  {
    icono: Video,
    titulo: "Conéctate desde cualquier lugar",
    texto: "Accede a tus sesiones virtuales y mantén la continuidad de tu proceso.",
  },
  {
    icono: HeartPulse,
    titulo: "Recibe acompañamiento emocional",
    texto: "Lleva un seguimiento cercano de tu bienestar a lo largo del tiempo.",
  },
  {
    icono: ClipboardCheck,
    titulo: "Consulta tu historial",
    texto: "Encuentra la información importante de tu atención en un solo espacio.",
  },
];

const beneficiosPsicologos = [
  {
    icono: Clock3,
    titulo: "Organiza tus horarios",
    texto: "Mantén tu agenda ordenada y visualiza tus próximos espacios de atención.",
  },
  {
    icono: UsersRound,
    titulo: "Gestiona pacientes y citas",
    texto: "Centraliza la información esencial para brindar una experiencia más cercana.",
  },
  {
    icono: Video,
    titulo: "Atiende por videollamada",
    texto: "Facilita sesiones virtuales integradas dentro del recorrido de atención.",
  },
  {
    icono: Activity,
    titulo: "Revisa el progreso emocional",
    texto: "Acompaña cada proceso con una visión clara de su evolución.",
  },
];

const modulos = [
  { icono: LockKeyhole, titulo: "Acceso seguro y rápido", texto: "Ingresa a tu espacio personal con una experiencia protegida." },
  { icono: CalendarCheck2, titulo: "Agenda inteligente de citas", texto: "Mantén cada encuentro organizado y fácil de consultar." },
  { icono: Video, titulo: "Sesiones virtuales integradas", texto: "Conéctate con comodidad cuando llegue el momento de tu cita." },
  { icono: Activity, titulo: "Seguimiento del bienestar emocional", texto: "Observa avances y conserva la continuidad de cada proceso." },
  { icono: CreditCard, titulo: "Pagos organizados", texto: "Consulta la información económica de tu atención con claridad." },
  { icono: UserRoundCheck, titulo: "Experiencias según cada rol", texto: "Pacientes y profesionales encuentran justo lo que necesitan." },
];

const pasos = [
  { numero: "01", titulo: "Crea tu cuenta", texto: "Regístrate y accede a tu espacio personal." },
  { numero: "02", titulo: "Agenda tu cita", texto: "Elige el espacio que mejor se adapte a ti." },
  { numero: "03", titulo: "Conéctate a tu sesión", texto: "Accede a tu encuentro virtual de forma simple." },
  { numero: "04", titulo: "Continúa tu seguimiento", texto: "Mantén tu proceso organizado en un solo lugar." },
];

const aparicion = {
  oculto: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

function Revelar({ children, className = "", demora = 0 }) {
  return (
    <motion.div
      className={className}
      variants={aparicion}
      initial="oculto"
      whileInView="visible"
      viewport={{ once: true, amount: 0.18 }}
      transition={{ duration: 0.55, delay: demora, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

function EncabezadoSeccion({ etiqueta, titulo, texto, centrado = false }) {
  return (
    <div className={centrado ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}>
      <p className="etiqueta">{etiqueta}</p>
      <h2 className="mt-4 text-3xl font-black tracking-tight text-slate-900 dark:text-white sm:text-4xl">
        {titulo}
      </h2>
      {texto && (
        <p className="mt-4 text-base leading-7 text-slate-600 dark:text-slate-300 sm:text-lg">
          {texto}
        </p>
      )}
    </div>
  );
}

export default function Inicio() {
  return (
    <>
      <BarraNavegacion />
      <main>
        <section id="inicio" className="relative isolate overflow-hidden py-20 sm:py-28 lg:py-32">
          <div className="absolute inset-x-0 top-0 -z-20 h-full bg-gradient-to-b from-blue-50/90 via-slate-50 to-slate-50 dark:from-blue-950/25 dark:via-slate-950 dark:to-slate-950" />
          <div className="absolute -left-20 top-16 -z-10 h-72 w-72 rounded-full bg-cyan-200/40 blur-3xl dark:bg-cyan-900/20" />
          <div className="absolute right-0 top-8 -z-10 h-96 w-96 rounded-full bg-indigo-200/45 blur-3xl dark:bg-indigo-900/20" />
          <div className="contenedor grid items-center gap-14 lg:grid-cols-[1.08fr_.92fr]">
            <motion.div
              initial={{ opacity: 0, x: -28 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.65, ease: "easeOut" }}
            >
              <span className="inline-flex items-center gap-2 rounded-full border border-blue-200/80 bg-white/70 px-4 py-2 text-xs font-bold text-blue-700 shadow-sm backdrop-blur dark:border-blue-900/70 dark:bg-slate-900/70 dark:text-blue-300">
                <Sparkles size={15} />
                Tu bienestar, mejor acompañado
              </span>
              <h1 className="mt-7 max-w-4xl text-4xl font-black leading-[1.06] tracking-tight text-slate-950 dark:text-white sm:text-6xl">
                Conecta con apoyo psicológico de forma{" "}
                <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 bg-clip-text text-transparent dark:from-blue-300 dark:via-violet-300 dark:to-cyan-300">
                  segura, simple y cercana
                </span>
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
                PsicoConecta facilita la gestión de citas, sesiones virtuales, pagos y
                seguimiento emocional en una sola plataforma pensada para pacientes y
                profesionales.
              </p>
              <div className="mt-9 flex flex-wrap gap-4">
                <Link to="/registro" className="boton-primario">
                  Comenzar ahora <ArrowRight size={18} />
                </Link>
                <Link to="/iniciar-sesion" className="boton-secundario">
                  Iniciar sesión
                </Link>
              </div>
              <div className="mt-9 flex flex-wrap gap-x-6 gap-y-3 text-sm font-semibold text-slate-600 dark:text-slate-300">
                {["Atención organizada", "Información privada", "Acompañamiento continuo"].map((texto) => (
                  <span key={texto} className="flex items-center gap-2">
                    <CheckCircle2 size={17} className="text-cyan-600 dark:text-cyan-300" />
                    {texto}
                  </span>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.65, delay: 0.12, ease: "easeOut" }}
              className="relative mx-auto w-full max-w-xl"
            >
              <div className="absolute -inset-5 -z-10 rounded-[2.5rem] bg-gradient-to-br from-blue-300/35 via-indigo-300/25 to-cyan-200/35 blur-2xl dark:from-blue-900/30 dark:via-indigo-900/20 dark:to-cyan-900/20" />
              <div className="overflow-hidden rounded-[2rem] border border-white/80 bg-white/85 p-5 shadow-2xl backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-900/85 sm:p-7">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-300">
                      Tu próxima cita
                    </p>
                    <h2 className="mt-2 text-xl font-black text-slate-900 dark:text-white">
                      Un espacio para ti
                    </h2>
                  </div>
                  <span className="icono-panel">
                    <HeartHandshake size={22} />
                  </span>
                </div>
                <div className="mt-6 rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-600 p-5 text-white">
                  <div className="flex items-center justify-between gap-4">
                    <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-bold">Confirmada</span>
                    <CalendarHeart size={21} />
                  </div>
                  <p className="mt-8 text-sm text-blue-100">Sesión virtual</p>
                  <p className="mt-1 text-xl font-black">Jueves, 10:30 a. m.</p>
                  <button type="button" className="mt-5 inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-xs font-black text-blue-700 shadow-sm">
                    Ver detalles <ArrowRight size={15} />
                  </button>
                </div>
                <div className="mt-4 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-2xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/70">
                    <Activity size={19} className="text-cyan-600 dark:text-cyan-300" />
                    <p className="mt-3 text-sm font-black text-slate-800 dark:text-white">Seguimiento cercano</p>
                    <p className="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">Tu proceso en un solo lugar</p>
                  </div>
                  <div className="rounded-2xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/70">
                    <ShieldCheck size={19} className="text-indigo-600 dark:text-indigo-300" />
                    <p className="mt-3 text-sm font-black text-slate-800 dark:text-white">Acceso protegido</p>
                    <p className="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">Tu información es privada</p>
                  </div>
                </div>
              </div>
              <motion.div
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -bottom-7 -left-4 hidden rounded-2xl border border-white/80 bg-white/90 p-4 shadow-xl backdrop-blur dark:border-slate-700 dark:bg-slate-800/90 sm:block"
              >
                <div className="flex items-center gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-cyan-50 text-cyan-600 dark:bg-cyan-950 dark:text-cyan-300">
                    <BadgeCheck size={20} />
                  </span>
                  <div>
                    <p className="text-xs font-black text-slate-800 dark:text-white">Proceso acompañado</p>
                    <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">Simple, humano y seguro</p>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </section>

        <section id="beneficios" className="py-20 sm:py-24">
          <div className="contenedor">
            <Revelar>
              <EncabezadoSeccion
                etiqueta="Pensado para pacientes"
                titulo="Tu atención psicológica, mucho más fácil de gestionar"
                texto="Encuentra lo importante de tu proceso en una plataforma cercana, clara y disponible cuando la necesites."
                centrado
              />
            </Revelar>
            <div className="mt-11 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {beneficiosPacientes.map((beneficio, indice) => (
                <TarjetaCaracteristica key={beneficio.titulo} {...beneficio} demora={indice * 0.07} />
              ))}
            </div>
          </div>
        </section>

        <section className="bg-white/70 py-20 dark:bg-slate-900/45 sm:py-24">
          <div className="contenedor">
            <Revelar>
              <EncabezadoSeccion
                etiqueta="Una experiencia integral"
                titulo="Todo lo que necesitas para avanzar con tranquilidad"
                texto="PsicoConecta reúne herramientas útiles para que cada etapa de la atención se sienta más ordenada y accesible."
              />
            </Revelar>
            <div className="mt-11 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {modulos.map(({ icono: Icono, titulo, texto }, indice) => (
                <Revelar key={titulo} demora={indice * 0.06}>
                  <article className="group h-full rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">
                    <span className="icono-panel transition duration-300 group-hover:bg-blue-600 group-hover:text-white">
                      <Icono size={22} />
                    </span>
                    <h3 className="mt-5 text-lg font-black text-slate-900 dark:text-white">{titulo}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{texto}</p>
                  </article>
                </Revelar>
              ))}
            </div>
          </div>
        </section>

        <section id="psicologos" className="py-20 sm:py-24">
          <div className="contenedor">
            <div className="overflow-hidden rounded-[2.25rem] bg-gradient-to-br from-slate-950 via-blue-900 to-indigo-950 px-6 py-10 text-white shadow-2xl sm:px-10 sm:py-14 lg:px-14">
              <div className="grid gap-12 lg:grid-cols-[.9fr_1.1fr] lg:items-center">
                <Revelar>
                  <p className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">Para psicólogos</p>
                  <h2 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">
                    Más tiempo para acompañar, menos tiempo organizando
                  </h2>
                  <p className="mt-4 leading-7 text-blue-100/80">
                    Gestiona tu atención profesional desde un espacio diseñado para trabajar
                    con claridad, continuidad y cercanía.
                  </p>
                  <Link to="/registro" className="mt-7 inline-flex items-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-black text-blue-700 transition hover:-translate-y-0.5 hover:shadow-lg">
                    Crear mi cuenta <ArrowRight size={17} />
                  </Link>
                </Revelar>
                <div className="grid gap-3 sm:grid-cols-2">
                  {beneficiosPsicologos.map(({ icono: Icono, titulo, texto }, indice) => (
                    <Revelar key={titulo} demora={indice * 0.07}>
                      <article className="h-full rounded-2xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                        <Icono size={21} className="text-cyan-300" />
                        <h3 className="mt-4 font-black">{titulo}</h3>
                        <p className="mt-2 text-sm leading-6 text-blue-100/75">{texto}</p>
                      </article>
                    </Revelar>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="como-funciona" className="bg-blue-50/60 py-20 dark:bg-blue-950/10 sm:py-24">
          <div className="contenedor">
            <Revelar>
              <EncabezadoSeccion
                etiqueta="Cómo funciona"
                titulo="Comenzar es más sencillo de lo que imaginas"
                texto="Un recorrido claro para mantener tu atención organizada desde el primer día."
                centrado
              />
            </Revelar>
            <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              {pasos.map(({ numero, titulo, texto }, indice) => (
                <Revelar key={numero} demora={indice * 0.08}>
                  <article className="relative h-full rounded-3xl border border-blue-100 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <span className="text-4xl font-black text-blue-100 dark:text-slate-700">{numero}</span>
                    <h3 className="mt-5 text-lg font-black text-slate-900 dark:text-white">{titulo}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{texto}</p>
                  </article>
                </Revelar>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20 sm:py-24">
          <div className="contenedor grid gap-10 lg:grid-cols-[.9fr_1.1fr] lg:items-center">
            <Revelar>
              <EncabezadoSeccion
                etiqueta="Confianza y privacidad"
                titulo="Tu información merece un espacio cuidado"
                texto="Cada persona accede a una experiencia pensada para proteger la privacidad y mantener la atención organizada."
              />
              <Link to="/registro" className="boton-secundario mt-7">
                Conocer la plataforma <ArrowRight size={17} />
              </Link>
            </Revelar>
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                { icono: ShieldCheck, titulo: "Acceso seguro", texto: "Tu cuenta personal mantiene tu información protegida." },
                { icono: LockKeyhole, titulo: "Información privada", texto: "Tus datos se presentan únicamente en el espacio que corresponde." },
                { icono: UserRoundCheck, titulo: "Roles diferenciados", texto: "Cada perfil accede a las herramientas necesarias para su experiencia." },
                { icono: HeartHandshake, titulo: "Plataforma confiable", texto: "Una experiencia diseñada alrededor del cuidado y la cercanía." },
              ].map(({ icono: Icono, titulo, texto }, indice) => (
                <Revelar key={titulo} demora={indice * 0.07}>
                  <article className="panel h-full p-5">
                    <Icono size={21} className="text-blue-600 dark:text-blue-300" />
                    <h3 className="mt-4 font-black text-slate-900 dark:text-white">{titulo}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{texto}</p>
                  </article>
                </Revelar>
              ))}
            </div>
          </div>
        </section>

        <section className="pb-20 sm:pb-24">
          <div className="contenedor">
            <Revelar>
              <div className="relative overflow-hidden rounded-[2.25rem] bg-gradient-to-r from-blue-700 via-indigo-700 to-violet-700 px-7 py-12 text-center text-white shadow-2xl sm:px-12 sm:py-16">
                <div className="absolute -left-16 -top-20 h-56 w-56 rounded-full bg-cyan-300/20 blur-3xl" />
                <div className="absolute -bottom-24 right-0 h-64 w-64 rounded-full bg-violet-300/25 blur-3xl" />
                <div className="relative mx-auto max-w-3xl">
                  <p className="text-xs font-bold uppercase tracking-[0.24em] text-blue-100">Da el primer paso</p>
                  <h2 className="mt-4 text-3xl font-black tracking-tight sm:text-4xl">
                    Empieza a gestionar tu atención psicológica de una forma más humana,
                    organizada y segura.
                  </h2>
                  <Link to="/registro" className="mt-8 inline-flex items-center gap-2 rounded-2xl bg-white px-6 py-3 text-sm font-black text-blue-700 shadow-lg transition hover:-translate-y-0.5">
                    Crear mi cuenta <ArrowRight size={18} />
                  </Link>
                </div>
              </div>
            </Revelar>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white py-12 dark:border-slate-800 dark:bg-slate-950">
        <div className="contenedor grid gap-9 md:grid-cols-[1.4fr_.8fr_.8fr]">
          <div>
            <Logo />
            <p className="mt-4 max-w-sm text-sm leading-6 text-slate-500 dark:text-slate-400">
              Atención psicológica más cercana, organizada y accesible para pacientes y profesionales.
            </p>
          </div>
          <div>
            <p className="text-sm font-black text-slate-900 dark:text-white">Enlaces rápidos</p>
            <div className="mt-4 flex flex-col gap-3">
              <a href="/#beneficios" className="enlace">Beneficios</a>
              <a href="/#como-funciona" className="enlace">Cómo funciona</a>
              <Link to="/iniciar-sesion" className="enlace">Iniciar sesión</Link>
            </div>
          </div>
          <div>
            <p className="text-sm font-black text-slate-900 dark:text-white">Contacto</p>
            <a href="mailto:soporte@psicoconecta.ec" className="mt-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-blue-700 dark:text-slate-400 dark:hover:text-blue-300">
              <Mail size={16} /> soporte@psicoconecta.ec
            </a>
          </div>
        </div>
        <div className="contenedor mt-10 border-t border-slate-100 pt-6 text-xs text-slate-400 dark:border-slate-800">
          &copy; 2026 PsicoConecta. Todos los derechos reservados.
        </div>
      </footer>
    </>
  );
}
