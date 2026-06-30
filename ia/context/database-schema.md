# Esquema de base de datos

Base de datos: `gestion_empresas` (MySQL 8)

## Convenciones

- Tablas en snake_case, plural
- Clave primaria: `codigo_<tabla>` (INT AUTO_INCREMENT)
- Multi-tenant: todas las tablas de negocio tienen `company_id` (FK a `companies.codigo_empresa`)
- Soft-delete: `deleted_at` TIMESTAMP NULL
- Timestamps: `created_at` y `updated_at` con DEFAULT CURRENT_TIMESTAMP y ON UPDATE

## Tablas

### companies
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_empresa | INT PK | AUTO_INCREMENT |
| nombre | VARCHAR(255) | NOT NULL |
| web | VARCHAR(500) | NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP | NULL |

### users
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_usuario | INT PK | AUTO_INCREMENT |
| company_id | INT FK | companies.codigo_empresa |
| correo | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| nombre | VARCHAR(255) | NOT NULL |
| rol | ENUM('admin_total','admin_empresa','usuario') | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP | NULL |

### company_services
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_servicio | INT PK | AUTO_INCREMENT |
| company_id | INT FK | companies.codigo_empresa, UNIQUE |
| scrum | BOOLEAN | DEFAULT FALSE |
| tickets | BOOLEAN | DEFAULT TRUE |
| documentos | BOOLEAN | DEFAULT FALSE |
| fichajes | BOOLEAN | DEFAULT FALSE |
| redireccion | BOOLEAN | DEFAULT FALSE |
| admin | BOOLEAN | DEFAULT FALSE |

### scrum_sprints
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_sprint | INT PK | AUTO_INCREMENT |
| company_id | INT FK | companies.codigo_empresa |
| nombre | VARCHAR(255) | NOT NULL |
| fecha_inicio | DATE | NOT NULL |
| fecha_fin | DATE | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### scrum_tasks
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_tarea | INT PK | AUTO_INCREMENT |
| company_id | INT FK | companies.codigo_empresa |
| sprint_id | INT FK | scrum_sprints.codigo_sprint, NULL |
| titulo | VARCHAR(255) | NOT NULL |
| descripcion | TEXT | NULL |
| columna | ENUM('pendiente','en_progreso','completado') | DEFAULT 'pendiente' |
| orden | INT | DEFAULT 0 |
| asignado_a | INT FK | users.codigo_usuario, NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

### tickets
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_ticket | INT PK | AUTO_INCREMENT |
| company_id | INT FK | companies.codigo_empresa |
| nombre | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | NOT NULL |
| asunto | VARCHAR(500) | NOT NULL |
| mensaje | TEXT | NOT NULL |
| estado | ENUM('pendiente','respondido','cerrado') | DEFAULT 'pendiente' |
| respuesta | TEXT | NULL |
| respondido_por | INT FK | users.codigo_usuario, NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

### documentos
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_documento | INT PK | AUTO_INCREMENT |
| company_id | INT FK | companies.codigo_empresa |
| nombre_original | VARCHAR(500) | NOT NULL |
| nombre_archivo | VARCHAR(500) | NOT NULL |
| tipo | VARCHAR(100) | NOT NULL |
| tamaño | INT | NOT NULL (bytes) |
| subido_por | INT FK | users.codigo_usuario |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP | NULL |

### document_permissions
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_permiso | INT PK | AUTO_INCREMENT |
| document_id | INT FK | documentos.codigo_documento |
| user_id | INT FK | users.codigo_usuario |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### fichajes
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo_fichaje | INT PK | AUTO_INCREMENT |
| company_id | INT FK | companies.codigo_empresa |
| user_id | INT FK | users.codigo_usuario |
| entrada | TIMESTAMP | NOT NULL |
| salida | TIMESTAMP | NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### token_blocklist
| Columna | Tipo | Detalles |
|---------|------|----------|
| codigo | INT PK | AUTO_INCREMENT |
| jti | VARCHAR(36) | UNIQUE, NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
