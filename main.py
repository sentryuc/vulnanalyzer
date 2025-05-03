#!/usr/bin/env python3

import argparse
import sys
import os
import json
from datetime import datetime

from core.caldera_client import CalderaClient
from core.scanner import VulnerabilityScanner
from core.exploiter import Exploiter

from config.settings import CALDERA_API_KEY, CALDERA_BASE_URL


def banner():
    print("""
    ██╗   ██╗██╗   ██╗██╗     ███╗   ██╗ █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗ 
    ██║   ██║██║   ██║██║     ████╗  ██║██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
    ██║   ██║██║   ██║██║     ██╔██╗ ██║███████║██╔██╗ ██║███████║██║   ╚████╔╝   ███╔╝ █████╗  ██████╔╝
    ╚██╗ ██╔╝██║   ██║██║     ██║╚██╗██║██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
     ╚████╔╝ ╚██████╔╝███████╗██║ ╚████║██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████╗███████╗██║  ██║
      ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝
                                                                                       v1.0
    """)
    print("Vulnerability analysis and adversary emulation framework")
    print("=" * 80)


def main():
    banner()

    parser = argparse.ArgumentParser(
        description="VulnAnalyzer - Framework de análisis de vulnerabilidades"
    )

    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Scan command #1
    scan_parser = subparsers.add_parser("scan", help="Escanear vulnerabilidades")
    scan_parser.add_argument("target", help="Objetivo a escanear (IP, rango, dominio)")
    scan_parser.add_argument(
        "--type",
        choices=["quick", "full", "stealth"],
        default="full",
        help="Tipo de escaneo (default: full)",
    )
    scan_parser.add_argument("--output", "-o", help="Archivo de salida para resultados")

    # Exploitation Command #2
    exploit_parser = subparsers.add_parser("exploit", help="Explotar vulnerabilidades")
    exploit_parser.add_argument(
        "--scan-file", help="Archivo con resultados de escaneo previo"
    )
    exploit_parser.add_argument("--target", help="Objetivo específico para explotar")
    exploit_parser.add_argument("--exploit", help="Exploit específico a utilizar")
    exploit_parser.add_argument(
        "--list", action="store_true", help="Listar exploits disponibles"
    )

    # Comando de Caldera
    caldera_parser = subparsers.add_parser("caldera", help="Interact with MITRE Calder")
    caldera_parser.add_argument(
        "--deploy", action="store_true", help="Instruction to generate an agent"
    )
    caldera_parser.add_argument(
        "--platform",
        choices=["windows", "linux", "darwin"],
        default="windows",
        help="Plataforma para el agente (default: windows)",
    )
    caldera_parser.add_argument(
        "--run", action="store_true", help="Ejecutar evaluación con Caldera"
    )
    caldera_parser.add_argument("--adversary", help="Nombre del adversario a utilizar")

    # ###################################################################
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Manejar comando de escaneo #1
    if args.command == "scan":
        print(f"[*] Iniciando escaneo de vulnerabilidades en {args.target}")
        scanner = VulnerabilityScanner(args.target, scan_type=args.type)
        results = scanner.run()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=4)
            print(f"[+] Resultados guardados en {args.output}")
        else:
            print(json.dumps(results, indent=4))

    # Manejar comando de explotación #2
    elif args.command == "exploit":
        if args.list:
            # Crear instancia temporal para listar exploits
            temp_exploiter = Exploiter({})
            exploits = temp_exploiter.list_exploits()
            print("\nExploits disponibles:")
            for category, category_exploits in exploits.items():
                print(f"\n[+] Categoría: {category}")
                for exploit in category_exploits:
                    print(
                        f"  - {exploit['name']}: {exploit['description']} (CVE: {exploit['cve']})"
                    )
            return

        if args.scan_file:
            with open(args.scan_file, "r") as f:
                scan_results = json.load(f)

            exploiter = Exploiter(scan_results)

            if args.exploit and args.target:
                print(f"[*] Ejecutando exploit {args.exploit} contra {args.target}")
                result = exploiter.run_specific_exploit(args.exploit, args.target)
                print(json.dumps(result, indent=4))
            else:
                print(
                    "[*] Ejecutando exploits coincidentes con vulnerabilidades detectadas"
                )
                results = exploiter.run_all_matching_exploits()
                print(json.dumps(results, indent=4))
        else:
            print("Error: Se requiere un archivo de escaneo previo (--scan-file)")

    # Manejar comando de Caldera
    elif args.command == "caldera":
        if not CALDERA_BASE_URL or not CALDERA_API_KEY:
            print(
                "Error: Se requiere configurar CALDERA_BASE_URL y CALDERA_API_KEY en config/settings.py"
            )
            return

        caldera = CalderaClient(CALDERA_BASE_URL, CALDERA_API_KEY)

        # Probar conexión
        connection_ok, message = caldera.test_connection()
        if not connection_ok:
            print(f"Error de conexión con Caldera: {message}")
            return

        # Despliega un comando para objetivo
        if args.deploy:
            caldera.deploy_agent()

        elif args.run:
            print("[*] Ejecutando evaluación con MITRE Caldera")
            results = caldera.run_caldera_assessment(adversary_name=args.adversary)

            if "error" in results:
                print(f"Error: {results['error']}")
            else:
                print(f"[+] Operación completada: {results['operation_id']}")
                print(f"[+] Adversario: {results['adversary']}")
                print(json.dumps(results, indent=4))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operation canceled by the user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {str(e)}")
        sys.exit(1)
