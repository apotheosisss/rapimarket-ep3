"""Fase 5 · Digitalización de la Parte 1: arma un PDF con las fotos del trabajo a mano y su transcripción.

Ejecutar desde codigo_y_data:  python -m src.guion_pdf
"""
import base64

import markdown

from src import config as cfg
from src.documentos import a_pdf

DIR = cfg.RAIZ_PROYECTO / "guion_y_papel"
FOTOS = [
    ("07_guion_3_actos_limitaciones.jpg", "Guion detallado de presentación: Situación, Complicación, Solución y limitaciones"),
    ("01_T1_problema_audiencias_arbol.jpg", "T1 · Problema de negocio, audiencias y árbol de preguntas"),
    ("02_T2_auditoria_memo_A1_A5.jpg", "T2 · Auditoría del Memo de Marketing (A1–A5; A6 venía resuelta en el enunciado)"),
    ("03_T3_auditoria_dashboards.jpg", "T3 · Auditoría del sistema actual de dashboards"),
    ("04_T4_fortalezas_matriz.jpg", "T4 · Fortalezas y matriz impacto × esfuerzo (incluye el punto 4 de T1)"),
    ("05_T5_kpis_navegacion_ux.jpg", "T5 · Diccionario de KPIs, navegación y UX"),
    ("08b_wireframe_rotado_para_lectura.jpg", "T5 · Wireframe en papel milimetrado (rotado para lectura)"),
    ("06_T6_recomendacion_minto.jpg", "T6 · Recomendación ejecutiva (Pirámide de Minto)"),
]


def _listas(md: str) -> str:
    """Python-Markdown exige una línea en blanco antes de cada lista: se agrega donde falta."""
    import re
    out = []
    for ln in md.splitlines():
        es_lista = re.match(r"^\s*(- |\d+\. )", ln)
        if es_lista and out and out[-1].strip() and not re.match(r"^\s*(- |\d+\. )", out[-1]):
            out.append("")
        out.append(ln)
    return "\n".join(out)


def main():
    img = lambda f: "data:image/jpeg;base64," + base64.b64encode((DIR / "fotos" / f).read_bytes()).decode()
    paginas = "".join(f'<section class="foto"><h2>{t}</h2><img src="{img(f)}"></section>' for f, t in FOTOS)
    trans = markdown.markdown(_listas((DIR / "Transcripcion_Parte1.md").read_text(encoding="utf-8")), extensions=["tables"])
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guion y evidencias Parte 1</title><style>
@page {{ size:A4; margin:12mm }}
body {{ font-family:"Segoe UI",Calibri,Arial,sans-serif; color:#1F2328; font-size:9.6pt; line-height:1.45 }}
h1 {{ color:#1B3A5C; font-size:17pt; margin:0 0 3mm }} h2 {{ color:#1B3A5C; font-size:11.5pt; margin:0 0 3mm }}
.foto {{ break-after:page; text-align:center }} .foto img {{ max-width:100%; max-height:255mm; border:.6pt solid #DCE2E8 }}
.trans h1 {{ font-size:14pt }} .trans h2 {{ font-size:11pt; margin-top:5mm; border-bottom:1pt solid #1B3A5C; padding-bottom:1mm; text-align:left }}
.trans table {{ border-collapse:collapse; width:100%; font-size:8.4pt; margin:2mm 0 }}
.trans th, .trans td {{ border:.6pt solid #DCE2E8; padding:3px 5px; vertical-align:top; text-align:left }}
.trans th {{ background:#E8EEF5 }}
.port {{ break-after:page }} .port li {{ margin:1mm 0 }}
</style></head><body>
<section class="port"><h1>EP3 Parte 1 · Guion detallado y evidencias en papel</h1>
<p>ADY1104 Visualización de Datos · Grupo 11: Claudio Aro, Guillermo Cerda, Manuel Díaz · Caso RapiMarket Q3 2026.</p>
<p>Digitalización del trabajo hecho a mano en clases (fotos originales sin editar) y su transcripción. Las fotos originales también están en la carpeta <i>fotos/</i>.</p>
<ol>{''.join(f'<li>{t}</li>' for _, t in FOTOS)}<li>Transcripción completa</li></ol></section>
{paginas}<section class="trans">{trans}</section></body></html>"""
    fuente = DIR / "fuente"
    fuente.mkdir(exist_ok=True)
    h = fuente / "Guion_y_evidencias_Parte1.html"
    h.write_text(html, encoding="utf-8")
    a_pdf(h, DIR / "Guion_y_evidencias_Parte1.pdf")


if __name__ == "__main__":
    main()
