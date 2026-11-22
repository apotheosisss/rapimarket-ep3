"""Fase 4 · Informe ejecutivo (PDF, máx. 4 páginas) y presentación Minto (PDF, 7 láminas).

Construye ambos documentos en HTML con las cifras de resultados/ y data/processed/, y los imprime a PDF
con Microsoft Edge o Google Chrome en modo headless si están instalados.

Requiere:  python -m src.pipeline  y  python -m src.auditoria
Ejecutar desde codigo_y_data:  python -m src.documentos
"""
import base64
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

from src import config as cfg

C = cfg.COL
INF = cfg.RAIZ_PROYECTO / "informes"
PRE = cfg.RAIZ_PROYECTO / "presentacion"
CAP = cfg.RAIZ_PROYECTO / "dashboard" / "capturas"

# Propuesta de inversión: asignación proporcional a la importancia de cada palanca operativa en la Tabla E
# (atraso 31 · faltantes 24 · frío 17 · reclamos 12), redondeada, más un 3 % para datos y monitoreo.
INVERSION = [
    ("Última milla en Santiago: reemplazo gradual del operador externo de Bodega Sur y ruteo de pedidos complejos",
     "Pedido atrasado (31 %)", 1.10, "Operaciones"),
    ("Control de stock en tiempo real y picking con escáner para eliminar faltantes y sustituciones",
     "Faltantes o sustituidos (24 %)", 0.85, "Operaciones / bodegas"),
    ("Cadena de frío: sensores de temperatura y cajas refrigeradas en las rutas con congelados",
     "Congelados fuera de temperatura (17 %)", 0.60, "Calidad y cadena de frío"),
    ("Mesa de soporte con respuesta a reclamos en menos de 24 horas",
     "Reclamo sin respuesta > 24 h (12 %)", 0.35, "Soporte al cliente"),
    ("Datos y monitoreo: dashboard unificado, alertas diarias y actualización de la encuesta",
     "Medición y control", 0.10, "Analítica"),
]


def b64(p: Path) -> str:
    mime = "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def miles(x):
    return f"{x:,.0f}".replace(",", ".")


def pct(x, d=1):
    return f"{x * 100:.{d}f} %".replace(".", ",")


def cifras() -> dict:
    men = pd.read_csv(cfg.DIR_PROC / "kpis_mensuales.csv").set_index("mes")
    ciu = pd.read_csv(cfg.DIR_PROC / "kpis_ciudad.csv").set_index("ciudad_bodega")
    bt = pd.read_csv(cfg.DIR_PROC / "kpis_bodega_tipo.csv")
    imp = pd.read_csv(cfg.DIR_RES / "importancia_random_forest.csv")
    mod = json.loads((cfg.DIR_RES / "modelo_fuga.json").read_text(encoding="utf-8"))
    aud = pd.read_csv(cfg.DIR_RES / "auditoria_A1_A6.csv")
    df = pd.read_csv(cfg.DIR_PROC / "pedidos_integrados.csv.gz",
                     usecols=["cliente_id", "atrasado", "recompra_30d", "n_reclamos", "reclamo_tardio", "con_reclamo",
                              "frio_roto", "con_congelados", "faltantes", "ciudad_bodega", "bodega"])
    obs = df[df["recompra_30d"].notna()]
    rec = obs.groupby("atrasado")["recompra_30d"].mean()
    rec_tard = obs[obs["con_reclamo"]].groupby(obs["reclamo_tardio"].fillna(False).astype(bool))["recompra_30d"].mean()
    stgo = df[df["ciudad_bodega"] == "Santiago"]
    sur = stgo[stgo["bodega"] == "Sur"]
    oper = imp[imp["variable"].isin(["Pedido atrasado", "Productos faltantes o sustituidos",
                                     "Congelados fuera de temperatura", "Reclamo sin respuesta > 24 h"])]["importancia_csv_pct"].sum()
    cup = float(imp.loc[imp["variable"] == "Uso de cupón de descuento", "importancia_csv_pct"].iloc[0])
    return dict(men=men, ciu=ciu, bt=bt, imp=imp, mod=mod, aud=aud, rec=rec, rec_tard=rec_tard,
                n_ped=len(df), atraso=df["atrasado"].mean(), reclamos=int(df["n_reclamos"].sum()),
                stgo_share=len(stgo) / len(df), stgo_atr=stgo["atrasado"].mean(), sur_atr=sur["atrasado"].mean(),
                sur_share_atr=sur["atrasado"].sum() / stgo["atrasado"].sum(), oper=oper, cup=cup,
                frio=df.loc[df["con_congelados"], "frio_roto"].mean(), falt=df["faltantes"].mean(),
                caida=men.loc[9, "pedidos"] / men.loc[7, "pedidos"] - 1,
                un_pedido=(df.groupby("cliente_id").size() == 1).mean())


