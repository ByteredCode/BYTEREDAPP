# NuevoTicket.jsx — Explicación Didáctica

## ¿Qué hace este componente?

`NuevoTicket.jsx` es un **formulario público** que permite a cualquier persona (autenticada o no) enviar un ticket de soporte. Es la puerta de entrada del sistema de tickets.

---

## Flujo del componente

### 1. Estado inicial
```javascript
const [form, setForm] = useState({
  nombre_contacto: "",
  correo_contacto: "",
  asunto: "",
  nivel_importancia: "Media",
  mensaje: "",
  codigo_empresa: "",
})
```
Seis campos que capturan toda la información del ticket. Todos son opcionales excepto `mensaje` y `codigo_empresa` (validados en el backend).

### 2. Estados de UI
- `enviado`: booleano que cambia la vista a una pantalla de confirmación.
- `error`: mensaje de error para mostrar al usuario.
- `cargando`: deshabilita el botón mientras se envía.

### 3. Envío del formulario
```javascript
async function enviar(e) {
  e.preventDefault()
  // Convierte campos vacíos a null
  payload.codigo_empresa = Number(payload.codigo_empresa)
  await api.post("/tickets", payload)
  setEnviado(true)
}
```
El código de empresa se convierte a número (`Number()`). El mensaje se envía al endpoint `POST /tickets` que es público (no requiere autenticación).

### 4. Pantalla de éxito
Cuando `enviado === true`, se muestra un mensaje de confirmación y un botón para enviar otro ticket que resetea todo el formulario.

---

## Campos del formulario

| Campo | Tipo | Obligatorio | Notas |
|---|---|---|---|
| Nombre | texto | No | Para contacto |
| Correo | email | No | Para respuesta |
| Asunto | texto | No | Título del ticket |
| Importancia | select | Sí (default Media) | Baja/Media/Alta/Crítica |
| Código empresa | número | Sí | Identifica el destino |
| Mensaje | textarea | Sí | El contenido del ticket |

---

## Diseño de seguridad

- El usuario no autenticado puede enviar tickets. El backend asocia `codigo_usuario = None`.
- Si hay sesión iniciada, el interceptor de Axios añade el token JWT y el backend asocia el usuario.
- No hay validación frontend de la existencia de la empresa (el backend la valida indirectamente a través del modelo).
- No hay límite de envío (rate limiting) — esto es una posible mejora de seguridad.

---

## Nota sobre el endpoint

El componente llama a `api.post("/tickets", payload)` sin indicar que el endpoint es público. Es el router del backend quien decide si requiere autenticación o no (usa un try/except para obtener el usuario opcionalmente).
