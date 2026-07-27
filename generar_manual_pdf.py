# -*- coding: utf-8 -*-
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        if self._pageNumber == 1:
            # Portada: Dibujar fondo decorativo o logo simple
            self.saveState()
            primary_color = colors.HexColor("#1A365D")
            self.setFillColor(primary_color)
            self.rect(0, 0, 30, 792, fill=True, stroke=False) # Barra decorativa izquierda
            self.restoreState()
            return

        self.saveState()
        primary_color = colors.HexColor("#1A365D")
        accent_color = colors.HexColor("#718096")
        border_color = colors.HexColor("#E2E8F0")

        # Encabezado (Header)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(primary_color)
        self.drawString(54, 745, "PSICOCONECTA - MANUAL DE USUARIO")
        self.setFont("Helvetica-Oblique", 8)
        self.setFillColor(accent_color)
        self.drawRightString(558, 745, "Salud Mental Integradora e IoT")
        
        # Línea divisoria superior
        self.setStrokeColor(border_color)
        self.setLineWidth(0.75)
        self.line(54, 737, 558, 737)

        # Línea divisoria inferior
        self.line(54, 55, 558, 55)

        # Pie de página (Footer)
        self.setFont("Helvetica", 8)
        self.setFillColor(accent_color)
        self.drawString(54, 40, "Confidencialidad Médica - Todos los Derechos Reservados 2026")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 40, page_str)
        self.restoreState()