CSS_BASE = f"""
* {{ box-sizing:border-box }} html,body {{ margin:0; background:#fff }}
body {{ font-family:"Segoe UI",Calibri,Arial,sans-serif; color:{C['tinta']} }}
.ok {{ color:{C['ok']} }} .al {{ color:{C['alerta_txt']} }} .mut {{ color:{C['gris_txt']} }}
table {{ border-collapse:collapse; width:100% }}
th,td {{ text-align:left; vertical-align:top; border-bottom:0.6pt solid {C['borde']} }}
thead th {{ background:#E8EEF5; border-bottom:1.4pt solid {C['marca']} }}
img {{ display:block; max-width:100% }}
"""


# =========================================================================== INFORME
def informe(k: dict) -> str:
    m, ci, imp, mod = k["men"], k["ciu"], k["imp"], k["mod"]
    aud = k["aud"]
    filas_aud = "".join(
        f"<tr><td><b>{r.afirmacion}</b></td><td>{r.dice_memo}</td><td><b>{r.tipo_error}</b></td>"
        f"<td>{r.recalculo_anexo}</td><td>{r.recalculo_csv}</td><td>{r.lectura_correcta}</td></tr>" for r in aud.itertuples())
    filas_inv = "".join(f"<tr><td>{a}</td><td>{b}</td><td style='text-align:right'><b>{c:.2f}</b></td><td>{d}</td></tr>".replace(f"{c:.2f}", f"{c:.2f}".replace(".", ","))
                        for a, b, c, d in INVERSION)
    fig = lambda n: b64(cfg.DIR_FIG / n)
    css = CSS_BASE + f"""
@page {{ size:A4; margin:13mm 14mm 12mm 14mm }}
body {{ font-size:9.1pt; line-height:1.42 }}
h1 {{ font-size:15pt; color:{C['marca']}; margin:0 0 2mm }}
h2 {{ font-size:11pt; color:{C['marca']}; margin:3.6mm 0 1.5mm; padding-bottom:1mm; border-bottom:1.2pt solid {C['marca']} }}
p {{ margin:0 0 1.8mm }} ul,ol {{ margin:0 0 2mm; padding-left:4.5mm }} li {{ margin:0 0 .8mm }}
th,td {{ padding:2.4px 5px; font-size:8.1pt }}
.top {{ display:flex; justify-content:space-between; font-size:8pt; color:{C['gris_txt']}; border-bottom:.6pt solid {C['borde']}; padding-bottom:1.5mm; margin-bottom:3mm }}
.titular {{ background:{C['marca']}; color:#fff; padding:4mm 5mm; border-radius:4px; margin:0 0 3mm }}
.titular .k {{ font-size:8pt; letter-spacing:.1em; text-transform:uppercase; color:#C9D6E4 }}
.titular .t {{ font-size:13.5pt; font-weight:700; line-height:1.25; margin-top:1mm }}
.args {{ display:grid; grid-template-columns:repeat(3,1fr); gap:3mm; margin:0 0 3mm }}
.arg {{ border:.8pt solid {C['borde']}; border-top:3pt solid {C['alerta']}; border-radius:4px; padding:2.5mm 3mm }}
.arg .n {{ font-size:15pt; font-weight:700; color:{C['alerta_txt']} }}
.arg p {{ font-size:8.4pt; margin:0 }}
.g2 {{ display:grid; grid-template-columns:1fr 1fr; gap:4mm; align-items:start }}
.box {{ background:#EEF3F8; border-left:3pt solid {C['marca']}; padding:2mm 3.5mm; border-radius:0 4px 4px 0; margin:1.5mm 0 2.5mm }}
.box.al {{ background:#FFF4E8; border-color:{C['alerta']} }}
figure {{ margin:1mm 0 2mm }} figcaption {{ font-size:7.6pt; color:{C['gris_txt']}; margin-top:.8mm }}
.pg {{ break-before:page }}
.aud td:nth-child(1) {{ width:5% }} .aud td:nth-child(3) {{ width:12% }}
"""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Informe ejecutivo RapiMarket Q3 2026</title><style>{css}</style></head><body>
<div class="top"><span>ADY1104 · Visualización de Datos · EP3 Parte 2 · Grupo 11: Claudio Aro, Guillermo Cerda, Manuel Díaz</span><span>Para: Comité Ejecutivo RapiMarket · noviembre 2026</span></div>
<h1>Informe ejecutivo · RapiMarket Q3 2026</h1>
<div class="titular"><div class="k">Recomendación</div>
<div class="t">Destinar los USD 3.000.000 a la operación —entrega, stock y cadena de frío— y nada a cupones: la fuga de clientes la explica la operación, no la falta de descuentos.</div></div>
<div class="args">
 <div class="arg"><div class="n">{k['oper']:.0f} %</div><p>de la capacidad del modelo de fuga viene de variables operativas (atraso, faltantes, frío, reclamos tardíos). El cupón aporta {k['cup']:.0f} %.</p></div>
 <div class="arg"><div class="n">{pct(k['rec'][False], 0)} → {pct(k['rec'][True], 0)}</div><p>cae la recompra a 30 días cuando el pedido llega atrasado. Con la misma calificación, el atraso decide si el cliente vuelve.</p></div>
 <div class="arg"><div class="n">{pct(k['caida'], 0).replace('-', '−')}</div><p>de pedidos entre julio y septiembre, mientras los reclamos por cada 100 pedidos suben de {str(round(m.loc[7, 'reclamos_100'], 1)).replace('.', ',')} a {str(round(m.loc[9, 'reclamos_100'], 1)).replace('.', ',')}.</p></div>
