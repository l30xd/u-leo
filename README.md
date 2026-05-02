# 🎓 Sistema CRUD de Estudiantes con OTP

Aplicación FastAPI con autenticación OTP vía Gmail y CRUD de estudiantes.

## 🚀 Inicio Rápido Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (copiar de .env.example)
cp .env.example .env

# Editar .env con tus credenciales de Gmail
# EMAIL_USERNAME=tu_email@gmail.com
# EMAIL_PASSWORD=tu_contraseña_app
# EMAIL_FROM=tu_email@gmail.com

# Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Acceder a http://localhost:8000/index.html
```

## 📋 Requisitos

- Python 3.11+
- Cuenta Gmail con contraseña de aplicación ([Generar](https://myaccount.google.com/apppasswords))
- SQLite (incluido en Python)

## 🔐 Configuración de Variables de Entorno

Crear archivo `.env`:

```env
EMAIL_USERNAME=tu_email@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_FROM=tu_email@gmail.com
```

**Nota**: La contraseña debe ser la "Contraseña de Aplicación" de Gmail, no tu contraseña normal.

## 📦 Estructura del Proyecto

```
u-leo/
├── main.py                 # Aplicación FastAPI
├── database.py             # Configuración de BD
├── requirements.txt        # Dependencias
├── routes/
│   ├── auth.py            # Endpoints OTP
│   └── students.py        # CRUD Estudiantes
├── models/
│   ├── student_model.py   # Modelos Pydantic
│   └── db_model.py        # Modelos SQLAlchemy
├── controllers/
│   └── student_controller.py  # Lógica CRUD
└── frontend/
    ├── index.html         # UI CRUD
    └── index.js           # Lógica Frontend
```

## 🌐 Endpoints API

### Autenticación
- `POST /auth/request-otp` - Solicitar OTP
- `POST /auth/verify-otp` - Verificar OTP y obtener token

### Estudiantes (requiere Bearer token)
- `GET /students` - Listar estudiantes
- `POST /students` - Crear estudiante
- `GET /students/{id}` - Obtener estudiante
- `PUT /students/{id}` - Actualizar estudiante
- `DELETE /students/{id}` - Eliminar estudiante

## 🚀 Deployment en Render

Ver [DEPLOYMENT.md](../DEPLOYMENT.md) para instrucciones completas.

### Quick Steps:
1. Push a GitHub
2. Conecta en Render: [dashboard.render.com](https://dashboard.render.com)
3. New Web Service → Conectar repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Añadir variables de entorno en Environment

## 💡 Features

✅ Autenticación OTP por email
✅ Envío de correos con Gmail SMTP
✅ CRUD de estudiantes protegido
✅ Base de datos SQLite
✅ Frontend vanilla JavaScript
✅ CORS habilitado
✅ Token expiración (1 hora)
✅ OTP expiración (5 minutos)

## 🐛 Troubleshooting

**"OTP no llega al email"**
- Verificar EMAIL_USERNAME y EMAIL_PASSWORD
- Usar contraseña de aplicación (no contraseña normal)
- Verifica que el email de recepción sea correcto

**"ModuleNotFoundError"**
- Verificar que estás en el directorio correcto
- Ejecutar: `cd /path/to/u-leo && uvicorn main:app`

**"Connection refused"**
- Verificar que no hay otro proceso en puerto 8000
- `lsof -i :8000` (Linux/Mac) o `netstat -ano | findstr :8000` (Windows)

## 📝 Licencia

Este proyecto es educativo.
