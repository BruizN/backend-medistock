---
name: Historia de Usuario
about: Describe this issue template's purpose here.
title: ''
labels: enhancement
assignees: ''

---

## 📖 Historia de Usuario (API): [Nombre de la Funcionalidad]

> **Como** [Rol del Usuario (ej: Administrador, Cliente)]
> **Quiero** [Acción a realizar (ej: crear, listar, borrar)]
> **Para** [Beneficio o valor de negocio]

---

## ✅ Criterios de Aceptación (API)

### 🟢 Escenarios de Éxito (Happy Path)
1. [Nombre del Escenario 1]
   * **Dado** que [Precondición (ej: tengo token válido)]
   * **Y** envío un [METODO] a `[endpoint]` con JSON `{ "campo": "valor" }`
   * **Entonces** recibo un [Status Code (ej: 201 Created)]
   * **Y** la respuesta incluye [Datos esperados en el body]

2. [Nombre del Escenario 2]
   * **Dado** que [Precondición]
   * **Y** envío un [METODO] a `[endpoint]`
   * **Entonces** recibo un [Status Code]
   * **Y** [Resultado esperado]

3. [Nombre del Escenario 3]
   * **Dado** que [Precondición]
   * **Y** envío un [METODO] a `[endpoint]`
   * **Entonces** recibo un [Status Code]

### 🟠 Escenarios Alternativos y Errores (Edge Cases)
- [ ] [Nombre del Error/Caso Borde]:
   * Si intento [Acción que provoca el error].
   * Entonces recibo un [Status Code (ej: 409 Conflict)] ("[Mensaje de error]").

- [ ] [Restricción de Integridad/Lógica]:
   * Si intento [Acción prohibida por lógica de negocio].
   * Entonces recibo un [Status Code] ("[Mensaje de error]").

- [ ] [Permisos Insuficientes]:
   * Si un usuario '[Rol no autorizado]' intenta hacer [Acción].
   * Entonces recibo un 403 Forbidden.

---

## 🛠️ Tareas Técnicas
1. **Capa de Modelos ([Tecnología/ORM]):**
   * Definir tabla/entidad `[NombreEntidad]` y sus esquemas (DTOs/Pydantic).
   * Campos clave: `[campo1]`, `[campo2]`.

2. **Migraciones y Base de Datos:**
   * Generar revisión (ej: Alembic) y aplicar cambios.
   * [Opcional] Crear seed data.

3. **Lógica de Negocio / Controladores:**
   * Implementar endpoints: `[GET/POST/PUT/DELETE]`.
   * Validar permisos y roles.

4. **Documentación:**
   * Actualizar OpenAPI/Swagger, README o Diagramas si aplica.

---

## 🔍 Notas de Pruebas
* **Casos de prueba unitarios / de integración que validen:**
   * Respuesta correcta del endpoint (status + body).
   * Persistencia correcta en la base de datos (Create/Update/Delete).
   * Manejo de errores (validaciones de input, unicidad, FKs).
   * Validación de seguridad (Tokens/Roles).

---

> 🔧 Detalles más técnicos en [Enlace a Documentación/Wiki]
