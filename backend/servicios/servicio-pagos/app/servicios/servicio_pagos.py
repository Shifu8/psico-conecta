from datetime import timedelta
from decimal import Decimal
import uuid

from flask import current_app
from sqlalchemy import case, or_

from app import db
from app.modelos import Pago, Reembolso, Tarifa, TransaccionPago
from app.servicios.cliente_stripe import ClienteStripe
from app.utilidades.errores import ErrorDominio
from app.utilidades.tiempo import ahora_utc, asegurar_utc


ESTADOS_PAGADOS = {"PAGADO", "REEMBOLSO_PARCIAL", "REPROGRAMACION_PENDIENTE"}
ESTADOS_CHECKOUT = {"PENDIENTE", "CHECKOUT_ABIERTO", "FALLIDO", "EXPIRADO"}
ESTADOS_TERMINALES_SIN_PAGO = {"CANCELADO", "REEMBOLSADO"}


class ServicioPagos:
    @staticmethod
    def cliente_stripe():
        cliente = current_app.extensions.get("stripe_client")
        if cliente is None:
            cliente = ClienteStripe()
            current_app.extensions["stripe_client"] = cliente
        return cliente

    @staticmethod
    def _uuid(valor, campo="id"):
        try:
            return valor if isinstance(valor, uuid.UUID) else uuid.UUID(str(valor))
        except (TypeError, ValueError, AttributeError):
            raise ErrorDominio(
                f"El campo {campo} no contiene un UUID válido.",
                400,
                "datos_invalidos",
            ) from None

    @staticmethod
    def _cita_normalizada(cita):
        if not isinstance(cita, dict):
            raise ErrorDominio("Los datos de la cita no son válidos.")
        requeridos = {
            "id",
            "paciente_id",
            "psicologo_id",
            "fecha_hora_inicio",
            "fecha_hora_fin",
            "estado",
            "modalidad",
        }
        faltantes = sorted(requeridos - set(cita))
        if faltantes:
            raise ErrorDominio(
                "La cita no contiene todos los datos necesarios.",
                400,
                "datos_cita_incompletos",
                {"faltantes": faltantes},
            )
        inicio = asegurar_utc(cita["fecha_hora_inicio"])
        fin = asegurar_utc(cita["fecha_hora_fin"])
        if not inicio or not fin or fin <= inicio:
            raise ErrorDominio("El horario de la cita no es válido.")
        return {
            "id": ServicioPagos._uuid(cita["id"], "cita.id"),
            "paciente_id": int(cita["paciente_id"]),
            "psicologo_id": int(cita["psicologo_id"]),
            "inicio": inicio,
            "fin": fin,
            "estado": str(cita["estado"]).upper(),
            "modalidad": str(cita["modalidad"]).upper(),
            "reprogramada_desde": (
                ServicioPagos._uuid(cita["reprogramada_desde"], "cita.reprogramada_desde")
                if cita.get("reprogramada_desde")
                else None
            ),
        }

    @staticmethod
    def _registrar(
        pago,
        tipo,
        estado=None,
        monto_centavos=None,
        datos=None,
        proveedor_evento_id=None,
    ):
        transaccion = TransaccionPago(
            pago_id=pago.id,
            tipo=tipo,
            estado=estado or pago.estado,
            monto_centavos=monto_centavos,
            datos=datos or {},
            proveedor_evento_id=proveedor_evento_id,
        )
        db.session.add(transaccion)
        return transaccion

    @staticmethod
    def _estado_segun_reembolso(pago):
        reembolsado = int(pago.reembolsado_centavos or 0)
        if reembolsado <= 0:
            return "PAGADO"
        if reembolsado >= int(pago.monto_centavos):
            return "REEMBOLSADO"
        return "REEMBOLSO_PARCIAL"

    @staticmethod
    def _obtener_pago(pago_id, bloquear=False):
        pago_uuid = ServicioPagos._uuid(pago_id, "pago_id")
        consulta = Pago.query.filter_by(id=pago_uuid)
        if bloquear:
            consulta = consulta.with_for_update()
        pago = consulta.first()
        if not pago:
            raise ErrorDominio("El pago no existe.", 404, "pago_no_encontrado")
        return pago

    @staticmethod
    def _verificar_acceso(pago, usuario_id, rol):
        usuario_id = int(usuario_id)
        if rol == "ADMIN":
            return
        if rol == "PACIENTE" and int(pago.paciente_id) == usuario_id:
            return
        if rol == "PSICOLOGO" and int(pago.psicologo_id) == usuario_id:
            return
        raise ErrorDominio("No tienes acceso a este pago.", 403, "acceso_denegado")

    @staticmethod
    def _tarifa_para(cita):
        # Prioridad: profesional+modalidad, profesional+todas, global+modalidad, global+todas.
        prioridad = case(
            (
                (Tarifa.psicologo_id == cita["psicologo_id"])
                & (Tarifa.modalidad == cita["modalidad"]),
                1,
            ),
            (
                (Tarifa.psicologo_id == cita["psicologo_id"])
                & (Tarifa.modalidad == "TODAS"),
                2,
            ),
            (
                Tarifa.psicologo_id.is_(None)
                & (Tarifa.modalidad == cita["modalidad"]),
                3,
            ),
            else_=4,
        )
        tarifa = (
            Tarifa.query.filter(
                Tarifa.activa.is_(True),
                or_(Tarifa.psicologo_id == cita["psicologo_id"], Tarifa.psicologo_id.is_(None)),
                Tarifa.modalidad.in_([cita["modalidad"], "TODAS"]),
            )
            .order_by(prioridad.asc(), Tarifa.creado_en.desc())
            .first()
        )
        if tarifa:
            return int(tarifa.monto_centavos), tarifa.moneda.upper(), tarifa.id
        return (
            int(current_app.config["DEFAULT_CONSULTATION_PRICE_CENTS"]),
            current_app.config["DEFAULT_CURRENCY"].upper(),
            None,
        )

    @staticmethod
    def _actualizar_datos_cita(pago, cita):
        pago.paciente_id = cita["paciente_id"]
        pago.psicologo_id = cita["psicologo_id"]
        pago.modalidad = cita["modalidad"]
        pago.fecha_hora_inicio = cita["inicio"]
        pago.fecha_hora_fin = cita["fin"]
        pago.actualizado_en = ahora_utc()

    @staticmethod
    def _crear_pago(cita, actor_id=None):
        monto, moneda, tarifa_id = ServicioPagos._tarifa_para(cita)
        pago = Pago(
            cita_id=cita["id"],
            paciente_id=cita["paciente_id"],
            psicologo_id=cita["psicologo_id"],
            monto_centavos=monto,
            moneda=moneda,
            estado="PENDIENTE",
            modalidad=cita["modalidad"],
            fecha_hora_inicio=cita["inicio"],
            fecha_hora_fin=cita["fin"],
        )
        db.session.add(pago)
        db.session.flush()
        ServicioPagos._registrar(
            pago,
            "PAGO_CREADO",
            datos={
                "actor_id": actor_id,
                "tarifa_id": str(tarifa_id) if tarifa_id else None,
                "cita_estado": cita["estado"],
            },
        )
        return pago

    @staticmethod
    def _expirar_checkout(pago):
        if not pago.stripe_checkout_session_id:
            return
        try:
            ServicioPagos.cliente_stripe().expirar_checkout(pago.stripe_checkout_session_id)
        except ErrorDominio as error:
            current_app.logger.warning(
                "No se pudo expirar Checkout %s: %s",
                pago.stripe_checkout_session_id,
                error.mensaje,
            )
        pago.checkout_url = None
        pago.checkout_expira_en = None

    @staticmethod
    def _transferir_pago_reprogramado(cita, actor_id=None):
        if not cita.get("reprogramada_desde"):
            return None
        pago = (
            Pago.query.filter_by(cita_id=cita["reprogramada_desde"])
            .with_for_update()
            .first()
        )
        if not pago:
            return None
        if pago.estado in {"PAGADO", "REEMBOLSO_PARCIAL", "REPROGRAMACION_PENDIENTE"}:
            cita_anterior = pago.cita_id
            pago.cita_id = cita["id"]
            ServicioPagos._actualizar_datos_cita(pago, cita)
            pago.estado = ServicioPagos._estado_segun_reembolso(pago)
            pago.ultimo_error = None
            ServicioPagos._registrar(
                pago,
                "PAGO_TRANSFERIDO_REPROGRAMACION",
                datos={
                    "actor_id": actor_id,
                    "cita_anterior": str(cita_anterior),
                    "cita_nueva": str(cita["id"]),
                },
            )
            return pago
        if pago.estado in ESTADOS_CHECKOUT:
            ServicioPagos._expirar_checkout(pago)
            pago.estado = "CANCELADO"
            pago.cancelado_en = ahora_utc()
            ServicioPagos._registrar(
                pago,
                "PAGO_CANCELADO_REPROGRAMACION",
                datos={"actor_id": actor_id, "cita_nueva": str(cita["id"])},
            )
        return None

    @staticmethod
    def sincronizar_desde_cita(cita_raw, actor_id=None):
        cita = ServicioPagos._cita_normalizada(cita_raw)
        pago = Pago.query.filter_by(cita_id=cita["id"]).with_for_update().first()

        if cita["estado"] == "PENDIENTE":
            transferido = ServicioPagos._transferir_pago_reprogramado(cita, actor_id)
            if transferido:
                db.session.commit()
                return transferido
            return pago

        if cita["estado"] == "CONFIRMADA":
            if not pago:
                pago = ServicioPagos._transferir_pago_reprogramado(cita, actor_id)
            if not pago:
                pago = ServicioPagos._crear_pago(cita, actor_id)
            else:
                ServicioPagos._actualizar_datos_cita(pago, cita)
                if pago.estado in {"FALLIDO", "EXPIRADO"}:
                    pago.estado = "PENDIENTE"
                    pago.ultimo_error = None
                ServicioPagos._registrar(
                    pago,
                    "CITA_CONFIRMADA_VERIFICADA",
                    datos={"actor_id": actor_id},
                )
            db.session.commit()
            return pago

        if not pago:
            return None

        ServicioPagos._actualizar_datos_cita(pago, cita)

        if cita["estado"] == "REPROGRAMADA":
            if pago.estado in {"PAGADO", "REEMBOLSO_PARCIAL"}:
                pago.estado = "REPROGRAMACION_PENDIENTE"
            elif pago.estado in ESTADOS_CHECKOUT:
                ServicioPagos._expirar_checkout(pago)
                pago.estado = "CANCELADO"
                pago.cancelado_en = ahora_utc()
            ServicioPagos._registrar(
                pago,
                "CITA_REPROGRAMADA",
                datos={"actor_id": actor_id},
            )
            db.session.commit()
            return pago

        if cita["estado"] == "CANCELADA":
            if pago.estado in {"PAGADO", "REEMBOLSO_PARCIAL", "REPROGRAMACION_PENDIENTE"}:
                if current_app.config["AUTO_REFUND_ON_CANCEL"] and pago.saldo_reembolsable_centavos > 0:
                    return ServicioPagos._crear_reembolso(
                        pago,
                        solicitado_por=actor_id,
                        monto_centavos=pago.saldo_reembolsable_centavos,
                        razon="requested_by_customer",
                        nota="Reembolso automático por cancelación de la cita.",
                        automatico=True,
                    )
                pago.estado = "CANCELADO"
            elif pago.estado in ESTADOS_CHECKOUT:
                ServicioPagos._expirar_checkout(pago)
                pago.estado = "CANCELADO"
            pago.cancelado_en = ahora_utc()
            ServicioPagos._registrar(
                pago,
                "CITA_CANCELADA",
                datos={"actor_id": actor_id, "reembolso_automatico": current_app.config["AUTO_REFUND_ON_CANCEL"]},
            )
            db.session.commit()
            return pago

        if cita["estado"] in {"COMPLETADA", "NO_ASISTIDA"}:
            ServicioPagos._registrar(
                pago,
                f"CITA_{cita['estado']}",
                datos={"actor_id": actor_id},
            )
            db.session.commit()
        return pago

    @staticmethod
    def crear_checkout(pago, usuario_id, email=None):
        ServicioPagos._verificar_acceso(pago, usuario_id, "PACIENTE")
        if pago.estado in {"PAGADO", "REEMBOLSO_PARCIAL", "REPROGRAMACION_PENDIENTE"}:
            return pago
        if pago.estado in ESTADOS_TERMINALES_SIN_PAGO or pago.estado == "REEMBOLSO_PENDIENTE":
            raise ErrorDominio(
                "Este pago ya no admite un nuevo Checkout.",
                409,
                "pago_no_disponible",
            )
        if asegurar_utc(pago.fecha_hora_inicio) <= ahora_utc():
            raise ErrorDominio(
                "No se puede pagar una cita que ya comenzó.",
                409,
                "cita_iniciada",
            )

        if (
            pago.estado == "CHECKOUT_ABIERTO"
            and pago.checkout_url
            and asegurar_utc(pago.checkout_expira_en) > ahora_utc()
        ):
            return pago

        if pago.stripe_checkout_session_id:
            ServicioPagos._expirar_checkout(pago)

        expira = ahora_utc() + timedelta(minutes=current_app.config["CHECKOUT_EXPIRES_MINUTES"])
        intento = (
            TransaccionPago.query.filter_by(pago_id=pago.id, tipo="CHECKOUT_CREADO").count()
            + 1
        )
        metadata = {
            "pago_id": str(pago.id),
            "cita_id": str(pago.cita_id),
            "paciente_id": str(pago.paciente_id),
            "psicologo_id": str(pago.psicologo_id),
        }
        parametros = {
            "mode": "payment",
            "success_url": f"{current_app.config['FRONTEND_URL']}/pagos/resultado?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{current_app.config['FRONTEND_URL']}/pagos?cita_id={pago.cita_id}&cancelado=1",
            "client_reference_id": str(pago.id),
            "expires_at": int(expira.timestamp()),
            "locale": "auto",
            "submit_type": "book",
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": pago.moneda.lower(),
                        "unit_amount": int(pago.monto_centavos),
                        "product_data": {
                            "name": "Consulta psicológica PsicoConecta",
                            "description": f"Cita {pago.modalidad.lower()} programada",
                            "metadata": metadata,
                        },
                    },
                }
            ],
            "metadata": metadata,
            "payment_intent_data": {"metadata": metadata},
        }
        if email:
            parametros["customer_email"] = email

        idempotency_key = f"checkout_{uuid.uuid4().hex}"

        sesion = ServicioPagos.cliente_stripe().crear_checkout(
            parametros,
            idempotency_key=idempotency_key,
        )
        if not sesion.get("id") or not sesion.get("url"):
            raise ErrorDominio(
                "Stripe no devolvió un enlace de pago válido.",
                502,
                "checkout_incompleto",
            )
        pago.stripe_checkout_session_id = str(sesion["id"])
        pago.stripe_payment_intent_id = (
            str(sesion["payment_intent"]) if sesion.get("payment_intent") else None
        )
        pago.stripe_customer_id = str(sesion["customer"]) if sesion.get("customer") else None
        pago.checkout_url = sesion["url"]
        pago.checkout_expira_en = expira
        pago.estado = "CHECKOUT_ABIERTO"
        pago.ultimo_error = None
        pago.actualizado_en = ahora_utc()
        ServicioPagos._registrar(
            pago,
            "CHECKOUT_CREADO",
            monto_centavos=pago.monto_centavos,
            datos={
                "session_id": pago.stripe_checkout_session_id,
                "intento": intento,
                "idempotency_key": idempotency_key,
            },
        )
        db.session.commit()
        return pago

    @staticmethod
    def _extraer_objeto(valor):
        if hasattr(valor, "to_dict_recursive"):
            return valor.to_dict_recursive()
        if isinstance(valor, dict):
            return valor
        return {}

    @staticmethod
    def _comprobante_desde_checkout(sesion):
        intent = ServicioPagos._extraer_objeto(sesion.get("payment_intent"))
        charge = ServicioPagos._extraer_objeto(intent.get("latest_charge"))
        return charge.get("receipt_url")

    @staticmethod
    def _actualizar_desde_checkout(pago, sesion, evento_id=None, tipo_evento="CHECKOUT_SINCRONIZADO"):
        pago.stripe_checkout_session_id = str(sesion.get("id") or pago.stripe_checkout_session_id or "") or None
        intent = sesion.get("payment_intent")
        if isinstance(intent, dict):
            pago.stripe_payment_intent_id = str(intent.get("id")) if intent.get("id") else pago.stripe_payment_intent_id
        elif intent:
            pago.stripe_payment_intent_id = str(intent)
        if sesion.get("customer"):
            customer = sesion["customer"]
            pago.stripe_customer_id = str(customer.get("id") if isinstance(customer, dict) else customer)
        comprobante = ServicioPagos._comprobante_desde_checkout(sesion)
        if comprobante:
            pago.comprobante_url = comprobante

        payment_status = str(sesion.get("payment_status") or "").lower()
        session_status = str(sesion.get("status") or "").lower()
        if payment_status == "paid":
            pago.estado = "PAGADO"
            pago.pagado_en = pago.pagado_en or ahora_utc()
            pago.checkout_url = None
            pago.checkout_expira_en = None
            pago.ultimo_error = None
        elif session_status == "expired":
            pago.estado = "EXPIRADO"
            pago.checkout_url = None
            pago.checkout_expira_en = None
        elif session_status == "complete":
            pago.estado = "PROCESANDO"
        elif session_status == "open":
            pago.estado = "CHECKOUT_ABIERTO"
        pago.actualizado_en = ahora_utc()
        ServicioPagos._registrar(
            pago,
            tipo_evento,
            monto_centavos=int(sesion.get("amount_total") or pago.monto_centavos),
            datos={
                "session_status": session_status,
                "payment_status": payment_status,
            },
            proveedor_evento_id=evento_id,
        )
        return pago

    @staticmethod
    def sincronizar_checkout(session_id, usuario_id, rol):
        pago = Pago.query.filter_by(stripe_checkout_session_id=str(session_id)).with_for_update().first()
        if not pago:
            raise ErrorDominio("No se encontró el pago asociado a esa sesión.", 404, "pago_no_encontrado")
        ServicioPagos._verificar_acceso(pago, usuario_id, rol)
        sesion = ServicioPagos.cliente_stripe().obtener_checkout(str(session_id))
        ServicioPagos._actualizar_desde_checkout(pago, sesion)
        db.session.commit()
        return pago

    @staticmethod
    def _crear_reembolso(
        pago,
        solicitado_por,
        monto_centavos,
        razon,
        nota=None,
        automatico=False,
    ):
        monto_centavos = int(monto_centavos or pago.saldo_reembolsable_centavos)
        if pago.estado not in {"PAGADO", "REEMBOLSO_PARCIAL", "REPROGRAMACION_PENDIENTE"}:
            raise ErrorDominio(
                "El pago no está disponible para reembolso.",
                409,
                "pago_no_reembolsable",
            )
        if not pago.stripe_payment_intent_id:
            raise ErrorDominio(
                "El pago no tiene un PaymentIntent de Stripe asociado.",
                409,
                "payment_intent_no_disponible",
            )
        if monto_centavos <= 0 or monto_centavos > pago.saldo_reembolsable_centavos:
            raise ErrorDominio(
                "El monto supera el saldo reembolsable.",
                400,
                "monto_reembolso_invalido",
                {"saldo_reembolsable_centavos": pago.saldo_reembolsable_centavos},
            )

        reembolso = Reembolso(
            pago_id=pago.id,
            solicitado_por=int(solicitado_por) if solicitado_por is not None else None,
            monto_centavos=monto_centavos,
            razon=razon,
            nota=nota,
            estado="PROCESANDO",
        )
        db.session.add(reembolso)
        db.session.flush()
        pago.estado = "REEMBOLSO_PENDIENTE"
        pago.actualizado_en = ahora_utc()

        try:
            respuesta = ServicioPagos.cliente_stripe().crear_reembolso(
                pago.stripe_payment_intent_id,
                monto_centavos,
                razon,
                metadata={
                    "pago_id": str(pago.id),
                    "reembolso_id": str(reembolso.id),
                    "cita_id": str(pago.cita_id),
                },
                idempotency_key=f"refund:{reembolso.id}",
            )
            reembolso.stripe_refund_id = str(respuesta.get("id")) if respuesta.get("id") else None
            estado_stripe = str(respuesta.get("status") or "pending").lower()
            if estado_stripe == "succeeded":
                reembolso.estado = "EXITOSO"
                pago.reembolsado_centavos += monto_centavos
                pago.estado = ServicioPagos._estado_segun_reembolso(pago)
                pago.ultimo_error = None
            elif estado_stripe in {"failed", "canceled"}:
                reembolso.estado = "FALLIDO" if estado_stripe == "failed" else "CANCELADO"
                pago.estado = ServicioPagos._estado_segun_reembolso(pago)
                reembolso.ultimo_error = respuesta.get("failure_reason")
                pago.ultimo_error = reembolso.ultimo_error
            else:
                reembolso.estado = "PENDIENTE"
                pago.estado = "REEMBOLSO_PENDIENTE"
            ServicioPagos._registrar(
                pago,
                "REEMBOLSO_AUTOMATICO" if automatico else "REEMBOLSO_SOLICITADO",
                monto_centavos=monto_centavos,
                datos={
                    "reembolso_id": str(reembolso.id),
                    "stripe_refund_id": reembolso.stripe_refund_id,
                    "estado_stripe": estado_stripe,
                    "razon": razon,
                },
            )
            db.session.commit()
            return pago
        except ErrorDominio as error:
            reembolso.estado = "FALLIDO"
            reembolso.ultimo_error = error.mensaje
            pago.estado = ServicioPagos._estado_segun_reembolso(pago)
            pago.ultimo_error = error.mensaje
            ServicioPagos._registrar(
                pago,
                "REEMBOLSO_FALLIDO",
                monto_centavos=monto_centavos,
                datos={"mensaje": error.mensaje, "automatico": automatico},
            )
            db.session.commit()
            raise

    @staticmethod
    def crear_reembolso(pago_id, solicitado_por, monto_centavos=None, razon="requested_by_customer", nota=None):
        pago = ServicioPagos._obtener_pago(pago_id, bloquear=True)
        return ServicioPagos._crear_reembolso(
            pago,
            solicitado_por,
            monto_centavos or pago.saldo_reembolsable_centavos,
            razon,
            nota,
            automatico=False,
        )

    @staticmethod
    def _pago_desde_objeto_stripe(objeto):
        metadata = objeto.get("metadata") or {}
        pago_id = metadata.get("pago_id")
        if pago_id:
            try:
                return Pago.query.filter_by(id=ServicioPagos._uuid(pago_id)).with_for_update().first()
            except ErrorDominio:
                return None
        if objeto.get("id") and str(objeto.get("id")).startswith("cs_"):
            return Pago.query.filter_by(stripe_checkout_session_id=str(objeto["id"])).with_for_update().first()
        if objeto.get("payment_intent"):
            payment_intent = objeto["payment_intent"]
            if isinstance(payment_intent, dict):
                payment_intent = payment_intent.get("id")
            return Pago.query.filter_by(stripe_payment_intent_id=str(payment_intent)).with_for_update().first()
        return None

    @staticmethod
    def procesar_webhook(payload, firma):
        evento = ServicioPagos.cliente_stripe().construir_evento(
            payload,
            firma,
            current_app.config["STRIPE_WEBHOOK_SECRET"],
        )
        evento_id = str(evento.get("id") or "")
        if evento_id and TransaccionPago.query.filter_by(proveedor_evento_id=evento_id).first():
            return {"recibido": True, "duplicado": True}

        tipo = str(evento.get("type") or "")
        objeto = ((evento.get("data") or {}).get("object") or {})
        pago = ServicioPagos._pago_desde_objeto_stripe(objeto)
        if not pago:
            return {"recibido": True, "ignorado": True}

        if tipo in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
            sesion = objeto
            if not isinstance(sesion.get("payment_intent"), dict):
                try:
                    sesion = ServicioPagos.cliente_stripe().obtener_checkout(str(objeto["id"]))
                except ErrorDominio:
                    sesion = objeto
            ServicioPagos._actualizar_desde_checkout(
                pago,
                sesion,
                evento_id=evento_id or None,
                tipo_evento=tipo,
            )
        elif tipo in {"checkout.session.expired", "checkout.session.async_payment_failed"}:
            pago.estado = "EXPIRADO" if tipo.endswith("expired") else "FALLIDO"
            pago.checkout_url = None
            pago.checkout_expira_en = None
            pago.ultimo_error = "El pago no se completó." if tipo.endswith("failed") else None
            ServicioPagos._registrar(
                pago,
                tipo,
                proveedor_evento_id=evento_id or None,
            )
        elif tipo == "payment_intent.payment_failed":
            pago.estado = "FALLIDO"
            error = objeto.get("last_payment_error") or {}
            pago.ultimo_error = error.get("message") or "Stripe informó que el pago falló."
            ServicioPagos._registrar(
                pago,
                tipo,
                datos={"mensaje": pago.ultimo_error},
                proveedor_evento_id=evento_id or None,
            )
        elif tipo in {"refund.created", "refund.updated", "refund.failed"}:
            metadata = objeto.get("metadata") or {}
            reembolso = None
            if metadata.get("reembolso_id"):
                try:
                    reembolso = Reembolso.query.filter_by(
                        id=ServicioPagos._uuid(metadata["reembolso_id"])
                    ).first()
                except ErrorDominio:
                    reembolso = None
            if not reembolso and objeto.get("id"):
                reembolso = Reembolso.query.filter_by(stripe_refund_id=str(objeto["id"])).first()
            if reembolso:
                reembolso.stripe_refund_id = str(objeto.get("id") or reembolso.stripe_refund_id)
                estado = str(objeto.get("status") or "pending").lower()
                if estado == "succeeded" and reembolso.estado != "EXITOSO":
                    reembolso.estado = "EXITOSO"
                    pago.reembolsado_centavos = min(
                        pago.monto_centavos,
                        int(pago.reembolsado_centavos or 0) + int(reembolso.monto_centavos),
                    )
                    pago.estado = ServicioPagos._estado_segun_reembolso(pago)
                elif estado in {"failed", "canceled"}:
                    # Un reembolso de tarjeta puede aparecer inicialmente como exitoso
                    # y fallar después. Si ya lo contabilizamos, debemos revertirlo.
                    if reembolso.estado == "EXITOSO":
                        pago.reembolsado_centavos = max(
                            0,
                            int(pago.reembolsado_centavos or 0)
                            - int(reembolso.monto_centavos),
                        )
                    reembolso.estado = "FALLIDO" if estado == "failed" else "CANCELADO"
                    reembolso.ultimo_error = objeto.get("failure_reason")
                    pago.estado = ServicioPagos._estado_segun_reembolso(pago)
                    pago.ultimo_error = reembolso.ultimo_error
                else:
                    reembolso.estado = "PENDIENTE"
                    pago.estado = "REEMBOLSO_PENDIENTE"
            ServicioPagos._registrar(
                pago,
                tipo,
                monto_centavos=int(objeto.get("amount") or 0) or None,
                datos={"stripe_refund_id": objeto.get("id")},
                proveedor_evento_id=evento_id or None,
            )
        elif tipo == "charge.dispute.created":
            pago.estado = "DISPUTADO"
            ServicioPagos._registrar(
                pago,
                tipo,
                datos={"dispute_id": objeto.get("id")},
                proveedor_evento_id=evento_id or None,
            )
        else:
            ServicioPagos._registrar(
                pago,
                f"WEBHOOK_{tipo or 'DESCONOCIDO'}",
                datos={"ignorado": True},
                proveedor_evento_id=evento_id or None,
            )
        pago.actualizado_en = ahora_utc()
        db.session.commit()
        return {"recibido": True, "tipo": tipo}

    @staticmethod
    def sincronizar_citas_existentes(citas, actor_id):
        resultado = {"procesadas": 0, "creadas_o_actualizadas": 0, "errores": []}
        for cita in citas or []:
            resultado["procesadas"] += 1
            try:
                pago = ServicioPagos.sincronizar_desde_cita(cita, actor_id)
                if pago:
                    resultado["creadas_o_actualizadas"] += 1
            except (ErrorDominio, ValueError, TypeError) as error:
                db.session.rollback()
                resultado["errores"].append({
                    "cita_id": str(cita.get("id", "desconocida")) if isinstance(cita, dict) else "desconocida",
                    "mensaje": getattr(error, "mensaje", str(error)),
                })
        return resultado

    @staticmethod
    def listar(usuario_id, rol, estado=None):
        consulta = Pago.query
        if rol == "PACIENTE":
            consulta = consulta.filter(Pago.paciente_id == int(usuario_id))
        elif rol == "PSICOLOGO":
            consulta = consulta.filter(Pago.psicologo_id == int(usuario_id))
        if estado:
            consulta = consulta.filter(Pago.estado == str(estado).upper())
        return consulta.order_by(Pago.creado_en.desc()).all()

    @staticmethod
    def obtener_por_cita(cita_id):
        cita_uuid = ServicioPagos._uuid(cita_id, "cita_id")
        return Pago.query.filter_by(cita_id=cita_uuid).first()

    @staticmethod
    def estado_interno_por_cita(cita_id):
        pago = ServicioPagos.obtener_por_cita(cita_id)
        if not pago:
            return {
                "cita_id": str(cita_id),
                "pago_encontrado": False,
                "pagado": False,
                "estado": None,
            }
        pagado = pago.estado in {"PAGADO", "REEMBOLSO_PARCIAL"}
        return {
            "cita_id": str(pago.cita_id),
            "pago_encontrado": True,
            "pagado": pagado,
            "estado": pago.estado,
            "monto_centavos": pago.monto_centavos,
            "moneda": pago.moneda,
        }

    @staticmethod
    def listar_tarifas(solo_activas=False):
        consulta = Tarifa.query
        if solo_activas:
            consulta = consulta.filter(Tarifa.activa.is_(True))
        return consulta.order_by(Tarifa.activa.desc(), Tarifa.creado_en.desc()).all()

    @staticmethod
    def crear_tarifa(datos, creado_por):
        psicologo_id = datos.get("psicologo_id")
        modalidad = datos.get("modalidad", "TODAS").upper()
        moneda = datos.get("moneda", "USD").upper()
        existentes = Tarifa.query.filter_by(
            psicologo_id=psicologo_id,
            modalidad=modalidad,
            activa=True,
        ).all()
        for tarifa in existentes:
            tarifa.activa = False
            tarifa.actualizado_en = ahora_utc()
        tarifa = Tarifa(
            psicologo_id=psicologo_id,
            modalidad=modalidad,
            monto_centavos=int(datos["monto_centavos"]),
            moneda=moneda,
            activa=True,
            creado_por=int(creado_por),
        )
        db.session.add(tarifa)
        db.session.commit()
        return tarifa

    @staticmethod
    def desactivar_tarifa(tarifa_id):
        tarifa = Tarifa.query.filter_by(id=ServicioPagos._uuid(tarifa_id, "tarifa_id")).first()
        if not tarifa:
            raise ErrorDominio("La tarifa no existe.", 404, "tarifa_no_encontrada")
        tarifa.activa = False
        tarifa.actualizado_en = ahora_utc()
        db.session.commit()
        return tarifa

    @staticmethod
    def serializar_tarifa(tarifa):
        return {
            "id": str(tarifa.id),
            "psicologo_id": tarifa.psicologo_id,
            "modalidad": tarifa.modalidad,
            "monto_centavos": tarifa.monto_centavos,
            "monto": float(Decimal(tarifa.monto_centavos) / Decimal(100)),
            "moneda": tarifa.moneda,
            "activa": tarifa.activa,
            "creado_por": tarifa.creado_por,
            "creado_en": tarifa.creado_en.isoformat() if tarifa.creado_en else None,
        }

    @staticmethod
    def serializar(pago, rol="PACIENTE", incluir_historial=False):
        ahora = ahora_utc()
        expira = asegurar_utc(pago.checkout_expira_en)
        checkout_vigente = bool(
            pago.checkout_url
            and pago.estado == "CHECKOUT_ABIERTO"
            and expira
            and expira > ahora
        )
        datos = {
            "id": str(pago.id),
            "cita_id": str(pago.cita_id),
            "paciente_id": pago.paciente_id,
            "psicologo_id": pago.psicologo_id,
            "monto_centavos": pago.monto_centavos,
            "monto": float(Decimal(pago.monto_centavos) / Decimal(100)),
            "moneda": pago.moneda,
            "estado": pago.estado,
            "proveedor": pago.proveedor,
            "modalidad": pago.modalidad,
            "fecha_hora_inicio": pago.fecha_hora_inicio.isoformat() if pago.fecha_hora_inicio else None,
            "fecha_hora_fin": pago.fecha_hora_fin.isoformat() if pago.fecha_hora_fin else None,
            "reembolsado_centavos": pago.reembolsado_centavos,
            "saldo_reembolsable_centavos": pago.saldo_reembolsable_centavos,
            "pagado_en": pago.pagado_en.isoformat() if pago.pagado_en else None,
            "comprobante_url": pago.comprobante_url if rol in {"PACIENTE", "ADMIN"} else None,
            "checkout_url": pago.checkout_url if rol == "PACIENTE" and checkout_vigente else None,
            "checkout_expira_en": expira.isoformat() if checkout_vigente else None,
            "puede_pagar": rol == "PACIENTE" and pago.estado in ESTADOS_CHECKOUT and asegurar_utc(pago.fecha_hora_inicio) > ahora,
            "puede_reembolsar": rol == "ADMIN" and pago.saldo_reembolsable_centavos > 0 and pago.estado in ESTADOS_PAGADOS,
            "ultimo_error": pago.ultimo_error,
            "creado_en": pago.creado_en.isoformat() if pago.creado_en else None,
            "actualizado_en": pago.actualizado_en.isoformat() if pago.actualizado_en else None,
        }
        if rol == "ADMIN":
            datos.update(
                {
                    "stripe_checkout_session_id": pago.stripe_checkout_session_id,
                    "stripe_payment_intent_id": pago.stripe_payment_intent_id,
                }
            )
        if incluir_historial:
            datos["transacciones"] = [
                {
                    "id": str(item.id),
                    "tipo": item.tipo,
                    "estado": item.estado,
                    "monto_centavos": item.monto_centavos,
                    "datos": item.datos or {},
                    "registrado_en": item.registrado_en.isoformat() if item.registrado_en else None,
                }
                for item in sorted(pago.transacciones, key=lambda item: item.registrado_en)
            ]
            datos["reembolsos"] = [
                {
                    "id": str(item.id),
                    "monto_centavos": item.monto_centavos,
                    "razon": item.razon,
                    "nota": item.nota,
                    "estado": item.estado,
                    "creado_en": item.creado_en.isoformat() if item.creado_en else None,
                }
                for item in sorted(pago.reembolsos, key=lambda item: item.creado_en)
            ]
        return datos