def construir_pdf(filename="manual_usuario_psicoconecta_v2.pdf"):
    # Margen de 0.75 pulgadas (54 pt) en los costados y 72 pt arriba/abajo
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Colores del sistema PsicoConecta
    primary = colors.HexColor("#1A365D")   # Azul marino
    secondary = colors.HexColor("#2B6CB0") # Azul intermedio
    text_color = colors.HexColor("#2D3748")# Carbón
    light_bg = colors.HexColor("#F7FAFC")  # Gris muy claro
    border_col = colors.HexColor("#E2E8F0")# Gris borde

    # Estilos de texto personalizados
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=primary,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=16,
        leading=22,
        textColor=secondary,
        spaceAfter=40
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary,
        spaceBefore=20,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=secondary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=text_color,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#4A5568")
    )

    story = []

    # ==================== PORTADA ====================
    story.append(Spacer(1, 100))
    story.append(Paragraph("PsicoConecta", title_style))
    story.append(Paragraph("Manual Integral del Usuario y Operador", subtitle_style))
    story.append(Spacer(1, 40))
    
    # Caja de metadatos de portada
    metadata_data = [
        [Paragraph("<b>Documento:</b> Manual Técnico y Operativo", body_style)],
        [Paragraph("<b>Versión:</b> 2.0 (Cumplimiento de Arquitectura)", body_style)],
        [Paragraph("<b>Fecha:</b> Julio 2026", body_style)],
        [Paragraph("<b>Autor:</b> Equipo de Desarrollo de PsicoConecta", body_style)],
        [Paragraph("<b>Plataforma:</b> Web + IoT (Sensores en tiempo real)", body_style)]
    ]
    meta_table = Table(metadata_data, colWidths=[400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('LINELEFT', (0,0), (0,-1), 4, secondary),
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 120))
    story.append(Paragraph("<i>Este manual contiene instrucciones para el uso del Portal de Pacientes, la Agenda del Psicólogo, los procesos de Pago en Línea, las Teleconsultas y la sincronización con el hardware vestible (ESP32).</i>", body_style))
    story.append(PageBreak())

    # ==================== CAPÍTULO 1 ====================
    story.append(Paragraph("Capítulo 1: Introducción a PsicoConecta", h1_style))
    story.append(Paragraph(
        "PsicoConecta es una plataforma integral de salud mental diseñada para enlazar la terapia psicológica tradicional con "
        "las tecnologías modernas de Internet de las Cosas (IoT) y analítica inteligente. A diferencia de otros portales, "
        "PsicoConecta permite monitorear de forma pasiva y segura los signos fisiológicos del paciente durante las sesiones de consulta, "
        "brindando al terapeuta métricas objetivas de su estado emocional en tiempo real.", body_style
    ))
    story.append(Paragraph(
        "El sistema consta de 5 módulos principales unificados bajo una arquitectura de microservicios limpia y eficiente:", body_style
    ))
    
    # Estilos de celdas de tablas
    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCellStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=text_color
    )

    modules_data = [
        [
            Paragraph("Módulo", table_header_style),
            Paragraph("Descripción Operativa", table_header_style),
            Paragraph("Tecnología Principal", table_header_style)
        ],
        [
            Paragraph("Módulo 1: Portal y Experiencia", table_cell_style),
            Paragraph("Acceso principal del usuario, visualizaciones de telemetría y perfiles.", table_cell_style),
            Paragraph("React, Nginx, Tailwind", table_cell_style)
        ],
        [
            Paragraph("Módulo 2: Gestión de Clínicas", table_cell_style),
            Paragraph("Registro y autenticación segura de profesionales y pacientes.", table_cell_style),
            Paragraph("Flask, SQLAlchemy, SQLite/Postgres", table_cell_style)
        ],
        [
            Paragraph("Módulo 3: Programación de Citas", table_cell_style),
            Paragraph("Reserva de horarios, agendas y control de disponibilidad.", table_cell_style),
            Paragraph("Flask, SQLAlchemy", table_cell_style)
        ],
        [
            Paragraph("Módulo 4: Teleconsulta y Pagos", table_cell_style),
            Paragraph("Videollamadas integradas y pagos seguros por Stripe.", table_cell_style),
            Paragraph("Zoom API SDK, Stripe API", table_cell_style)
        ],
        [
            Paragraph("Módulo 5: Servicios Inteligentes e IoT", table_cell_style),
            Paragraph("Procesamiento de datos fisiológicos (ESP32) y persistencia en la nube.", table_cell_style),
            Paragraph("WebSockets, AWS DynamoDB, Python", table_cell_style)
        ]
    ]
    t_modules = Table(modules_data, colWidths=[130, 240, 130])
    t_modules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_col),
        ('BACKGROUND', (0,1), (-1,-1), light_bg),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_modules)
    story.append(Spacer(1, 15))

    # ==================== CAPÍTULO 2 ====================
    story.append(Paragraph("Capítulo 2: Registro, Inicio de Sesión y Perfiles", h1_style))
    story.append(Paragraph(
        "El acceso a la plataforma está regulado según roles claros (Pacientes, Psicólogos y Administradores). "
        "Toda la información es cifrada y protegida para asegurar el cumplimiento del secreto médico y las leyes de privacidad de datos.", body_style
    ))
    
    story.append(Paragraph("2.1 Creación de Cuenta (Pacientes)", h2_style))
    story.append(Paragraph("• Ingrese al portal principal y presione <b>Registrarse</b>.", bullet_style))
    story.append(Paragraph("• Rellene los campos obligatorios: Nombre completo, Correo electrónico, Contraseña y Cédula/Identificación.", bullet_style))
    story.append(Paragraph("• Confirme su correo para activar la cuenta y poder reservar citas.", bullet_style))
    
    story.append(Paragraph("2.2 Acceso al Portal", h2_style))
    story.append(Paragraph(
        "Para iniciar sesión, introduzca sus credenciales autorizadas en la pantalla de ingreso. PsicoConecta también soporta "
        "autenticación simplificada a través de Google. Si es psicólogo, su cuenta deberá ser pre-aprobada por el administrador "
        "de la clínica antes de habilitar su panel.", body_style
    ))
    
    # Caja de advertencia (Callout)
    warning_data = [[
        Paragraph("<b>⚠️ NOTA DE SEGURIDAD:</b> No comparta sus credenciales con terceros. Si sospecha que su cuenta ha sido vulnerada, "
                  "utilice la opción 'Restablecer contraseña' inmediatamente desde la interfaz de ingreso.", callout_style)
    ]]
    t_warn = Table(warning_data, colWidths=[500])
    t_warn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF5F5")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FEB2B2")),
    ]))
    story.append(t_warn)
    story.append(PageBreak())

    # ==================== CAPÍTULO 3 ====================
    story.append(Paragraph("Capítulo 3: Reserva y Programación de Citas", h1_style))
    story.append(Paragraph(
        "El Módulo de Citas permite una coordinación fluida entre la agenda del psicólogo y la disponibilidad del paciente. "
        "Los psicólogos definen sus horarios disponibles y los pacientes pueden agendar citas de forma interactiva.", body_style
    ))
    
    story.append(Paragraph("3.1 Proceso de Agendamiento", h2_style))
    story.append(Paragraph("1. Inicie sesión como <b>Paciente</b>.", bullet_style))
    story.append(Paragraph("2. Vaya a la sección <b>Agendar Cita</b>.", bullet_style))
    story.append(Paragraph("3. Seleccione el psicólogo de su preferencia y vea los horarios disponibles en el calendario.", bullet_style))
    story.append(Paragraph("4. Seleccione un bloque libre y haga clic en <b>Confirmar Horario</b>.", bullet_style))
    story.append(Paragraph("5. El sistema redirigirá al módulo de pagos para garantizar la reserva del turno.", bullet_style))

    story.append(Paragraph("3.2 Gestión de Disponibilidad (Para Psicólogos)", h2_style))
    story.append(Paragraph(
        "El psicólogo puede definir su disponibilidad semanal ingresando a su Panel de Control en la pestaña <b>Configuración de Agenda</b>. "
        "Aquí puede bloquear días festivos, vacaciones o modificar horas de atención. "
        "Las citas agendadas aparecerán automáticamente en su panel diario junto con el enlace a la sala de teleconsulta.", body_style
    ))
    story.append(Spacer(1, 10))

    # ==================== CAPÍTULO 4 ====================
    story.append(Paragraph("Capítulo 4: Pagos y Teleconsultas Virtuales", h1_style))
    story.append(Paragraph(
        "El Módulo 4 integra transacciones monetarias y la infraestructura de videollamadas para asegurar una experiencia de telemedicina integral.", body_style
    ))
    
    story.append(Paragraph("4.1 Pasarela de Pagos (Stripe)", h2_style))
    story.append(Paragraph(
        "Para validar la reserva, el paciente debe realizar el pago correspondiente usando una tarjeta de crédito o débito válida. "
        "PsicoConecta está integrado con <b>Stripe</b>, garantizando la encriptación de datos bajo estándares PCI-DSS. "
        "Una vez realizado el pago, recibirá una confirmación por correo electrónico y el estado de la cita cambiará a 'Pagada'.", body_style
    ))
    
    story.append(Paragraph("4.2 Acceso a la Teleconsulta (Zoom)", h2_style))
    story.append(Paragraph(
        "En la fecha y hora acordadas, ambos usuarios (psicólogo y paciente) deben presionar el botón <b>Ingresar a la Sesión</b> "
        "desde sus respectivos paneles. El sistema generará dinámicamente un enlace de videoconferencia seguro a través de Zoom "
        "e iniciará la videollamada sin necesidad de salir del navegador.", body_style
    ))
    story.append(PageBreak())

    # ==================== CAPÍTULO 5 ====================
    story.append(Paragraph("Capítulo 5: Servicios Inteligentes e IoT (Telemetría)", h1_style))
    story.append(Paragraph(
        "El Módulo 5 representa el núcleo tecnológico innovador del proyecto. Permite conectar un hardware vestible (ESP32 con sensor de pulso cardíaco) "
        "y transmitir en tiempo real el ritmo y comportamiento fisiológico del paciente.", body_style
    ))
    
    story.append(Paragraph("5.1 Instrucciones para el Paciente (Uso de la ESP32)", h2_style))
    story.append(Paragraph("1. Coloque el sensor de pulso firmemente en su dedo índice o lóbulo de la oreja.", bullet_style))
    story.append(Paragraph("2. Encienda el dispositivo ESP32. Este se conectará automáticamente a la red Wi-Fi configurada (Hotspot: 'marinerito').", bullet_style))
    story.append(Paragraph("3. Al conectarse, la pantalla del monitor serie de la placa mostrará <i>¡Conexión establecida con el Servicio de Telemetría!</i>.", bullet_style))
    story.append(Paragraph("4. Permanezca relajado y evite movimientos bruscos durante la sesión de terapia para evitar ruidos en las lecturas.", bullet_style))

    story.append(Paragraph("5.2 Panel del Psicólogo (Visualización y Monitoreo)", h2_style))
    story.append(Paragraph(
        "Durante la teleconsulta, el psicólogo verá un gráfico interactivo en tiempo real que dibuja las pulsaciones del paciente (a 50Hz). "
        "Además, la inteligencia del sistema calcula indicadores de estrés y cambios súbitos, alertando al profesional si el paciente "
        "sufre un pico de ansiedad durante la sesión.", body_style
    ))
    
    story.append(Paragraph("5.3 Almacenamiento y Persistencia Histórica", h2_style))
    story.append(Paragraph(
        "Para no saturar el canal de tiempo real ni bloquear los servidores, los datos de la ESP32 son acumulados temporalmente en un buffer de memoria. "
        "Cada 2 segundos, un hilo secundario asíncrono realiza una inserción masiva (Batch Insert) en la tabla <b>lecturas_iot</b> "
        "de AWS DynamoDB, enriqueciendo los registros con la hora y fecha locales del sistema operativo, el ID y el nombre completo del paciente.", body_style
    ))
    story.append(Spacer(1, 10))

    # ==================== CAPÍTULO 6 ====================
    story.append(Paragraph("Capítulo 6: Solución de Problemas Comunes", h1_style))
    
    trouble_header_style = ParagraphStyle(
        'TroubleHeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.white
    )

    trouble_data = [
        [
            Paragraph("Problema", trouble_header_style),
            Paragraph("Causa Probable", trouble_header_style),
            Paragraph("Solución Recomendada", trouble_header_style)
        ],
        [
            Paragraph("La ESP32 se desconecta cíclicamente.", table_cell_style),
            Paragraph("Token inválido o falta de señal Wi-Fi.", table_cell_style),
            Paragraph("Verifique que el dispositivo tenga el token 'PsicoConectaSecureToken2026' y que el Hotspot 'marinerito' esté encendido.", table_cell_style)
        ],
        [
            Paragraph("No carga el gráfico en tiempo real.", table_cell_style),
            Paragraph("El psicólogo no tiene seleccionado al paciente correcto.", table_cell_style),
            Paragraph("Asegúrese de abrir la teleconsulta del paciente exacto en su Dashboard de Psicólogo.", table_cell_style)
        ],
        [
            Paragraph("El pago es rechazado.", table_cell_style),
            Paragraph("Fondos insuficientes o bloqueo bancario.", table_cell_style),
            Paragraph("Intente con otra tarjeta o consulte con el banco. El sistema Stripe notificará el código de error exacto.", table_cell_style)
        ],
        [
            Paragraph("No inicia la llamada de Zoom.", table_cell_style),
            Paragraph("El navegador bloqueó las ventanas emergentes o permisos de cámara.", table_cell_style),
            Paragraph("Otorgue permisos de cámara/micrófono en la barra de direcciones del navegador.", table_cell_style)
        ]
    ]
    t_trouble = Table(trouble_data, colWidths=[120, 180, 200])
    t_trouble.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#718096")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_col),
        ('BACKGROUND', (0,1), (-1,-1), light_bg),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_trouble)

    # Construir PDF usando nuestro NumberedCanvas personalizado
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    construir_pdf()
    print("PDF generado exitosamente.")
