# 🐍 Backend con FastAPI + PostgreSQL (Neon) + JWT

Este proyecto es un **backend en FastAPI** que implementa:

- Autenticación con **JWT** (access y refresh tokens).  
- Manejo de **usuarios, roles y marcas**.  
- Base de datos **PostgreSQL** alojada en **Neon**.  
- Despliegue en **Render** listo para producción.  

---

## 🚀 Requisitos

- **Python 3.10+**
- **PostgreSQL** (Neon u otra instancia compatible)
- **pip** o **pipenv/poetry** para manejar dependencias

---

## 📦 Instalación

1. Clonar el repositorio:

```bash
https://github.com/Jairo-18/backend-prueba-tecnica-full-stack.git
cd backend-prueba-tecnica-full-stack

2. Crear y activar entorno virtual:
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

3. Instalar dependencias:

pip install -r requirements.txt

4. Configuración:

# Clave secreta para JWT
SECRET_KEY=super-clave-ultra-segura

# Algoritmo de JWT
ALGORITHM=HS256

# Expiración del token en minutos
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Conexión a Neon PostgreSQL
DATABASE_URL='postgresql://neondb_owner:npg_FhuRnw1xX6vN@ep-damp-thunder-adta61mg-pooler.c-2.us-east-1.aws.neon.tech/pruebaTecnicaFullStack?sslmode=require&channel_binding=require'

5. Ejecución en Desarrollo:

uvicorn api.index:app --reload
http://localhost:8000/docs