</div>
<h2>1. Situación, complicación y decisión</h2>
<p><b>Situación.</b> Los dashboards de cada área (D1 Marketing, D2 Operaciones, D3 Finanzas) muestran que todo va bien, y Marketing propone invertir los USD 3 M en cupones.
<b>Complicación.</b> Al recalcular con los datos, el negocio se contrae: menos pedidos cada mes, más reclamos por pedido, Santiago atrasa {pct(k['stgo_atr'])} de sus pedidos (resto del país: {pct(ci.drop('Santiago')['atrasados'].sum() / ci.drop('Santiago')['pedidos'].sum())}) y la Bodega Sur —operada por un tercero y ausente de D2— concentra {pct(k['sur_share_atr'], 0)} de los atrasos de Santiago.
<b>Decisión.</b> Aprobar antes del cierre de 2026 una inversión operativa de USD 3 M para el primer semestre de 2027.</p>
<p><b>Audiencias.</b> Principal: Comité Ejecutivo (nivel técnico medio-bajo; decide la inversión; lectura mensual). Secundaria: área de Operaciones (nivel medio-alto; uso diario con filtros y drill-down).
<b>Objetivo de comunicación:</b> persuadir con evidencia y dejar un sistema para monitorear.</p>
<h2>2. Pipeline y calidad de datos (Fase 1)</h2>
<p>Se integraron los 6 CSV del grupo ({miles(k['n_ped'])} pedidos, 78.000 clientes, 27.414 reclamos, 77.600 calificaciones, 48.103 cupones, 7 bodegas) con uniones por <i>cliente_id</i>, <i>pedido_id</i> y <i>bodega</i>.
No hay duplicados ni llaves huérfanas. Los únicos nulos están en la temperatura de llegada y corresponden a pedidos sin congelados. Los valores extremos de tiempo y monto se conservan porque son el fenómeno a medir; por eso se informan mediana y p90.
Variables derivadas: atraso (fuera de la ventana de 45 min), congelado fuera de temperatura (sobre −15 °C, corte natural en los datos), reclamo sin respuesta en 24 h y recompra a 30 días (solo pedidos con 30 días de seguimiento).</p>
<div class="box"><p><b>Nota de alcance.</b> Los CSV del grupo son una muestra distinta del Anexo oficial ({miles(k['n_ped'])} pedidos vs 180.000), sin comunas ni visitas a la app. Por eso las cifras difieren levemente; las conclusiones son las mismas con ambas fuentes, y se muestran las dos.</p></div>

