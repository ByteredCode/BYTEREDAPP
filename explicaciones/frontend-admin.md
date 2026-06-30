# Panel de Administración — Explicación Didáctica

## Arquitectura del panel

El panel de administración sigue una estructura de layout con sidebar:

```
/admin/empresas          → Empresas.jsx
/admin/empresas/nueva    → EmpresaForm.jsx
/admin/empresas/:id      → EmpresaForm.jsx (edición)
/admin/empresas/:id/servicios  → Servicios.jsx
/admin/empresas/:id/usuarios   → EmpresaUsuarios.jsx
/admin/usuarios          → Usuarios.jsx
/admin/usuarios/nueva    → UsuarioForm.jsx
/admin/usuarios/:id      → UsuarioForm.jsx (edición)
/admin/tickets           → TicketsAdmin.jsx
/admin/documentos        → DocumentosAdmin.jsx
```

Todas las rutas están protegidas por `AdminOnlyRoute.jsx`.

---

## 1. `AdminOnlyRoute.jsx` — Guardia de protección

Componente que actúa como **ruta protegida**: solo usuarios con rol `admin_total` o `admin_empresa` pueden acceder.

- Si está cargando → muestra "Cargando..."
- Si no hay usuario → redirige a `/login`
- Si el rol no es admin → redirige a `/dashboard`
- Si es admin → renderiza los hijos (`<Outlet />`)

---

## 2. `AdminLayout.jsx` — Layout con sidebar

Muestra una barra lateral con enlaces de navegación. El enlace a "Empresas" solo es visible para `admin_total`. Los demás enlaces (Usuarios, Tickets, Documentos) son visibles para ambos tipos de admin.

Usa `<NavLink>` para resaltar la sección activa y `<Outlet />` para el contenido.

---

## 3. Empresas

### `Empresas.jsx` — Listado
- Carga `GET /admin/empresas` (solo admin_total).
- Muestra tabla con código, nombre, web (con enlace) y acciones.
- Acciones por empresa: Editar, Servicios, Usuarios — todas navegan a rutas anidadas.

### `EmpresaForm.jsx` — Crear/Editar
- Detecta si es creación o edición según el parámetro `id` en la URL.
- En edición, carga los datos existentes con `GET /admin/empresas/{id}`.
- Valida que el nombre no esté vacío antes de enviar.
- Tras guardar, navega de vuelta a `/admin/empresas`.

### `EmpresaUsuarios.jsx` — Usuarios por empresa
- Carga en paralelo los usuarios de la empresa y el nombre de la empresa.
- Muestra tabla con ID, correo, nombre, rol y acciones (Editar).
- Botón "Nuevo usuario" pasa `?empresa={id}` como query param para pre-seleccionar la empresa.

---

## 4. Usuarios

### `Usuarios.jsx` — Listado
- Si es `admin_total`, carga todos los usuarios (`GET /admin/usuarios`).
- Si es `admin_empresa`, carga solo los de su empresa (`GET /admin/empresas/{id}/usuarios`).
- Muestra tabla con ID, correo, nombre, rol, empresa.

### `UsuarioForm.jsx` — Crear/Editar
- Detecta si es creación o edición.
- **Roles disponibles**: solo "usuario" y "admin_empresa" (el rol "admin_total" no se asigna desde el panel).
- En creación, si hay query param `empresa`, lo pre-selecciona.
- Solo `admin_total` puede editar el código de empresa.
- La contraseña solo se pide en creación; en edición se omite.

---

## 5. `Servicios.jsx` — Feature flags por empresa

Muestra un toggle switch para cada servicio disponible (Scrum, Tickets, Documentación, Fichaje, Redirección).

- Al activar/desactivar, llama a `PUT /admin/empresas/{id}/servicios`.
- Actualiza el estado local optimistamente: busca el servicio en el array `prev` y cambia su estado `activo`.
- Muestra el estado actual con clase CSS (activo/inactivo).

---

## 6. `TicketsAdmin.jsx` — Gestión de tickets

- Lista todos los tickets de la empresa en una tabla.
- Al hacer clic en "Ver", abre un modal con el detalle completo del ticket.
- Dentro del modal, un `<select>` permite cambiar el estado (Pendiente → Leido → Respondido → Cerrado).
- El cambio de estado se aplica inmediatamente y se actualiza la lista.

---

## Resumen de roles

| Rol | Acceso a |
|---|---|
| **admin_total** | Todo: empresas, usuarios de todas las empresas, servicios, tickets, documentos |
| **admin_empresa** | Solo su empresa: usuarios, tickets, documentos. No puede modificar servicios ni crear/editar empresas |

Esta separación implementa el principio de **mínimo privilegio**: cada admin tiene acceso solo a lo que necesita.
