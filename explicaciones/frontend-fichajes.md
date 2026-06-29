# Fichajes.jsx — Explicación Didáctica

## ¿Qué hace este componente?

`Fichajes.jsx` es la interfaz de **control horario**. Permite al usuario ver su historial de entradas/salidas y registrar la salida cuando termina su jornada.

La entrada se registra automáticamente al iniciar sesión (en el backend, en el router `auth/login`).

---

## Estados del componente

```javascript
const [fichajes, setFichajes] = useState([])   // Historial completo
const [abierto, setAbierto] = useState(null)    // Fichaje actual (sin salida)
```

- `fichajes`: array con todo el historial del usuario.
- `abierto`: el fichaje que no tiene `hora_salida` (está trabajando actualmente).

---

## Carga de datos con Promise.allSettled

```javascript
const [resFichajes, resActual] = await Promise.allSettled([
  api.get("/fichajes"),
  api.get("/fichajes/actual"),
])
```

Usa `Promise.allSettled` en lugar de `Promise.all` porque una de las peticiones puede fallar esperadamente: `GET /fichajes/actual` devuelve 404 si no hay fichaje abierto. `allSettled` permite manejar cada respuesta individualmente sin que un error bloquee la otra.

- Si `resActual` falla, `setAbierto(null)`.
- Si `resFichajes` falla, simplemente no se actualiza el estado.

---

## Interfaz de usuario

### Estado abierto
Si hay fichaje abierto, se muestra:
- "Abierto desde: HH:MM:SS" con la hora formateada
- Botón rojo "Registrar salida" que llama a `POST /fichajes/salida`

### Tabla de historial
Columnas: ID, Entrada, Salida, Duración.

La duración se calcula en el frontend:
```javascript
const duracion = salida
  ? Math.round((salida - entrada) / 60000) + " min"
  : "—"
```
Resta las fechas (en milisegundos), divide por 60000 (ms → minutos) y redondea.

---

## Flujo completo

1. **Login** → el backend registra entrada automáticamente
2. **Usuario ve el panel** → el frontend detecta el fichaje abierto
3. **Usuario hace clic en "Registrar salida"** → se envía `POST /fichajes/salida`
4. **Se recarga la vista** → el fichaje aparece cerrado en el historial

---

## Nota sobre useCallback

```javascript
const fetchData = useCallback(async () => { ... }, [])
```

Se usa `useCallback` para memorizar la función. La función `fetchData` se pasa al `useEffect` y también se llama desde `ficharSalida`. Sin `useCallback`, la función se recrearía en cada render, causando potencialmente bucles infinitos en el `useEffect`.
