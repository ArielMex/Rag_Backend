create extension if not exists "uuid-ossp";

create or replace function actualiza_updated_at()
returns trigger as $$
begin
  new.updated_at = current_timestamp;
  return new;
end;
$$ language plpgsql;

create table usuarios (
    id varchar(255) primary key,
    nombre varchar(100) not null,
    email varchar(150) not null unique,
    password_hash varchar(255) not null,
    rol varchar(50) not null,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp
);

create trigger tg_usuarios_updated_at
before update on usuarios
for each row execute function actualiza_updated_at();

create table salas_estudio (
    id varchar(255) primary key,
    nombre_sala varchar(100) not null,
    codigo_acceso varchar(50) not null unique,
    created_at timestamp default current_timestamp
);

create table usuarios_salas (
    usuario_id varchar(255) references usuarios(id) on delete cascade,
    sala_id varchar(255) references salas_estudio(id) on delete cascade,
    fecha_ingreso timestamp default current_timestamp,
    primary key (usuario_id, sala_id)
);

create table documentos (
    id varchar(255) primary key,
    usuario_id varchar(255) references usuarios(id) on delete set null,
    sala_id varchar(255) references salas_estudio(id) on delete cascade,
    nombre_archivo varchar(255) not null,
    tipo_mime varchar(100) not null,
    ruta_vector_id varchar(255) not null,
    created_at timestamp default current_timestamp
);

create table metricas_estudio (
    id varchar(255) primary key,
    usuario_id varchar(255) references usuarios(id) on delete cascade,
    racha_dias int default 0,
    puntaje_ultimo_examen int default 0,
    updated_at timestamp default current_timestamp
);

create trigger tg_meticas_updated_at
before update on metricas_estudio
for each row execute function actualiza_updated_at();

create table evaluaciones (
    id varchar(255) primary key,
    documento_id varchar(255) references documentos(id) on delete cascade,
    tipo_evaluacion varchar(50) not null,
    contenido_json jsonb not null,
    created_at timestamp default current_timestamp
);