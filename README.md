# Framework VulnAnalyzer

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Descripción

Framework VulnAnalyzer es una herramienta de análisis de vulnerabilidades que integra Caldera y OpenVAS para realizar evaluaciones de seguridad automatizadas. Permite identificar y analizar vulnerabilidades en sistemas y redes de manera eficiente.

## ✨ Características

- 🔍 Análisis automatizado de vulnerabilidades
- 🔗 Integración con Caldera para operaciones de seguridad
- 🛡️ Escaneo con OpenVAS
- 📊 Generación de reportes detallados
- 🐍 Desarrollado en Python
- 🔧 Configuración flexible mediante variables de entorno

## 🚀 Instalación

### Prerrequisitos

- Python 3.10 o superior
- Nmap (para escaneos de red)
- Acceso a servidor Caldera
- Acceso a servidor OpenVAS

### Pasos de Instalación

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/sentryuc/vulnanalyzer.git
cd vulnanalyzer
```

#### 2. Crear Ambiente Virtual

Es recomendable usar un ambiente virtual para trabajar en proyectos aislados que no afecten el ambiente principal del sistema.

```bash
# Crear el ambiente virtual
python -m venv venv

# Activar el ambiente virtual
# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

#### 3. Configurar Herramientas e instalacion de requirements.txt

Ejecuta el script de configuración para preparar el ambiente de Caldera y OpenVAS:

```bash
chmod +x setup.sh
./setup.sh
```

#### 4. Instalar Nmap (si no está disponible)

Si el programa se ejecuta desde un servidor que no tenga nmap instalado:

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install nmap -y

# Fedora/CentOS/RHEL
sudo dnf install nmap -y

# Arch/Manjaro
sudo pacman -S nmap

# macOS (con Homebrew)
brew install nmap
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# Configuración de Caldera
CALDERA_BASE_URL=http://tu-servidor-caldera:8888
CALDERA_API_KEY=tu-api-key-de-caldera

# Configuración de OpenVAS (opcional)
OPENVAS_HOST=tu-servidor-openvas
OPENVAS_PORT=9392
OPENVAS_USERNAME=tu-usuario
OPENVAS_PASSWORD=tu-contraseña

# Configuración general
LOG_LEVEL=INFO
OUTPUT_DIR=./reports
```

### Obtener API Key de Caldera

1. Para ingresar a caldaera a traves del contenedor de docker

```bash
docker exec -it caldera-server /bin/bash
```

2. Obtener la credenciales de inicio ya que caldera configura una API y constraseña cada vez que inicia.

```bash
cat conf/local.yml
```

3. Usar la credencial de inicio dependiendo de lo que se desee trabajar `red` o `blue`
4. Copia la key al archivo `.env`

## 📁 Estructura del Proyecto

```
vulnanalyzer/
├── config/
├── core/
├── modules/
├── reports/
├── cli/
├── .env
├── .gitingnore
├── .docker-compose.yml
├── LICENSE
├── main.py
├── README.md
├── requirements.txt
└── setup.sh
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🔗 Enlaces Útiles

- [Documentación de Caldera](https://caldera.readthedocs.io/)
- [Documentación de OpenVAS](https://www.openvas.org/documentation/)
- [Guía de Nmap](https://nmap.org/docs.html)

## 📊 Estado del Proyecto

- ✅ Instalación y configuración básica
- ✅ Integración con Caldera
- ✅ Integración con OpenVAS
- 🔄 Generación de reportes
- 🔄 Interfaz web
- 🔄 API REST

---

**Nota**: Este proyecto está en desarrollo activo. Las funcionalidades pueden cambiar sin previo aviso.
