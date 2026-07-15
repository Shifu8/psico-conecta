class ErrorDominio(Exception):
    def __init__(self, mensaje, codigo=400, error="solicitud_invalida", detalles=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.error = error
        self.detalles = detalles
