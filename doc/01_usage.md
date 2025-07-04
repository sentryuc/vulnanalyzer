# Uso de VulnAnalyzer

Esta guía explica cómo utilizar las funcionalidades principales de VulnAnalyzer.

## 1. Descubrimiento de Anfitriones

Antes de escanear vulnerabilidades, puedes descubrir qué anfitriones están activos en tu red.

**Comando:**

```bash
python3 main.py discover <rango_de_red> [opciones]
```

**Ejemplo:**

```bash
python3 main.py discover 192.168.1.0/24
```

**Salida:**
El comando mostrará una lista de las direcciones IP activas en formato JSON.

```json
{
    "active_hosts": [
        "192.168.1.1",
        "192.168.1.10",
        "192.168.1.54"
    ]
}
```

**Guardar la salida en un fichero:**

```bash
python3 main.py discover 192.168.1.0/24 -o discovered_hosts.json
```

## 2. Escaneo de Vulnerabilidades

Una vez que hayas identificado un objetivo, puedes escanearlo en busca de vulnerabilidades.

**Comando:**

```bash
python3 main.py scan <ip_o_dominio> [opciones]
```

**Ejemplo:**

```bash
python3 main.py scan 192.168.1.10
```

### Tipos de Escaneo

Puedes especificar el tipo de escaneo con la opción `--type`:

- `quick`: Un escaneo rápido de los puertos más comunes.
- `full`: Un escaneo completo de todos los puertos TCP.
- `stealth`: Un escaneo sigiloso para evitar la detección.

**Ejemplo de escaneo rápido:**

```bash
python3 main.py scan 192.168.1.10 --type quick
```

### Guardar los Resultados

Guarda los resultados del escaneo en un fichero JSON para su posterior análisis o para usarlos en la fase de explotación.

```bash
python3 main.py scan 192.168.1.10 --type quick -o scan_results.json
```
