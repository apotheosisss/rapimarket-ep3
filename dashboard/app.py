"""
Dashboard interactivo · RapiMarket Q3 2026 (EP3 Parte 2 · ADY1104 Visualización de Datos)

Traduce a Streamlit el wireframe en papel milimetrado de la Parte 1:
  fila 1  -> filtros Periodo / Año + 4 KPIs (clientes activos, pedidos, ventas, reclamos) con variación
  fila 2  -> Clientes por zona · Ventas vs Meta · Reclamos por bodega
  fila 3  -> Datos trimestrales (tabla) con la columna "Peor bodega (según p90)"
  drill-down en otra página (Vista operativa) al hacer clic en una ciudad.

Ejecutar desde la raíz del proyecto:
    streamlit run dashboard/app.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "codigo_y_data"))

from src import config as cfg               # noqa: E402
from src.pipeline import kpis, p90          # noqa: E402

C = cfg.COL
st.set_page_config(page_title="RapiMarket · Dashboard Q3 2026", page_icon="📦", layout="wide",
                   initial_sidebar_state="expanded")

# ======================================================================== estilo
st.markdown(f"""
<style>
.block-container {{padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px;}}
h1, h2, h3 {{color: {C['marca']};}}
.kpi {{background:#fff; border:1px solid {C['borde']}; border-radius:10px; padding:12px 16px 10px; height:100%;}}
.kpi .lab {{font-size:.86rem; color:{C['gris_txt']}; font-weight:600; display:flex; justify-content:space-between; gap:8px}}
.kpi .val {{font-size:1.9rem; font-weight:700; color:{C['tinta']}; line-height:1.15; margin:4px 0 2px}}
.kpi .val small {{font-size:.95rem; color:{C['gris_txt']}; font-weight:600}}
.kpi .dlt {{font-size:.86rem; font-weight:600}}
.kpi .sub {{font-size:.78rem; color:{C['gris_txt']}}}
.est {{font-size:.78rem; font-weight:700; white-space:nowrap}}
.ok {{color:{C['ok']}}} .al {{color:{C['alerta_txt']}}} .ne {{color:{C['gris_txt']}}}
.banner {{background:#FFF4E8; border-left:6px solid {C['alerta']}; border-radius:6px; padding:10px 16px;
          font-size:1.02rem; font-weight:600; color:{C['tinta']}; margin:4px 0 12px}}
.banner.azul {{background:#EAF1F9; border-left-color:{C['ok']}}}
.pie {{color:{C['gris_txt']}; font-size:.8rem}}
div[data-testid="stCaptionContainer"] p {{color:{C['gris_txt']};}}
</style>
""", unsafe_allow_html=True)


# ======================================================================== datos
@st.cache_data(show_spinner="Cargando datos integrados...")
def cargar_datos():
    ruta = cfg.DIR_PROC / "pedidos_integrados.csv.gz"
    if not ruta.exists():                      # reproducibilidad: genera el pipeline si falta
        from src import pipeline
        pipeline.main()
    df = pd.read_csv(ruta, parse_dates=["fecha", "fecha_siguiente", "semana"])
    df["calif_grupo"] = pd.Categorical(df["calif_grupo"], ["1-2", "3", "4-5"])
    return df


@st.cache_data
def cargar_resultados():
    r = cfg.DIR_RES
    out = {}
    for n in ["auditoria_A1_A6", "importancia_random_forest", "calidad_tablas", "calidad_controles"]:
        f = r / f"{n}.csv"
        out[n] = pd.read_csv(f) if f.exists() else None
    f = r / "modelo_fuga.json"
    out["modelo"] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    return out


df_all = cargar_datos()
res = cargar_resultados()


# ======================================================================== utilidades
def miles(x):
    return f"{x:,.0f}".replace(",", ".")


def pct(x, d=1):
    return f"{x * 100:.{d}f} %".replace(".", ",")


def num(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def clp_m(x):
    return f"CLP {x / 1e6:,.0f} M".replace(",", ".")


def kpi_card(label, valor, unidad="", delta=None, bueno_si_sube=True, sub="", estado=None):
    """Tarjeta KPI accesible: color + flecha + texto (nunca solo color)."""
    est_html = ""
    if estado is not None:
        cls, ico, txt = ("ok", "✔", "Cumple meta") if estado else ("al", "▲", "Bajo meta")
        if estado is False:
            ico = "⚠"
        est_html = f'<span class="est {cls}">{ico} {txt}</span>'
    dlt_html = ""
    if delta is not None and not np.isnan(delta):
        sube = delta > 0
        favorable = sube == bueno_si_sube
        cls = "ok" if favorable else "al"
        flecha = "▲" if sube else "▼"
        palabra = "mejora" if favorable else "empeora"
        dlt_html = f'<div class="dlt {cls}">{flecha} {delta:+.1f} %'.replace(".", ",") + f' vs mes anterior · {palabra}</div>'
    elif delta is not None:
        dlt_html = '<div class="dlt ne">— sin mes anterior en los datos</div>'
    st.markdown(f"""<div class="kpi"><div class="lab"><span>{label}</span>{est_html}</div>
        <div class="val">{valor} <small>{unidad}</small></div>{dlt_html}<div class="sub">{sub}</div></div>""",
                unsafe_allow_html=True)


def layout(fig, h=320, leyenda=True):
    fig.update_layout(height=h, margin=dict(l=8, r=12, t=8, b=8), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family="Segoe UI, Arial", size=12.5, color=C["tinta"]),
                      hoverlabel=dict(bgcolor="white", font_size=12.5),
                      showlegend=leyenda, legend=dict(orientation="h", y=1.08, x=0, title=None))
    fig.update_xaxes(showgrid=False, linecolor=C["gris"])
    fig.update_yaxes(gridcolor=C["borde"], zeroline=False)
    return fig


def var_pct(a, b):
    return (a / b - 1) * 100 if b else np.nan


def _peor_total(d):
    s = d[d["ciudad_bodega"] == "Santiago"]
    if s.empty:
        return "—"
    g = s.groupby("bodega")["tiempo_entrega_min"].apply(p90)
    return f"{g.idxmax()} ({g.max():.0f} min)"


def _drill_ciudad():
    """Drill-down: al hacer clic en una ciudad se abre la Vista operativa filtrada por esa ciudad."""
    ev = st.session_state.get("zona")
    pts = ev.selection.points if ev and ev.selection else []
    if pts and pts[0].get("y"):
        st.session_state.ciudad_drill = pts[0]["y"]
        st.session_state.pagina = "Vista operativa"


# ======================================================================== navegación y filtros
PAGINAS = ["Vista estratégica", "Vista operativa", "Auditoría del memo (A1–A6)", "Fuga de clientes", "Calidad de datos y método"]
if "pagina" not in st.session_state:
    st.session_state.pagina = PAGINAS[0]
if "ciudad_drill" not in st.session_state:
    st.session_state.ciudad_drill = "Todas"

with st.sidebar:
    st.markdown(f"<h2 style='margin:0'>RapiMarket</h2><div class='pie'>Comité Ejecutivo · Q3 2026</div>", unsafe_allow_html=True)
    pagina = st.radio("Página", PAGINAS, key="pagina")
    st.divider()
    st.markdown("**Filtros operativos**")
    ciudades = ["Todas"] + sorted(df_all["ciudad_bodega"].unique(), key=lambda c: (c != "Santiago", c))
    ciudad = st.selectbox("Ciudad", ciudades, key="ciudad_drill",
                          help="También se elige haciendo clic en una ciudad del gráfico 'Clientes por zona'.")
    bod_opts = sorted(df_all.loc[df_all.ciudad_bodega == ciudad, "bodega"].unique()) if ciudad != "Todas" else sorted(df_all["bodega"].unique())
    bodegas = st.multiselect("Bodega", bod_opts, default=bod_opts)
    tipo = st.radio("Tipo de pedido", ["Todos", "Simple", "Complejo"], horizontal=True,
                    help="Complejo = más de 30 productos, congelados o más de 6 km.")
    st.divider()
    st.caption("Paleta segura para daltonismo: **azul = cumple**, **naranja = alerta**, gris = contexto. "
               "Cada estado también se indica con ícono y texto (WCAG 2.1).")
    st.caption("Datos: 6 CSV del grupo 11 (01-jul a 30-sep-2026). Visitas a la app: Anexo oficial.")

df_f = df_all.copy()
if ciudad != "Todas":
    df_f = df_f[df_f["ciudad_bodega"] == ciudad]
if bodegas:
    df_f = df_f[df_f["bodega"].isin(bodegas)]
if tipo != "Todos":
    df_f = df_f[df_f["tipo_pedido"] == tipo]
filtros_txt = " · ".join(x for x in [ciudad if ciudad != "Todas" else "", ", ".join(bodegas) if len(bodegas) < len(bod_opts) else "",
                                     tipo if tipo != "Todos" else ""] if x) or "sin filtros operativos"


# ======================================================================== 1. VISTA ESTRATÉGICA (wireframe)
def vista_estrategica():
    cab = st.columns([5, 1.3, 1])
    cab[0].markdown("## Panorama del trimestre")
    periodo = cab[1].selectbox("Periodo", ["Q3 completo", "Julio", "Agosto", "Septiembre"], index=0)
    cab[2].selectbox("Año", [2026], index=0, disabled=True, help="Los datos disponibles cubren solo el Q3 2026.")
    st.caption(f"Filtros activos: {filtros_txt}. Los KPIs comparan el mes {'final del período' if periodo == 'Q3 completo' else 'elegido'} contra el mes anterior.")

    meses = {"Q3 completo": [7, 8, 9], "Julio": [7], "Agosto": [8], "Septiembre": [9]}[periodo]
    mes_ref = meses[-1]
    men = kpis(df_f, "mes").set_index("mes")
    ref = men.loc[mes_ref] if mes_ref in men.index else None
    prev = men.loc[mes_ref - 1] if (mes_ref - 1) in men.index else None
    per = df_f[df_f["mes"].isin(meses)]

    caida = var_pct(men.loc[9, "pedidos"], men.loc[7, "pedidos"]) if {7, 9} <= set(men.index) else np.nan
    st.markdown(f"""<div class="banner">Los pedidos cayeron {num(abs(caida))} % entre julio y septiembre y los reclamos por pedido suben:
        la fuga se explica por la entrega (atrasos y faltantes), no por falta de cupones.</div>""", unsafe_allow_html=True)

    # ---- fila 1: 4 KPIs del wireframe (diccionario unificado T5)
    k = st.columns(4)
    with k[0]:
        kpi_card(f"Clientes activos en {cfg.MESES[mes_ref].lower()}", miles(ref["clientes_activos"]) if ref is not None else "—", "",
                 var_pct(ref["clientes_activos"], prev["clientes_activos"]) if prev is not None else np.nan,
                 sub="Definición única: clientes con ≥ 1 pedido en el mes")
    with k[1]:
        kpi_card(f"Pedidos de {cfg.MESES[mes_ref].lower()}", miles(ref["pedidos"]) if ref is not None else "—", "",
                 var_pct(ref["pedidos"], prev["pedidos"]) if prev is not None else np.nan,
                 sub="Meta: mantener o crecer vs mes anterior",
                 estado=(None if prev is None else bool(ref["pedidos"] >= prev["pedidos"])))
    with k[2]:
        v = per["ticket_total_clp"].sum()
        kpi_card(f"Ventas de {cfg.MESES[mes_ref].lower()}", clp_m(ref["ventas_clp"]) if ref is not None else "—", "",
                 var_pct(ref["ventas_clp"], prev["ventas_clp"]) if prev is not None else np.nan,
                 sub=(f"Total Q3: {clp_m(v)}. " if len(meses) > 1 else "") + "Productos + cargo de servicio")
    with k[3]:
        kpi_card("Reclamos por 100 pedidos", num(ref["reclamos_100"]) if ref is not None else "—", "",
                 var_pct(ref["reclamos_100"], prev["reclamos_100"]) if prev is not None else np.nan,
                 bueno_si_sube=False, estado=bool(ref["reclamos_100"] <= cfg.META_RECLAMOS_100) if ref is not None else None,
                 sub=f"Meta ≤ {num(cfg.META_RECLAMOS_100)} (julio, Anexo). Memo: 1,2 % sobre visitas")

    # ---- franja de metas de la decisión
    st.write("")
    m = st.columns(3)
    stgo = per[per["ciudad_bodega"] == "Santiago"]
    with m[0]:
        t = per["atrasado"].mean()
        kpi_card("Pedidos atrasados", pct(t), "", sub=f"Meta ≤ {pct(cfg.META_ATRASO, 0)} (nivel de Valparaíso, Tabla B)",
                 estado=bool(t <= cfg.META_ATRASO))
    with m[1]:
        v = p90(stgo["tiempo_entrega_min"]) if len(stgo) else np.nan
        kpi_card("p90 de entrega en Santiago", "—" if np.isnan(v) else f"{v:.0f}", "min",
                 sub=f"Meta < {cfg.META_P90_MIN} min (Anexo, Tabla B)", estado=None if np.isnan(v) else bool(v < cfg.META_P90_MIN))
    with m[2]:
        cg = per[per["con_congelados"]]
        v = cg["frio_roto"].mean() if len(cg) else np.nan
        kpi_card("Congelados fuera de temperatura", "—" if np.isnan(v) else pct(v), "",
                 sub=f"Llegan sobre {num(cfg.UMBRAL_FRIO_C, 0)} °C · 1 de cada {0 if not v else round(1 / v)} pedidos con congelados")

    st.write("")
    # ---- fila 2: tres gráficos del wireframe
    g = st.columns([1, 1.25, 1.1])
    with g[0]:
        st.markdown("#### Clientes por zona")
        z = kpis(per, "ciudad_bodega").sort_values("clientes_activos")
        cols = [C["alerta"] if t > cfg.META_ATRASO else C["ok"] for t in z["tasa_atraso"]]
        patron = ["/" if c == "Santiago" else "" for c in z["ciudad_bodega"]]
        fig = go.Figure(go.Bar(x=z["clientes_activos"], y=z["ciudad_bodega"], orientation="h",
                               marker=dict(color=cols, pattern_shape=patron, pattern_fgcolor="white"),
                               text=[f"<b>{miles(c)}</b> · {pct(t)} {'⚠' if t > cfg.META_ATRASO else '✔'}" for c, t in zip(z["clientes_activos"], z["tasa_atraso"])],
                               textposition="outside", cliponaxis=False,
                               customdata=np.c_[z["pedidos"], z["tasa_atraso"] * 100, z["p90_min"]],
                               hovertemplate="<b>%{y}</b><br>Clientes activos: %{x:,.0f}<br>Pedidos: %{customdata[0]:,.0f}"
                                             "<br>Atrasados: %{customdata[1]:.1f} %<br>p90: %{customdata[2]:.0f} min<extra>Clic para ver detalle</extra>"))
        layout(fig, 300, False).update_xaxes(title=None, showticklabels=False, range=[0, z["clientes_activos"].max() * 1.9])
        st.plotly_chart(fig, width="stretch", on_select=_drill_ciudad, selection_mode="points", key="zona")
        st.caption("Barra = clientes distintos con pedido en el período; texto = % de pedidos atrasados. Naranja = atraso sobre la meta de 12 %; Santiago rayado como en el wireframe. "
                   "**Clic en una barra** para abrir su detalle operativo.")
    with g[1]:
        st.markdown("#### Ventas vs Meta")
        w = df_f.groupby("semana").agg(ventas=("ticket_total_clp", "sum"), dias=("fecha", "nunique")).reset_index()
        w = w[w["dias"] == 7].reset_index(drop=True)          # solo semanas completas (lunes a domingo)
        # Meta: mantener el ritmo del último trimestre fiscal reportado por Finanzas (D3: CLP 7.335 M en jun-ago = 13 semanas)
        meta = 7_335e6 / 13
        colp = [C["ok"] if v >= meta else C["alerta"] for v in w["ventas"]]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=w["semana"], y=w["ventas"] / 1e6, mode="lines+markers", name="Ventas",
                                 line=dict(color=C["tinta"], width=2.4), marker=dict(color=colp, size=9, line=dict(color="white", width=1)),
                                 hovertemplate="Semana del %{x|%d-%b}<br>Ventas: CLP %{y:,.0f} M<extra></extra>"))
        if len(w):
            fig.add_trace(go.Scatter(x=[w["semana"].min(), w["semana"].max()], y=[meta / 1e6] * 2, mode="lines", name="Meta",
                                     line=dict(color=C["tinta"], dash="dash", width=1.6), hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Periodos", line=dict(color=C["gris"], width=1)))
        vm = df_f.groupby("mes")["ticket_total_clp"].sum()
        ymax = max(w["ventas"].max() if len(w) else 0, meta) / 1e6 * 1.3
        for mm, ini in [(7, "2026-07-01"), (8, "2026-08-01"), (9, "2026-09-01")]:
            if mm in vm.index:
                if mm > 7:
                    fig.add_shape(type="line", x0=ini, x1=ini, y0=0, y1=ymax, line=dict(color=C["gris"], width=1))
                fig.add_annotation(x=pd.Timestamp(ini) + pd.Timedelta(days=15), y=ymax * 0.95, showarrow=False,
                                   text=f"<b>{cfg.MESES[mm]}</b><br>{clp_m(vm[mm])}", font=dict(size=11, color=C["gris_txt"]))
        if len(w):
            i = w["ventas"].idxmax()
            f = w.index[-1]
            fig.add_annotation(x=w.loc[i, "semana"], y=w.loc[i, "ventas"] / 1e6, text=f"{w.loc[i, 'ventas'] / 1e6:,.0f}".replace(",", "."),
                               showarrow=False, xshift=22, font=dict(size=11, color=C["tinta"]))
            fig.add_annotation(x=w.loc[f, "semana"], y=w.loc[f, "ventas"] / 1e6, text=f"{w.loc[f, 'ventas'] / 1e6:,.0f}".replace(",", "."),
                               showarrow=False, yshift=-15, font=dict(size=11, color=C["alerta_txt"]))
        layout(fig, 320).update_yaxes(title="CLP millones por semana", range=[0, ymax])
        fig.update_layout(legend=dict(orientation="h", y=-0.18, x=0))
        st.plotly_chart(fig, width="stretch", key="ventas")
        st.caption(f"Semanas completas. Meta = ritmo del trimestre fiscal jun–ago de D3 (CLP 7.335 M ÷ 13 = {meta / 1e6:,.0f} M por semana)".replace(",", ".")
                   + ". Punto naranja = semana bajo la meta. Los pedidos suben hasta el 20-jul y caen desde el 21-jul.")
    with g[2]:
        st.markdown("#### Reclamos por bodega")
        sg = df_f[df_f["ciudad_bodega"] == "Santiago"]
        rb = sg.groupby(["mes", "bodega"]).agg(rec=("n_reclamos", "sum"), ped=("pedido_id", "size")).reset_index()
        rb["r100"] = rb["rec"] / rb["ped"] * 100
        rb["periodo"] = rb["mes"].map(cfg.MESES)
        fig = go.Figure()
        estilos = {"Centro": "dot", "Norte": "solid", "Sur": "dash"}
        simb = {"Centro": "circle", "Norte": "square", "Sur": "triangle-up"}
        posic = {"Centro": "bottom center", "Norte": "bottom center", "Sur": "top center"}
        for b in ["Norte", "Sur", "Centro"]:
            d = rb[rb["bodega"] == b]
            if d.empty:
                continue
            fig.add_trace(go.Scatter(x=d["periodo"], y=d["r100"], name=b + (" (externo)" if b == "Sur" else ""),
                                     mode="lines+markers+text", text=[num(v) for v in d["r100"]], textposition=posic[b],
                                     textfont=dict(size=11, color=cfg.COL_BODEGA[b]),
                                     line=dict(color=cfg.COL_BODEGA[b], dash=estilos[b], width=2.4), marker=dict(symbol=simb[b], size=9),
                                     customdata=np.c_[d["rec"], d["ped"]],
                                     hovertemplate=f"<b>{b}</b> · %{{x}}<br>%{{y:.1f}} reclamos por 100 pedidos"
                                                   "<br>%{customdata[0]:,.0f} reclamos / %{customdata[1]:,.0f} pedidos<extra></extra>"))
        top = rb["r100"].max() if len(rb) else 25
        layout(fig, 300).update_yaxes(title="Reclamos por 100 pedidos", range=[0, top * 1.25])
        fig.update_xaxes(type="category")
        st.plotly_chart(fig, width="stretch", key="reclamos")
        st.caption("Bodegas de Santiago por mes, incluida Sur (operador externo, omitida en D2). Tasa sobre pedidos para comparar bodegas de distinto tamaño.")

    # ---- fila 3: datos trimestrales
    st.markdown("#### Datos trimestrales")
    t = kpis(df_f, "mes").set_index("mes")
    stg = df_f[df_f["ciudad_bodega"] == "Santiago"]
    if len(stg):
        pb = stg.groupby(["mes", "bodega"])["tiempo_entrega_min"].apply(p90).reset_index()
        pb = pb.loc[pb.groupby("mes")["tiempo_entrega_min"].idxmax()].set_index("mes")
        t["peor"] = pb["bodega"] + " (" + pb["tiempo_entrega_min"].round().astype(int).astype(str) + " min)"
    else:
        t["peor"] = "—"
    tot = kpis(df_f.assign(q="Total Q3"), "q").iloc[0]
    filas = [{"Período": cfg.MESES[mm], "Clientes activos": miles(r["clientes_activos"]), "Pedidos entregados": miles(r["pedidos"]),
              "Pedidos atrasados": f"{miles(r['atrasados'])} ({pct(r['tasa_atraso'])})", "Reclamos": miles(r["reclamos"]),
              "Ventas totales": clp_m(r["ventas_clp"]), "Visitas app (Anexo)": miles(cfg.ANEXO["visitas_app_mes"]),
              "Peor bodega (según p90)": r["peor"]} for mm, r in t.iterrows()]
    filas.append({"Período": "Total Q3", "Clientes activos": miles(tot["clientes_activos"]), "Pedidos entregados": miles(tot["pedidos"]),
                  "Pedidos atrasados": f"{miles(tot['atrasados'])} ({pct(tot['tasa_atraso'])})", "Reclamos": miles(tot["reclamos"]),
                  "Ventas totales": clp_m(tot["ventas_clp"]), "Visitas app (Anexo)": miles(cfg.ANEXO["visitas_app_q3"]),
                  "Peor bodega (según p90)": _peor_total(df_f)})
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")
    st.caption("Clientes activos del total = clientes distintos del trimestre. Peor bodega: mayor p90 de entrega entre las bodegas de Santiago.")


# ======================================================================== 2. VISTA OPERATIVA (drill-down)
def vista_operativa():
    st.markdown(f"## Vista operativa · {ciudad if ciudad != 'Todas' else 'todas las ciudades'}")
    st.caption(f"Filtros activos: {filtros_txt}. Para volver al panorama usa la página 'Vista estratégica'.")
    if df_f.empty:
        st.warning("No hay pedidos con los filtros elegidos.")
        return
    k = st.columns(5)
    t = df_f["atrasado"].mean()
    with k[0]:
        kpi_card("Pedidos atrasados", pct(t), "", sub=f"Meta ≤ {pct(cfg.META_ATRASO, 0)}", estado=bool(t <= cfg.META_ATRASO))
    v = p90(df_f["tiempo_entrega_min"])
    with k[1]:
        kpi_card("p90 de entrega", f"{v:.0f}", "min", sub=f"Meta < {cfg.META_P90_MIN} min", estado=bool(v < cfg.META_P90_MIN))
    with k[2]:
        kpi_card("Con faltantes o sustituidos", pct(df_f["faltantes"].mean()), "", sub="Anexo: 21 % del total")
    cg = df_f[df_f["con_congelados"]]
    with k[3]:
        kpi_card("Congelados fuera de temperatura", pct(cg["frio_roto"].mean()) if len(cg) else "—", "", sub=f"Sobre {num(cfg.UMBRAL_FRIO_C, 0)} °C")
    rc = df_f[df_f["con_reclamo"]]
    with k[4]:
        kpi_card("Reclamos sin respuesta > 24 h", pct(rc["reclamo_tardio"].mean()) if len(rc) else "—", "", sub="Tabla E: sube la fuga de 31 % a 61 %")

    st.write("")
    c = st.columns([1.15, 1])
    with c[0]:
        st.markdown("#### Atrasos por bodega: total vs separado por tipo")
        modo = st.radio("Ver", ["Separado por tipo de pedido", "Total por bodega (lo que vio el memo)"], horizontal=True, label_visibility="collapsed")
        base = df_f if ciudad != "Todas" else df_f[df_f["ciudad_bodega"] == "Santiago"]
        if modo.startswith("Total"):
            a = base.groupby("bodega").agg(t=("atrasado", "mean"), n=("pedido_id", "size"), cx=("complejo", "mean")).reset_index()
            fig = go.Figure(go.Bar(x=a["bodega"], y=a["t"] * 100, marker_color=[cfg.COL_BODEGA.get(b, C["gris"]) for b in a["bodega"]],
                                   text=[pct(x) for x in a["t"]], textposition="outside",
                                   customdata=np.c_[a["n"], a["cx"] * 100],
                                   hovertemplate="<b>%{x}</b><br>%{y:.1f} % atrasados<br>%{customdata[0]:,.0f} pedidos<br>%{customdata[1]:.0f} % complejos<extra></extra>"))
            layout(fig, 330, False)
        else:
            a = base.groupby(["bodega", "tipo_pedido"]).agg(t=("atrasado", "mean"), n=("pedido_id", "size")).reset_index()
            fig = go.Figure()
            for tp, col, pat in [("Simple", C["gris"], ""), ("Complejo", C["alerta"], "/")]:
                d = a[a["tipo_pedido"] == tp]
                fig.add_trace(go.Bar(x=d["bodega"], y=d["t"] * 100, name=tp, marker=dict(color=col, pattern_shape=pat),
                                     text=[pct(x) for x in d["t"]], textposition="outside", customdata=d["n"],
                                     hovertemplate=f"<b>%{{x}}</b> · {tp}<br>%{{y:.1f}} % atrasados<br>%{{customdata:,.0f}} pedidos<extra></extra>"))
            layout(fig, 330).update_layout(barmode="group")
        fig.update_yaxes(title="% de pedidos atrasados", range=[0, a["t"].max() * 100 * 1.2])
        st.plotly_chart(fig, width="stretch", key="simpson")
        st.caption("Paradoja de Simpson: en total Centro parece peor que Norte, pero dentro de cada tipo de pedido atrasa menos. "
                   "Centro atiende sobre todo pedidos complejos.")
    with c[1]:
        st.markdown("#### p90 de entrega por ciudad vs meta")
        z = kpis(df_f, "ciudad_bodega").sort_values("p90_min")
        fig = go.Figure(go.Bar(x=z["p90_min"], y=z["ciudad_bodega"], orientation="h",
                               marker_color=[C["alerta"] if v >= cfg.META_P90_MIN else C["ok"] for v in z["p90_min"]],
                               text=[f"{v:.0f} min {'⚠' if v >= cfg.META_P90_MIN else '✔'}" for v in z["p90_min"]], textposition="outside",
                               customdata=np.c_[z["mediana_min"], z["pedidos"]],
                               hovertemplate="<b>%{y}</b><br>p90: %{x:.0f} min<br>Mediana: %{customdata[0]:.0f} min<br>%{customdata[1]:,.0f} pedidos<extra></extra>"))
        fig.add_vline(x=cfg.META_P90_MIN, line_dash="dash", line_color=C["tinta"], annotation_text=f"Meta {cfg.META_P90_MIN} min")
        layout(fig, 330, False).update_xaxes(range=[0, max(80, z["p90_min"].max() + 12)], title="minutos")
        st.plotly_chart(fig, width="stretch", key="p90")

    st.markdown("#### Tendencia semanal de atrasos por bodega")
    w = df_f.groupby(["semana", "bodega"]).agg(t=("atrasado", "mean"), dias=("fecha", "nunique")).reset_index()
    w = w[w["dias"] == 7]
    fig = go.Figure()
    dashes = ["solid", "dot", "dash", "dashdot", "longdash", "longdashdot", "solid"]
    for i, b in enumerate(sorted(w["bodega"].unique(), key=lambda x: (x not in cfg.COL_BODEGA, x))):
        d = w[w["bodega"] == b]
        fig.add_trace(go.Scatter(x=d["semana"], y=d["t"] * 100, name=b, mode="lines+markers",
                                 line=dict(color=cfg.COL_BODEGA.get(b, C["gris"]), dash=dashes[i % 7], width=2.2),
                                 hovertemplate=f"<b>{b}</b> · semana del %{{x|%d-%b}}<br>%{{y:.1f}} % atrasados<extra></extra>"))
    fig.add_hline(y=cfg.META_ATRASO * 100, line_dash="dash", line_color=C["tinta"], annotation_text="Meta 12 %")
    layout(fig, 300).update_yaxes(title="% atrasados", rangemode="tozero")
    st.plotly_chart(fig, width="stretch", key="tend")

    with st.expander("Ver los pedidos con mayor retraso (detalle)", expanded=False):
        cols = ["pedido_id", "fecha", "ciudad_bodega", "bodega", "tipo_pedido", "n_productos", "tiempo_entrega_min",
                "faltantes", "frio_roto", "categoria_reclamo", "horas_respuesta", "estrellas"]
        st.dataframe(df_f.nlargest(200, "tiempo_entrega_min")[cols].rename(columns={
            "ciudad_bodega": "ciudad", "tiempo_entrega_min": "minutos", "categoria_reclamo": "reclamo",
            "horas_respuesta": "horas resp. reclamo"}), hide_index=True, width="stretch", height=320)


# ======================================================================== 3. AUDITORÍA DEL MEMO
def vista_auditoria():
    st.markdown("## Auditoría del Memo de Marketing (A1–A6)")
    st.markdown('<div class="banner">Las 6 afirmaciones del memo se apoyan en errores de lectura de datos. Corregidas, todas apuntan a la operación, no a los cupones.</div>', unsafe_allow_html=True)
    aud = res["auditoria_A1_A6"]
    if aud is None:
        st.info("Ejecuta `python -m src.auditoria` en codigo_y_data para generar los recálculos.")
        return
    t = aud.rename(columns={"afirmacion": "Afirm.", "dice_memo": "Dice el memo", "tipo_error": "Tipo de error",
                            "recalculo_anexo": "Recálculo con el Anexo", "recalculo_csv": "Recálculo con los CSV",
                            "lectura_correcta": "Lectura correcta", "decision_erronea": "Decisión errónea que provoca"}).drop(columns="tema")
    st.table(t.set_index("Afirm."))
    st.markdown("#### Evidencia visual")
    tabs = st.tabs(["A2 · Pedidos y ticket", "A3 · Volumen vs tasa", "A4 · Simpson", "A5 · Recompra", "A6 · Encuesta"])
    men = kpis(df_all, "mes")
    with tabs[0]:
        c = st.columns(2)
        acum = cfg.ANEXO["acumulado_jun"] + men["pedidos"].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[cfg.MESES[m] for m in men["mes"]], y=men["pedidos"], name="Pedidos del mes", marker_color=[C["gris"], C["gris"], C["alerta"]],
                             text=[miles(v) for v in men["pedidos"]], textposition="outside"))
        layout(fig, 300, False).update_yaxes(title="Pedidos del mes", rangemode="tozero")
        c[0].plotly_chart(fig, width="stretch", key="a2a")
        c[0].caption(f"El acumulado histórico sube (≈ {miles(acum.iloc[-1])} con los CSV) aunque cada mes se vende menos.")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[cfg.MESES[m] for m in men["mes"]], y=men["ticket_productos"], name="Productos", marker_color=C["ok"]))
        fig.add_trace(go.Bar(x=[cfg.MESES[m] for m in men["mes"]], y=men["ticket_total"] - men["ticket_productos"], name="Cargo de servicio", marker_color=C["alerta"],
                             marker_pattern_shape="/"))
        layout(fig, 300).update_layout(barmode="stack").update_yaxes(title="Ticket promedio (CLP)", rangemode="tozero")
        c[1].plotly_chart(fig, width="stretch", key="a2b")
        c[1].caption("El ticket de productos no sube; el alza es el cargo de CLP 1.990 aplicado desde agosto.")
    with tabs[1]:
        z = kpis(df_all, "ciudad_bodega").sort_values("pedidos", ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=z["ciudad_bodega"], y=z["pedidos"], name="Pedidos (barras)", marker_color=[C["alerta"] if c == "Santiago" else C["gris"] for c in z["ciudad_bodega"]], yaxis="y"))
        fig.add_trace(go.Scatter(x=z["ciudad_bodega"], y=z["tasa_atraso"] * 100, name="% atrasados (línea)", mode="lines+markers+text",
                                 text=[pct(v) for v in z["tasa_atraso"]], textposition="top center", line=dict(color=C["tinta"]), yaxis="y2"))
        layout(fig, 330).update_layout(yaxis=dict(title="Pedidos"), yaxis2=dict(title="% atrasados", overlaying="y", side="right", range=[0, 30], showgrid=False))
        st.plotly_chart(fig, width="stretch", key="a3")
        st.caption("Más volumen no es mejor desempeño: Santiago tiene el doble de atrasos que el resto.")
    with tabs[2]:
        s = df_all[df_all["ciudad_bodega"] == "Santiago"].groupby(["bodega", "tipo_pedido"])["atrasado"].mean().unstack()
        tot = df_all[df_all["ciudad_bodega"] == "Santiago"].groupby("bodega")["atrasado"].mean()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=tot.index, y=tot * 100, name="Total (memo)", marker_color=C["borde"], marker_line_color=C["gris_txt"], marker_line_width=1))
        fig.add_trace(go.Bar(x=s.index, y=s["Simple"] * 100, name="Simple", marker_color=C["gris"]))
        fig.add_trace(go.Bar(x=s.index, y=s["Complejo"] * 100, name="Complejo", marker_color=C["alerta"], marker_pattern_shape="/"))
        layout(fig, 330).update_layout(barmode="group").update_yaxes(title="% atrasados")
        st.plotly_chart(fig, width="stretch", key="a4")
        st.caption("Dentro de cada tipo, Centro atrasa menos que Norte. Cerrar Centro empeoraría la operación. La peor bodega es Sur (externa).")
    with tabs[3]:
        o = df_all[df_all["recompra_30d"].notna()]
        a5 = o.groupby(["atrasado", "calif_grupo"], observed=True)["recompra_30d"].mean().unstack()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[f"{g} ★" for g in a5.columns], y=a5.loc[False] * 100, name="Entregado a tiempo", marker_color=C["ok"]))
        fig.add_trace(go.Bar(x=[f"{g} ★" for g in a5.columns], y=a5.loc[True] * 100, name="Atrasado", marker_color=C["alerta"], marker_pattern_shape="/"))
        layout(fig, 330).update_layout(barmode="group").update_yaxes(title="Recompra a 30 días (%)", range=[0, 80])
        st.plotly_chart(fig, width="stretch", key="a5")
        st.caption("Con la misma calificación, quien recibió tarde recompra mucho menos. La calificación no explica la fuga; el atraso sí.")
    with tabs[4]:
        cal = df_all["estrellas"].dropna().value_counts(normalize=True).sort_index()
        fig = go.Figure(go.Bar(x=[f"{int(i)} ★" for i in cal.index], y=cal * 100, marker_color=[C["alerta"] if i <= 2 else C["gris"] for i in cal.index],
                               text=[pct(v) for v in cal], textposition="outside"))
        layout(fig, 300, False).update_yaxes(title="% de pedidos calificados")
        st.plotly_chart(fig, width="stretch", key="a6")
        st.caption(f"Promedio de todos los pedidos calificados: {num(df_all['estrellas'].mean(), 2)} / 5, lejos del 4,6 de la encuesta "
                   "que solo recibieron clientes con 2.º pedido (sesgo de supervivencia).")


# ======================================================================== 4. FUGA
def vista_fuga():
    st.markdown("## Fuga de clientes: ¿qué la explica?")
    o = df_all[df_all["recompra_30d"].notna()]
    r = o.groupby("atrasado")["recompra_30d"].mean()
    st.markdown(f'<div class="banner">Un pedido atrasado baja la recompra a 30 días de {pct(r[False])} a {pct(r[True])}. '
                'Las variables operativas explican casi toda la fuga; el cupón, muy poco.</div>', unsafe_allow_html=True)
    c = st.columns([1.1, 1])
    with c[0]:
        st.markdown("#### Importancia de variables (Random Forest)")
        imp = res["importancia_random_forest"]
        if imp is not None:
            im = imp.sort_values("importancia_tabla_e_pct")
            fig = go.Figure()
            fig.add_trace(go.Bar(y=im["variable"], x=im["importancia_tabla_e_pct"], orientation="h", name="Tabla E (Anexo)", marker_color=C["gris"]))
            fig.add_trace(go.Bar(y=im["variable"], x=im["importancia_csv_pct"], orientation="h", name="Recalculado con CSV", marker_color=C["marca"],
                                 text=[f"{v:.0f} %" for v in im["importancia_csv_pct"]], textposition="outside"))
            layout(fig, 360).update_layout(barmode="group").update_xaxes(title="Importancia relativa (%)", range=[0, im["importancia_csv_pct"].max() + 12])
            st.plotly_chart(fig, width="stretch", key="rf")
            m = res["modelo"] or {}
            st.caption(f"AUC en prueba con las 7 variables de la Tabla E: {num(m.get('auc_prueba', np.nan), 2)} (Anexo: 0,81). "
                       "Importancia por permutación normalizada a 100 %. El orden coincide con el Anexo: atraso y faltantes primero; cupón, bajo.")
    with c[1]:
        st.markdown("#### Recompra a 30 días según la experiencia")
        filas = []
        for nombre, col in [("Atraso", "atrasado"), ("Faltantes", "faltantes"), ("Congelados fuera de temp.", "frio_roto"),
                            ("Reclamo > 24 h sin respuesta", "reclamo_tardio"), ("Usó cupón", "con_cupon")]:
            g = o.groupby(o[col].fillna(False).astype(bool))["recompra_30d"].mean()
            if True in g.index and False in g.index:
                filas.append((nombre, g[False], g[True]))
        d = pd.DataFrame(filas, columns=["Factor", "sin", "con"])
        fig = go.Figure()
        fig.add_trace(go.Bar(y=d["Factor"], x=d["sin"] * 100, orientation="h", name="Sin el factor", marker_color=C["ok"]))
        fig.add_trace(go.Bar(y=d["Factor"], x=d["con"] * 100, orientation="h", name="Con el factor", marker_color=C["alerta"], marker_pattern_shape="/",
                             text=[f"{(c2 - s) * 100:+.0f} pp" for s, c2 in zip(d["sin"], d["con"])], textposition="outside"))
        layout(fig, 360).update_layout(barmode="group").update_xaxes(title="Recompra a 30 días (%)", range=[0, 85])
        st.plotly_chart(fig, width="stretch", key="fac")
        st.caption("Pedidos con 30 días de seguimiento (01-jul a 31-ago). Diferencia en puntos porcentuales.")


# ======================================================================== 5. CALIDAD Y MÉTODO
def vista_metodo():
    st.markdown("## Calidad de datos y método")
    c = st.columns(2)
    with c[0]:
        st.markdown("#### Auditoría de calidad (Fase 1)")
        if res["calidad_tablas"] is not None:
            st.dataframe(res["calidad_tablas"], hide_index=True, width="stretch")
        if res["calidad_controles"] is not None:
            st.dataframe(res["calidad_controles"], hide_index=True, width="stretch")
    with c[1]:
        st.markdown("#### Diccionario de KPIs unificados (T5)")
        st.dataframe(pd.DataFrame([
            ["Clientes activos", "Clientes distintos con ≥ 1 pedido en el período", "pedidos.csv", "Diaria", "Crecer vs mes anterior", "Marketing"],
            ["Pedidos", "N° de pedidos entregados en el mes", "pedidos.csv", "Diaria", "Mantener o crecer", "Logística / despachos"],
            ["Ventas", "Σ (monto productos + cargo de servicio)", "pedidos.csv", "Diaria", "Nivel de julio", "Marketing / finanzas"],
            ["Reclamos por 100 pedidos", "Reclamos ÷ pedidos × 100", "reclamos.csv + pedidos.csv", "Diaria", f"≤ {num(cfg.META_RECLAMOS_100)}", "Soporte al cliente"],
            ["Pedidos atrasados", "Pedidos fuera de la ventana de 45 min ÷ pedidos", "pedidos.csv", "Tiempo real / diaria", "≤ 12 %", "Operaciones"],
            ["p90 de entrega", "Percentil 90 del tiempo de entrega", "pedidos.csv", "Diaria", "< 60 min", "Operaciones"],
        ], columns=["KPI", "Fórmula", "Fuente", "Frecuencia", "Meta", "Responsable"]), hide_index=True, width="stretch")
        st.markdown("""
**Clientes activos unificado.** Conviven tres cifras: 412.000 cuentas históricas (D1), 148.000 con medio de pago válido (D3)
y 61.300 con pedido en los últimos 30 días (D2). El dashboard usa una sola definición: **clientes con al menos un pedido en el período**.

**Supuestos y límites**
- *Atrasado* = la marca de la fuente (entrega fuera de la ventana de 45 min).
- *Congelado fuera de temperatura* = llega sobre −15 °C (corte natural en los datos).
- *Recompra a 30 días* solo para pedidos con 30 días de seguimiento (hasta el 31-ago); septiembre queda censurado.
- Los CSV no traen comunas ni visitas a la app: el filtro geográfico es por ciudad y bodega, y las visitas vienen del Anexo.
- Los CSV del grupo son una muestra distinta del Anexo (193.419 pedidos vs 180.000): las cifras difieren, pero los hallazgos se mantienen.
""")


# ======================================================================== render
{"Vista estratégica": vista_estrategica, "Vista operativa": vista_operativa, "Auditoría del memo (A1–A6)": vista_auditoria,
 "Fuga de clientes": vista_fuga, "Calidad de datos y método": vista_metodo}[pagina]()
st.markdown("<hr><div class='pie'>EP3 · ADY1104 Visualización de Datos · Duoc UC · Grupo 11 (Claudio Aro, Guillermo Cerda, Manuel Díaz) · Fuente: CSV RapiMarket Q3 2026 y Anexo oficial.</div>",
            unsafe_allow_html=True)
