# Proyecto MEDISTOCK - API RESTful

## Descripción
La API RESTful de MEDISTOCK es el núcleo de la nueva plataforma unificada de comercio electrónico para insumos médicos y equipamiento clínico. Resuelve el problema de saturación en el canal de ventas tradicional (basado en correos y llamadas), proporcionando un catálogo en tiempo real y permitiendo que tanto pacientes particulares (B2C) como sistemas ERP de clínicas (B2B) puedan consultar stock y realizar pedidos de forma automatizada y eficiente.

## Stack Tecnológico
* **Lenguaje:** Python 3.x
* **Framework:** FastAPI
* **Base de Datos:** PostgreSQL
* **ORM:** SQLModel
* **Herramientas de Construcción:** Docker / Docker Compose

## Estructura de Carpetas
La arquitectura sigue el patrón de Monolito Modular con Separación en Capas (Layered Architecture):
* `modules/[nombre_modulo]/router`: Endpoints REST expuestos para consumo.
* `modules/[nombre_modulo]/service`: Lógica de negocio y reglas de validación.
* `modules/[nombre_modulo]/repository`: Persistencia y consultas a la base de datos (SQLModel).
* `models/`: Entidades globales y clases base compartidas (`AuditMixin`).
* `core/`: Configuraciones, dependencias, utilidades y conexión a base de datos.

## Configuración e Instalación

### Backend (Docker)
1. Clonar el repositorio.
2. Configurar el archivo `.env` en la raíz (puedes copiar el `.env.example`).
3. Ejecutar el siguiente comando para levantar la API y la Base de Datos:
   ```bash
   docker-compose up --build -d
   ```

Una vez corriendo:
* **Backend API:** Estará disponible en `http://localhost:8000`
* **Swagger UI:** Estará disponible en `http://localhost:8000/docs`

### Frontend Cliente (Local)
El cliente está construido como un proyecto independiente en la carpeta `frontend/`. Para iniciarlo:
1. Abre una nueva terminal.
2. Navega al directorio: `cd frontend`
3. Instala dependencias: `npm install`
4. Levanta el servidor de desarrollo: `npm run dev`

El frontend estará disponible en `http://localhost:5173`.

## Documentación de Arquitectura (Modelo 4+1)
Acceso a los diagramas de despliegue y organización:
* **Diagrama C4 (Despliegue):** Documentación disponible en el archivo `workspace.dsl` para renderizar en Structurizr.
* **Nota:** La API se auto-documenta mediante Swagger/OpenAPI en la ruta `/docs`.

## Pruebas de API
La API integra documentación interactiva para pruebas en tiempo real:
* **Swagger UI:** `http://localhost:8000/docs`
