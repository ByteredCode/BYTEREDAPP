# Docker en BYTEREDAPP

## ¿Por qué usamos Docker?

Docker permite ejecutar aplicaciones en **contenedores**: entornos aislados y ligeros que contienen todo lo necesario para que un programa funcione.

**Analogía:** Un contenedor Docker es como una caja de herramientas autosuficiente. Dentro de la caja está MySQL 8.0 con su configuración, sus archivos de datos, y todo lo que necesita. Si mueves la caja a otro ordenador, dentro sigue funcionando igual.

---

## ¿Qué contenedor usamos?

Actualmente solo tenemos un contenedor: **MySQL 8.0**.

### ¿Por qué solo MySQL va en Docker y no el backend o frontend?

| Componente | ¿En Docker? | Motivo |
|---|---|---|
| **MySQL** | ✅ Sí | Es una dependencia externa. La BD debe ser la misma en desarrollo y producción. |
| **Backend (FastAPI)** | ❌ No | En desarrollo es más rápido ejecutarlo directamente con `uvicorn run:app` (hot reload). En producción se podría dockerizar. |
| **Frontend (React)** | ❌ No | Similar al backend: Vite tiene hot reload en desarrollo que no funcionaría bien dentro de un contenedor. |

---

## docker-compose.yml

```yaml
services:
  db:
    image: mysql:8.0
    container_name: byteredapp-db-1
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: byteredapp
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password

volumes:
  mysql_data:
```

Desglose:

### `image: mysql:8.0`
Especifica la imagen de Docker que vamos a usar. `mysql:8.0` es la imagen oficial de MySQL mantenida por Oracle. El tag `8.0` garantiza que siempre descargamos esa versión específica.

### `container_name: byteredapp-db-1`
Nombre del contenedor. Sin esto, Docker genera un nombre aleatorio. Tener un nombre fijo facilita ejecutar comandos como `docker exec byteredapp-db-1 mysql ...`.

### `environment`
Variables de entorno que MySQL usa al arrancar por primera vez:
- `MYSQL_ROOT_PASSWORD: root` — contraseña del usuario root
- `MYSQL_DATABASE: byteredapp` — base de datos que se crea automáticamente al iniciar

### `ports: "3306:3306"`
Mapea el puerto 3306 del contenedor al 3306 del host. Así podemos conectar desde nuestra máquina al MySQL del contenedor como si estuviera instalado localmente.

**Formato:** `puerto_host:puerto_contenedor`

### `volumes`
Los datos de MySQL se guardan en `/var/lib/mysql` dentro del contenedor. Si el contenedor se elimina, los datos se pierden (a menos que se use un volumen). `mysql_data` es un volumen persistente que sobrevive a la eliminación del contenedor.

### `command: --default-authentication-plugin=mysql_native_password`
MySQL 8.0 cambió el plugin de autenticación por defecto a `caching_sha2_password`. Algunos clientes (como versiones antiguas de librerías Python) no lo soportan. Esta opción fuerza el uso del plugin clásico `mysql_native_password`.

---

## ¿Cómo se usa?

### Arrancar MySQL
```bash
docker compose up -d
```
`-d` significa "detached" (modo background). MySQL arranca en segundo plano.

### Verificar que está corriendo
```bash
docker ps
```
Debe aparecer el contenedor `byteredapp-db-1` con estado `Up`.

### Conectarse a MySQL
```bash
docker exec -it byteredapp-db-1 mysql -uroot -proot byteredapp
```

### Detener MySQL (sin borrar datos)
```bash
docker compose stop
```

### Detener y borrar todo (incluyendo datos)
```bash
docker compose down -v
```
`-v` elimina también el volumen de datos. Precaución: esto borra la BD.

### Ver logs
```bash
docker compose logs -f
```

---

## ¿Qué pasa si Docker Desktop no está abierto?

Los comandos `docker` fallan. Síntomas:
```
error during connect: ... pipe docker_engine...
```

Solución: abrir Docker Desktop manualmente. En Windows:
```bash
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

Esperar a que Docker Desktop termine de cargar (icono verde en la bandeja del sistema), luego ejecutar `docker compose up -d`.

---

## ¿Por qué Docker Desktop en Windows?

Docker necesita el kernel de Linux para funcionar. En Windows, Docker Desktop crea una máquina virtual Linux (WSL2) donde ejecuta los contenedores. La experiencia es casi transparente: los comandos son los mismos que en Linux.

---

## Alternativas que NO usamos

| Alternativa | Motivo de descarte |
|---|---|
| Instalar MySQL directamente en Windows | Contamina el sistema, difícil de desinstalar, versión fija |
| Usar SQLite | Menos funciones, no soporta múltiples conexiones concurrentes bien |
| Usar un servicio cloud (AWS RDS) | Coste innecesario en desarrollo |

---

## Conclusión: ¿para qué sirve Docker aquí?

Docker nos da:
1. **Una BD limpia y controlada** — misma versión y configuración para todo el equipo
2. **Fácil de empezar** — `docker compose up -d` y ya tienes MySQL
3. **Fácil de reiniciar** — `docker compose down -v && docker compose up -d` te da una BD fresh
4. **Sin instalaciones complicadas** — no necesitas instalar MySQL en Windows