<h2 class="pg">3. Auditoría del Memo de Marketing (A1–A6)</h2>
<table class="aud"><thead><tr><th>Afirm.</th><th>Dice el memo</th><th>Error</th><th>Recálculo con el Anexo</th><th>Recálculo con los CSV</th><th>Lectura correcta</th></tr></thead><tbody>{filas_aud}</tbody></table>
<div class="g2" style="margin-top:2mm">
 <figure><img src="{fig('fig_A2_pedidos_ticket.png')}"><figcaption>A2. Los pedidos mensuales caen y el ticket de productos no sube: el alza es el cargo de servicio de CLP 1.990 desde agosto.</figcaption></figure>
 <figure><img src="{fig('fig_A3_volumen_vs_tasa.png')}"><figcaption>A3. Santiago concentra volumen, pero también la mayor tasa de atraso y el único p90 sobre la meta de 60 min ({ci.loc['Santiago', 'p90_min']:.0f} min).</figcaption></figure>
</div>

<h2 class="pg">4. Paradoja de Simpson: Centro no es la peor bodega (A4)</h2>
<figure><img src="{fig('fig_A4_simpson.png')}"><figcaption>En total, Centro parece peor que Norte. Separado por tipo de pedido, Centro atrasa menos en complejos y en simples: atiende 80 % de pedidos complejos y Norte solo 20 %. Cerrar Centro trasladaría pedidos complejos a la bodega que peor los atiende. La peor es Sur (externa).</figcaption></figure>
<h2>5. Qué explica la fuga (A5, A6 y modelo)</h2>
<div class="g2">
 <figure><img src="{fig('fig_A5_recompra.png')}"><figcaption>A5. Dentro de cada grupo de calificación, la recompra cambia poco; entre a tiempo y atrasado cambia ~27 pp. La mala nota es síntoma del atraso.</figcaption></figure>
 <figure><img src="{fig('fig_RF_importancia.png')}"><figcaption>Random Forest con las 7 variables de la Tabla E (AUC {str(mod['auc_prueba'])[:4].replace('.', ',')}; Anexo 0,81). Atraso y faltantes lideran en ambas fuentes; el cupón aporta poco.</figcaption></figure>
</div>
<p><b>A6.</b> La encuesta de 4,6/5 solo llegó a clientes con segundo pedido: excluye al {pct(k['un_pedido'])} que compró una sola vez en el trimestre. La calificación de todos los pedidos promedia 3,1/5.
Además, un reclamo sin respuesta en 24 horas baja la recompra de {pct(k['rec_tard'][False], 0)} a {pct(k['rec_tard'][True], 0)}.</p>

