# Modelo de datos

Descripción corta:
Este documento describe el paradigma de almacenamiento de la plataforma, que combina bases de datos relacionales y no relacionales según las necesidades específicas de cada microservicio.

## 1. Persistencia Híbrida

PsicoConecta adopta un enfoque de "Polyglot Persistence", utilizando el motor de base de datos más apropiado para el tipo de carga de trabajo.

### 1.1 Base de datos relacional (PostgreSQL)
Se utiliza para toda la información estructurada, transaccional y altamente conectada. A fin de mantener la autonomía de los microservicios, se utiliza una instancia única de PostgreSQL pero separada lógicamente mediante **Esquemas (Schemas)**.
*   **Esquema `usuarios_schema`**: Gestionado por el Servicio de Usuarios.
*   **Esquema `citas_schema`**: Gestionado por el Servicio de Citas.
*   **Esquema `teleconsulta_schema`**: Gestionado por el Servicio de Teleconsulta.
*   **Esquema `pagos_schema`**: Gestionado por el Servicio de Pagos.

Esta separación asegura que ningún servicio pueda hacer "JOINs" directos con tablas que no le pertenecen, obligando a la comunicación a través de las APIs (salvo excepciones diseñadas de solo lectura).

### 1.2 Base de datos NoSQL (DynamoDB)
Se emplea exclusivamente para el Servicio de Inteligencia e IoT. Dado el volumen, la falta de estructura predefinida y la alta velocidad requerida para ingerir lecturas biométricas continuas, DynamoDB (o un equivalente NoSQL como MongoDB) proporciona la flexibilidad necesaria para almacenar "documentos" de eventos.
