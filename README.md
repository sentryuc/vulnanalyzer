# Framework VulnAnalyzer

## Requirements

Install the necessary requirements

```bash
pip install -r requirements.txt
```

Si el programa se corre desde un servidor que no tenga nmap se debe de instalar las dependencias

```bash
# Debian/Ubuntu
sudo apt install nmap -y

# Fedora/CentOS/RHEL
sudo dnf install nmap -y

# Arch/Manjaro
sudo pacman -S nmap
```

### Instalar caldera

* Configuracion de la API de Caldera
Ya configurado el ambiente se debe de configurar con la API correspondiente de caldera y la URL del servidor donde esta corriendo, y configurar las variables en un `.env`

```bash
CALDERA_BASE_URL=
CALDERA_API_KEY=
```
