# Esquema de base de datos

Base de datos: `gestion_empresas` (MySQL 8.0)

## Tablas

### empresa
| Columna | Tipo | Detalles |
|---|---|---|
| codigo_empresa | INT | PK, AUTO_INCREMENT |
| nombre | VARCHAR(150) | NOT NULL |
| codigo_scrum | VARCHAR(100) | Código del tablero Scrum |
| usuario_admin_dpd | INT | FK → usuario (admin DPD) |
| web | VARCHAR(255) | URL web externa |

### empresa_servicios (feature flags)
| Columna | Tipo | Detalles |
|---|---|---|
| codigo_empresa | INT | PK, FK → empresa |
| servicio | VARCHAR(50) | PK: 'scrum', 'tickets', 'docs', 'fichaje' |
| activo | BOOLEAN | DEFAULT TRUE |

### usuario
| Columna | Tipo | Detalles |
|---|---|---|
| codigo_usuario | INT | PK, AUTO_INCREMENT |
| correo | VARCHAR(150) | UNIQUE, NOT NULL |
| contrasena | VARCHAR(255) | NOT NULL (hash bcrypt) |
| nombre | VARCHAR(150) | NOT NULL |
| rol | ENUM | 'admin_total','admin_empresa','usuario' |
| codigo_empresa | INT | FK → empresa |

### tareas (Scrum/Kanban)
| Columna | Tipo | Detalles |
|---|---|---|
| codigo_tarea | INT | PK, AUTO_INCREMENT |
| titulo | VARCHAR(200) | NOT NULL |
| descripcion | TEXT | |
| asignacion | INT | FK → usuario (SET NULL on delete) |
| columna | ENUM | 'Todo','Haciendose','En revision','Done' |
| codigo_empresa | INT | FK → empresa |

### documentos (DPD/ISO)
| Columna | Tipo | Detalles |
|---|---|---|
| id_documento | INT | PK, AUTO_INCREMENT |
| nombre | VARCHAR(255) | NOT NULL |
| codigo_empresa | INT | FK → empresa |
| usuario_subio | INT | FK → usuario |
| fecha | DATE | NOT NULL |
| ruta_archivo | VARCHAR(255) | |
| tipo_documento | ENUM | 'DPD','ISO' |

### documento_permisos
| Columna | Tipo | Detalles |
|---|---|---|
| id_documento | INT | PK, FK → documentos |
| codigo_usuario | INT | PK, FK → usuario |

### tickets (incidencias)
| Columna | Tipo | Detalles |
|---|---|---|
| id_reporte | INT | PK, AUTO_INCREMENT |
| codigo_usuario | INT | FK → usuario |
| nivel_importancia | ENUM | 'Baja','Media','Alta','Critica' |
| mensaje | TEXT | NOT NULL |
| codigo_empresa | INT | FK → empresa |
| estado | ENUM | 'Pendiente','Leido','Respondido','Cerrado' |
| fecha_reporte | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### fichajes (control horario)
| Columna | Tipo | Detalles |
|---|---|---|
| id_fichaje | INT | PK, AUTO_INCREMENT |
| codigo_empresa | INT | FK → empresa |
| codigo_usuario | INT | FK → usuario |
| hora_entrada | DATETIME | NOT NULL |
| hora_salida | DATETIME | |

## Índices
- idx_usuario_empresa ON usuario(codigo_empresa)
- idx_tareas_empresa ON tareas(codigo_empresa)
- idx_tickets_empresa ON tickets(codigo_empresa)
- idx_fichajes_usuario ON fichajes(codigo_usuario)
- idx_documentos_empresa ON documentos(codigo_empresa)

## Relaciones clave
- empresa 1:N usuario (cada usuario pertenece a una empresa)
- empresa 1:N tareas, documentos, tickets, fichajes (aislamiento multi-tenant)
- usuario 1:N tareas (asignación), tickets, fichajes, documentos (subida)
- documentos N:M usuarios (vía documento_permisos)
