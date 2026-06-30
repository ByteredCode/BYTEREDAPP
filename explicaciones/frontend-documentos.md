# Componentes de Documentos DPD/ISO — Explicación Didáctica

## Visión general

Dos componentes trabajan juntos para gestionar documentos según normativa DPD e ISO:

- **DocumentosAdmin.jsx**: panel principal con subida, listado, descarga y eliminación.
- **PermisosDoc.jsx**: modal para gestionar quién puede ver cada documento.

Ambos dependen de la API `/documentos` del backend.

---

## 1. `DocumentosAdmin.jsx` — Panel de documentos

### Estado y carga de datos
```javascript
const [docs, setDocs] = useState([])        // Lista de documentos
const [mostrarSubida, setMostrarSubida]     // Modal de subida
const [archivo, setArchivo]                 // Archivo seleccionado
const [tipoDoc, setTipoDoc]                 // DPD o ISO
const [permisoDoc, setPermisoDoc]           // Documento seleccionado para permisos
```
`fetchDocs()` obtiene la lista vía `GET /documentos`. Se ejecuta al montar y tras cada operación (subir, eliminar, cambiar permisos).

### Subida de documentos
```javascript
const fd = new FormData()
fd.append("archivo", archivo)
if (tipoDoc) fd.append("tipo_documento", tipoDoc)
await api.post("/documentos", fd, {
  headers: { "Content-Type": "multipart/form-data" }
})
```
Usa `FormData` para enviar el archivo binario. Es importante **no establecer** `Content-Type` manualmente: Axios lo hace automáticamente con el boundary correcto para multipart.

### Descarga
```javascript
const res = await api.get(`/documentos/${id}/descargar`, { responseType: "blob" })
const url = URL.createObjectURL(res.data)
const a = document.createElement("a")
a.href = url
a.click()
URL.revokeObjectURL(url)
```
Crea un blob URL temporal, genera un clic en un enlace invisible, y libera la memoria. Es la forma estándar de forzar descargas en el cliente.

### Eliminación
Con confirmación del usuario antes de llamar a `DELETE /documentos/{id}`.

### Tabla de documentos
Muestra nombre, tipo (DPD/ISO/—), ID del usuario que subió, fecha y acciones (Descargar, Permisos, Eliminar).

### Modal de subida
Formulario simple con selector de archivo y selector de tipo (DPD/ISO). Se cierra al hacer clic fuera del modal o al cancelar.

---

## 2. `PermisosDoc.jsx` — Gestión de permisos

Modal que se abre al hacer clic en "Permisos" sobre un documento.

### Funcionalidad
- **Lista permisos actuales**: tabla con IDs de usuario que tienen acceso.
- **Añadir permiso**: input numérico + botón. Llama a `POST /documentos/{id}/permisos`.
- **Quitar permiso**: botón rojo por cada fila. Llama a `DELETE /documentos/{id}/permisos/{userId}`.

### Props
```javascript
{ doc, onClose, onUpdated }
```
- `doc`: el documento seleccionado.
- `onClose`: cierra el modal.
- `onUpdated`: recarga la lista de documentos (por si cambian los permisos visibles).

---

## Relación entre componentes

```
DocumentosAdmin
  ├── Modal de subida (formulario)
  ├── Tabla de documentos
  │     ├── Botón Descargar
  │     ├── Botón Permisos → abre PermisosDoc
  │     └── Botón Eliminar
  └── PermisosDoc (modal independiente)
```

DocumentosAdmin mantiene el estado `permisoDoc`. Cuando se hace clic en "Permisos", se asigna el documento a esa variable y se renderiza condicionalmente `<PermisosDoc>`. Al cerrar, se limpia y se recarga la lista.

---

## Sistema de permisos (backend)

El backend implementa una lógica interesante:
- **Admins** (`admin_total` o `admin_empresa`): ven todos los documentos de la empresa.
- **Usuarios normales**: solo ven los documentos que ellos subieron + aquellos para los que tienen permiso explícito en `documento_permisos`.

Esto permite un control granular sin necesidad de roles complejos.
