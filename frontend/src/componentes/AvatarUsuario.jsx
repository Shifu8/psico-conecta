import { useEffect, useMemo, useState } from "react";
import { UserRound } from "lucide-react";
import { resolverUrlFotoPerfil } from "../servicios/servicioAutenticacion";

const tamanos = {
  sm: "h-10 w-10 text-xs",
  md: "h-12 w-12 text-sm",
  lg: "h-20 w-20 text-xl",
  xl: "h-24 w-24 text-2xl",
};

const iconos = {
  sm: 18,
  md: 22,
  lg: 36,
  xl: 42,
};

export default function AvatarUsuario({ usuario, tamano = "md", className = "" }) {
  const [imagenFallida, setImagenFallida] = useState(false);
  const urlFoto = resolverUrlFotoPerfil(usuario);

  useEffect(() => {
    setImagenFallida(false);
  }, [urlFoto]);

  const iniciales = useMemo(() => {
    const partes = [usuario?.first_name, usuario?.last_name].filter(Boolean);
    const texto = partes.length ? partes : [usuario?.full_name || usuario?.email || ""];
    return texto
      .join(" ")
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((parte) => parte[0]?.toUpperCase())
      .join("");
  }, [usuario]);

  const claseTamano = tamanos[tamano] || tamanos.md;
  const contenidoAlterno = iniciales || <UserRound size={iconos[tamano] || iconos.md} />;

  return (
    <span
      className={`${claseTamano} grid shrink-0 place-items-center overflow-hidden rounded-2xl bg-blue-50 font-black text-blue-700 ring-1 ring-blue-100 dark:bg-blue-950/50 dark:text-blue-200 dark:ring-blue-900 ${className}`}
    >
      {urlFoto && !imagenFallida ? (
        <img
          src={urlFoto}
          alt=""
          className="h-full w-full object-cover"
          onError={() => setImagenFallida(true)}
        />
      ) : (
        contenidoAlterno
      )}
    </span>
  );
}