<h2 class="pg">6. Propuesta (Pirámide de Minto)</h2>
<div class="titular" style="margin-bottom:2mm"><div class="t" style="font-size:12pt">Invertir USD 3 M en la operación, con piloto en diciembre de 2026 y despliegue en el primer semestre de 2027.</div></div>
<table><thead><tr><th>Iniciativa</th><th>Palanca (importancia Tabla E)</th><th style="text-align:right">USD M</th><th>Responsable</th></tr></thead>
<tbody>{filas_inv}<tr><td><b>Total</b></td><td>Cupones de descuento: USD 0</td><td style="text-align:right"><b>3,00</b></td><td></td></tr></tbody></table>
<p class="mut" style="font-size:7.8pt">Asignación proporcional a la importancia de cada palanca operativa en la Tabla E (31 · 24 · 17 · 12), redondeada, más 3 % para datos y monitoreo.</p>
<div class="g2">
<div><p><b>Metas al cierre del primer semestre de 2027</b></p><ul>
<li>p90 de entrega en Santiago &lt; 60 min (hoy {ci.loc['Santiago', 'p90_min']:.0f} con CSV; 78 en el Anexo).</li>
<li>Pedidos atrasados ≤ 12 % (hoy {pct(k['atraso'])}).</li>
<li>Recompra a 30 días de vuelta al 41 % del Anexo (septiembre: 33 %).</li>
<li>Reclamos ≤ 12,6 por cada 100 pedidos y 0 reclamos sin respuesta en 24 h.</li></ul></div>
<div><p><b>Plazos</b></p><ul>
<li>Diciembre 2026: aprobación y piloto en Bodega Sur (control de stock y sensores de frío).</li>
<li>Enero–marzo 2027: despliegue en Santiago y mesa de reclamos.</li>
<li>Abril–junio 2027: extensión a regiones y evaluación contra metas en el dashboard.</li></ul></div></div>
<h2>7. Dashboard para decidir y monitorear</h2>
<div class="g2"><figure><img src="{b64(CAP / '01_vista_estrategica.png')}"><figcaption>Vista estratégica (Streamlit): traduce el wireframe de la Parte 1 —4 KPIs con variación, clientes por zona, ventas vs meta, reclamos por bodega y tabla trimestral—. Un clic en una ciudad abre la vista operativa (drill-down).</figcaption></figure>
<div><ul><li><b>KPIs unificados:</b> una sola definición de clientes activos (con pedido en el período) en lugar de 412.000 / 148.000 / 61.300.</li>
<li><b>Accesibilidad WCAG 2.1:</b> paleta azul/naranja segura para daltonismo; cada estado lleva ícono y texto, no solo color; contraste ≥ 4,5:1.</li>
<li><b>Information scent:</b> títulos que concluyen y la indicación "clic para ver detalle" en cada gráfico navegable.</li>
<li><b>Progressive disclosure:</b> el Comité ve 7 cifras; el detalle por bodega, tipo y pedido queda en la vista operativa.</li></ul></div></div>
<h2>8. Limitaciones y mitigación</h2>
<ol><li><b>Datos no capturados:</b> la bodega Sur no reportaba a D2, no hay comunas ni visitas a la app en los CSV. <i>Mitigación:</i> exigir al operador de Sur el envío diario de datos como condición del contrato y replicar el desglose de la Tabla C en regiones.</li>
<li><b>Encuesta sesgada:</b> solo llega tras el segundo pedido. <i>Mitigación:</i> encuestar tras el primer pedido y al detectar abandono.</li>
<li><b>Modelo:</b> con las variables disponibles, el AUC recalculado ({str(mod['auc_prueba'])[:4].replace('.', ',')}) es menor al reportado (0,81); sirve para ordenar palancas, no para predecir clientes individuales.</li></ol>
</body></html>"""


# =========================================================================== PRESENTACIÓN
def presentacion(k: dict) -> str:
    m, ci, mod = k["men"], k["ciu"], k["mod"]
    fig = lambda n: b64(cfg.DIR_FIG / n)
    css = CSS_BASE + f"""
