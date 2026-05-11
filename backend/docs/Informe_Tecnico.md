# Informe Técnico de Arquitectura - MEDISTOCK

## 1. Introducción
Este documento detalla la arquitectura de software diseñada para la nueva plataforma unificada de comercio electrónico de **MEDISTOCK**, orientada a solucionar los problemas de concurrencia, disponibilidad de stock en tiempo real y escalabilidad frente a clínicas institucionales y pacientes particulares.

## 2. Diagrama Entidad-Relación (DER)
El modelo de datos relacional (implementado en PostgreSQL) asegura integridad referencial y soporte para concurrencia.

*(Ver diagrama generado en Mermaid en el archivo `der.md` o renderizado nativamente si el lector soporta Mermaid).*
- **Users**: Gestiona la autenticación y roles de acceso.
- **Products**: El maestro de materiales, stock y precios.
- **Orders & Order Items**: Registra la trazabilidad transaccional de compras y permite asociar pagos externos.

## 3. Arquitectura de Software: Modelo 4+1 (Mapeado a C4)

El diseño se basa en el modelo **4+1 Vistas de Arquitectura**, documentado y estructurado a través del estándar **C4 Model** (ver `workspace.dsl`).

### 3.1 Vista Lógica (C4 System Context)
Representa la relación de alto nivel del sistema MEDISTOCK con sus actores externos.
- **Actores**: Clínicas (B2B) y Pacientes (B2C).
- **Sistemas Externos**: Pasarela de pagos (Webpay/MercadoPago), API de divisas (para facturación o visualización internacional) y ERPs de Clínicas que consumen el catálogo.

### 3.2 Vista de Desarrollo (C4 Containers)
Se estructuró el proyecto utilizando el patrón de **Monolito Modular**.
- **Frontend SPA (Vite/React)**: Aplicación cliente responsable de la interfaz gráfica e interacción del usuario. Desplegada en un servidor/dominio separado.
- **Backend API (FastAPI)**: Orquestador de la lógica de negocio, validaciones y acceso a datos. Expone una API RESTFul.
- **Base de Datos (PostgreSQL)**: Persistencia principal.

### 3.3 Vista de Procesos (C4 Components)
Desglosa internamente la API RESTful (FastAPI) en módulos lógicos que siguen el estándar *Layered Architecture* (Router -> Service -> Repository).
- **Auth Module**: JWT, seguridad, control de sesiones.
- **Inventory Module**: Control concurrente de stock y catálogo.
- **Orders Module**: Cesta de compras y comunicación con la pasarela de pagos externa.

### 3.4 Vista Física o de Despliegue (C4 Deployment)
El sistema es **distribuido**.
- **Nodo 1**: Servidor Cloud (Ej: AWS EC2 / Vercel) donde corre y se sirve estáticamente la Single Page Application (SPA).
- **Nodo 2**: Servidor Cloud (AWS EC2 / Render) donde se levantan los contenedores Docker del Backend (FastAPI + PostgreSQL + Volúmenes).
- **Restricción de Red**: El frontend se comunica con el backend exclusivamente vía HTTP/HTTPS sobre internet, cumpliendo el requisito IL3.2 e IL3.3.

### 3.5 Vista de Escenarios (C4 Dynamic)
El flujo principal de negocio (Compra) describe el funcionamiento orquestado:
1. El usuario visualiza productos y arma su carrito en la SPA.
2. La SPA envía una solicitud `POST /orders` a la API.
3. La API consulta a la **API de Divisas** para actualizar montos o a la **API Logística** si fuese necesario.
4. La API genera un token de transacción en la **Pasarela de Pagos Externa** (Transbank).
5. Se responde a la SPA con la URL de redirección bancaria.
6. Una vez completado el pago, Webpay notifica al backend para asentar el pago en BD.

## 4. Architectural Decision Records (ADR)
* **ADR-001: Framework Backend**. Se escoge Python + FastAPI por su alto rendimiento asíncrono, generación automática de OpenAPI (Swagger) y ecosistema robusto (SQLModel).
* **ADR-002: Despliegue Distribuido**. Se decide separar físicamente el Frontend del Backend para poder escalar las instancias HTTP estáticas de manera independiente a los cómputos de base de datos.
* **ADR-003: Docs as Code**. Se adopta Structurizr (DSL) y Mermaid para que los diagramas evolucionen junto con el código fuente en GitHub (GitHub Flow).
