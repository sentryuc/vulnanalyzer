import json
import os
import datetime
from jinja2 import Environment, FileSystemLoader
import weasyprint


class ReportGenerator:
    def __init__(self, data):
        self.data = data
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "reports",
            "templates",
        )
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate_html_report(self, output_file):
        """Genera un reporte en formato HTML"""
        template = self.env.get_template("report_template.html")

        # Preparar datos para la plantilla
        context = {
            "title": "Reporte de Análisis de Vulnerabilidades",
            "timestamp": self.timestamp,
            "data": self.data,
            "summary": self._generate_summary(),
        }

        # Renderizar plantilla
        html_content = template.render(**context)

        # Guardar archivo HTML
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def generate_pdf_report(self, output_file):
        """Genera un reporte en formato PDF"""
        # Primero generamos el HTML
        html_file = output_file.replace(".pdf", ".html")
        self.generate_html_report(html_file)

        # Convertir HTML a PDF
        html = weasyprint.HTML(filename=html_file)
        html.write_pdf(output_file)

        # Opcional: eliminar el archivo HTML temporal
        os.remove(html_file)

    def generate_json_report(self, output_file):
        """Genera un reporte en formato JSON"""
        report_data = {
            "title": "Reporte de Análisis de Vulnerabilidades",
            "timestamp": self.timestamp,
            "summary": self._generate_summary(),
            "data": self.data,
        }

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=4)

    def _generate_summary(self):
        """Genera un resumen de los hallazgos"""
        summary = {
            "total_hosts": 0,
            "total_vulnerabilities": 0,
            "severity_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            "vulnerability_types": {},
        }

        # Procesar resultados de escaneo
        if "scan_results" in self.data:
            scan_results = self.data["scan_results"]
            summary["total_hosts"] = len(scan_results)

            for host, host_data in scan_results.items():
                # Contar vulnerabilidades del host
                host_vulns = host_data.get("vulnerabilities", [])
                summary["total_vulnerabilities"] += len(host_vulns)

                # Contar por severidad
                for vuln in host_vulns:
                    severity = vuln.get("severity", "info").lower()
                    summary["severity_counts"][severity] += 1

                    # Contar por tipo
                    vuln_type = vuln.get("type", "unknown")
                    if vuln_type not in summary["vulnerability_types"]:
                        summary["vulnerability_types"][vuln_type] = 0
                    summary["vulnerability_types"][vuln_type] += 1

        # Procesar resultados de OWASP
        if "owasp_results" in self.data:
            owasp_results = self.data["owasp_results"]
            owasp_vulns = owasp_results.get("vulnerabilities", [])

            summary["total_vulnerabilities"] += len(owasp_vulns)

            for vuln in owasp_vulns:
                severity = vuln.get("severity", "info").lower()
                summary["severity_counts"][severity] += 1

                vuln_type = vuln.get("type", "unknown")
                if vuln_type not in summary["vulnerability_types"]:
                    summary["vulnerability_types"][vuln_type] = 0
                summary["vulnerability_types"][vuln_type] += 1

        # Procesar resultados de explotación
        if "exploit_results" in self.data:
            exploit_results = self.data["exploit_results"]

            for host, exploits in exploit_results.items():
                for exploit in exploits:
                    if exploit.get("success", False):
                        # Cada explotación exitosa se considera una vulnerabilidad crítica
                        summary["total_vulnerabilities"] += 1
                        summary["severity_counts"]["critical"] += 1

                        exploit_name = exploit.get("exploit", "unknown")
                        if exploit_name not in summary["vulnerability_types"]:
                            summary["vulnerability_types"][exploit_name] = 0
                        summary["vulnerability_types"][exploit_name] += 1

        return summary