@page {{ size:338.67mm 190.5mm; margin:0 }}
.s {{ width:338.67mm; height:190.5mm; padding:13mm 16mm 11mm; position:relative; break-after:page; overflow:hidden }}
.s:last-child {{ break-after:auto }}
.k {{ font-size:10.5pt; letter-spacing:.12em; text-transform:uppercase; color:{C['gris_txt']}; font-weight:600 }}
h1 {{ font-size:25pt; line-height:1.15; color:{C['marca']}; margin:2mm 0 5mm }}
h1 em {{ font-style:normal; color:{C['alerta_txt']} }}
p, li {{ font-size:13pt; line-height:1.4 }}
.foot {{ position:absolute; left:16mm; right:16mm; bottom:6mm; font-size:8.5pt; color:{C['gris_txt']}; display:flex; justify-content:space-between }}
.cover {{ background:{C['marca']}; color:#fff }}
.cover h1 {{ color:#fff; font-size:31pt; margin-top:22mm }}
.cover .k {{ color:#C9D6E4 }} .cover p {{ color:#E8EEF5; font-size:14pt }}
.cover .foot {{ color:#C9D6E4 }}
.g2 {{ display:grid; grid-template-columns:1fr 1fr; gap:9mm; align-items:start }}
.g3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6mm }}
.card {{ border:.8pt solid {C['borde']}; border-top:4pt solid {C['alerta']}; border-radius:6px; padding:5mm 6mm }}
.card.az {{ border-top-color:{C['marca']} }}
.big {{ font-size:30pt; font-weight:700; color:{C['alerta_txt']}; line-height:1.05 }}
.card.az .big {{ color:{C['marca']} }}
.card p {{ font-size:11.5pt; margin:2mm 0 0 }}
.act {{ font-size:10pt; font-weight:700; color:{C['alerta_txt']}; letter-spacing:.08em; text-transform:uppercase }}
th,td {{ padding:2.2mm 3mm; font-size:11pt }}
.cap {{ font-size:10pt; color:{C['gris_txt']}; margin-top:2mm }}
.dec {{ background:#FFF4E8; border-left:5pt solid {C['alerta']}; padding:4mm 6mm; border-radius:0 6px 6px 0; font-size:14pt; font-weight:600 }}
"""
    foot = lambda n: f'<div class="foot"><span>RapiMarket · Comité Ejecutivo · Q3 2026 · Grupo 11</span><span>{n} / 7</span></div>'
    inv = "".join(f"<tr><td>{a.split(':')[0]}</td><td>{b}</td><td style='text-align:right'><b>{f'{c:.2f}'.replace('.', ',')}</b></td></tr>" for a, b, c, d in INVERSION)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Presentación ejecutiva RapiMarket</title><style>{css}</style></head><body>
<section class="s cover"><div class="k">Recomendación al Comité Ejecutivo · Inversión H1 2027</div>
<h1>Invertir los USD 3 M en la operación, no en cupones: la fuga de clientes la causa la entrega</h1>
<p>Los datos del Q3 muestran un negocio que se contrae por atrasos, faltantes y cadena de frío. El memo de Marketing leyó mal los datos.</p>
<p style="margin-top:8mm">Grupo 11: Claudio Aro, Guillermo Cerda, Manuel Díaz · ADY1104 Visualización de Datos · Duoc UC</p>
<p style="margin-top:6mm">Decisión solicitada: aprobar el plan antes del cierre de 2026 · piloto en diciembre · despliegue enero–junio 2027.</p>{foot(1)}</section>

<section class="s"><div class="k">Guion en 3 actos</div><h1>Los dashboards dicen que todo va bien; los datos dicen lo contrario</h1>
<div class="g3">
<div class="card az"><div class="act">Situación</div><p>D1, D2 y D3 muestran cifras positivas y Marketing pide los USD 3 M para cupones.</p></div>
<div class="card"><div class="act">Complicación</div><p>Los pedidos caen {pct(-k['caida'], 0)} de julio a septiembre, los reclamos por pedido suben y Santiago atrasa {pct(k['stgo_atr'], 0)} de sus pedidos. La bodega Sur ni siquiera aparece en D2.</p></div>
<div class="card az"><div class="act">Solución</div><p>Destinar los USD 3 M a operaciones: última milla, control de stock, cadena de frío y respuesta a reclamos.</p></div></div>
<p class="cap" style="margin-top:8mm">Fuente: CSV RapiMarket Q3 2026 (grupo 11) y Anexo oficial.</p>{foot(2)}</section>

<section class="s"><div class="k">Argumento 1</div><h1>La fuga es operativa: {k['oper']:.0f} % de lo que predice el abandono es la entrega; el cupón, <em>{k['cup']:.0f} %</em></h1>
<div class="g2"><div><img src="{fig('fig_RF_importancia.png')}"><p class="cap">Random Forest con las variables de la Tabla E. AUC {str(mod['auc_prueba'])[:4].replace('.', ',')} con los CSV (Anexo: 0,81).</p></div>
<div><img src="{fig('fig_A5_recompra.png')}"><p class="cap">Con la misma calificación, quien recibe tarde recompra ~27 pp menos.</p></div></div>{foot(3)}</section>

<section class="s"><div class="k">Argumento 2</div><h1>El problema está en Santiago y en la bodega Sur, no en Bodega Centro</h1>
<div class="g2"><div><img src="{fig('fig_A4_simpson.png')}"><p class="cap">Paradoja de Simpson: separado por tipo de pedido, Centro es la que menos atrasa. Cerrarla (A4) empeoraría la operación.</p></div>
<div><img src="{fig('fig_A3_volumen_vs_tasa.png')}"><p class="cap">Santiago: más volumen y {pct(k['stgo_atr'])} de atraso; p90 de {ci.loc['Santiago', 'p90_min']:.0f} min frente a una meta de 60. Sur concentra {pct(k['sur_share_atr'], 0)} de sus atrasos.</p></div></div>{foot(4)}</section>

<section class="s"><div class="k">Argumento 3</div><h1>El memo de Marketing se apoya en seis errores de lectura</h1>
<table><thead><tr><th>Afirmación</th><th>Error</th><th>Lectura correcta</th></tr></thead><tbody>
{''.join(f"<tr><td><b>{r.afirmacion}</b> · {r.tema}</td><td>{r.tipo_error}</td><td>{r.lectura_correcta}</td></tr>" for r in k['aud'].itertuples())}
</tbody></table>{foot(5)}</section>

<section class="s"><div class="k">Propuesta</div><h1>USD 3 M en cinco iniciativas, con metas medibles en el dashboard</h1>
<div class="g2" style="grid-template-columns:1.35fr 1fr"><div><table><thead><tr><th>Iniciativa</th><th>Palanca</th><th style="text-align:right">USD M</th></tr></thead><tbody>{inv}
<tr><td><b>Total</b> (cupones: USD 0)</td><td></td><td style="text-align:right"><b>3,00</b></td></tr></tbody></table>
<p class="cap">Asignación proporcional a la importancia de cada palanca en la Tabla E.</p></div>
<div><div class="card az"><div class="act" style="color:{C['marca']}">Metas H1 2027</div>
<p>p90 Santiago &lt; 60 min · atrasos ≤ 12 % · recompra a 30 días de vuelta al 41 % · reclamos ≤ 12,6 por 100 pedidos · 0 reclamos sin respuesta en 24 h.</p></div>
<div class="card" style="margin-top:5mm"><div class="act">Plazos</div><p>Dic 2026: piloto en Bodega Sur. Ene–mar 2027: Santiago. Abr–jun 2027: regiones y evaluación.</p></div></div></div>{foot(6)}</section>

<section class="s"><div class="k">Monitoreo y decisión</div><h1>Un dashboard único para seguir el plan, y la decisión que pedimos hoy</h1>
<div class="g2" style="grid-template-columns:1.3fr 1fr"><div><img src="{b64(CAP / '01_vista_estrategica.png')}" style="border:.8pt solid {C['borde']}"><p class="cap">Dashboard en Streamlit: KPIs unificados, drill-down por ciudad y bodega, paleta accesible (WCAG 2.1).</p></div>
<div><p><b>Limitaciones</b></p><ul style="padding-left:6mm"><li>Sur no reportaba datos: se exigirán por contrato.</li><li>La encuesta solo llega tras el 2.º pedido: se encuestará tras el 1.º y al abandonar.</li></ul>
<div class="dec" style="margin-top:6mm">Aprobar antes del cierre de 2026 los USD 3 M para operaciones y designar un responsable por iniciativa.</div></div></div>{foot(7)}</section>
</body></html>"""


def _navegador():
    for c in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              shutil.which("msedge") or "", shutil.which("google-chrome") or "", shutil.which("chromium") or ""]:
        if c and Path(c).exists():
            return c
    return None


def a_pdf(html_path: Path, pdf_path: Path):
    nav = _navegador()
    if not nav:
        print(f"Sin Edge/Chrome: abre {html_path.name} en el navegador e imprime a PDF.")
        return
    subprocess.run([nav, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], capture_output=True, timeout=180)
    print("PDF:", pdf_path.relative_to(cfg.RAIZ_PROYECTO))


def main():
    k = cifras()
    for carpeta, nombre, html in [(INF, "Informe_Ejecutivo_RapiMarket", informe(k)),
                                  (PRE, "Presentacion_Ejecutiva_RapiMarket", presentacion(k))]:
        fuente = carpeta / "fuente"
        fuente.mkdir(parents=True, exist_ok=True)
        h = fuente / f"{nombre}.html"
        h.write_text(html, encoding="utf-8")
        a_pdf(h, carpeta / f"{nombre}.pdf")


if __name__ == "__main__":
    main()
