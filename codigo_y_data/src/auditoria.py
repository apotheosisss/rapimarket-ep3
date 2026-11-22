"""Fase 2 · EDA de auditoría y validación numérica.

- Recalcula las 6 afirmaciones del Memo de Marketing (A1-A6) con los CSV del grupo y las contrasta con el Anexo.
- Desarma la Paradoja de Simpson de Bodega Centro vs Norte.
- Reentrena un Random Forest de fuga para verificar la Tabla E (importancia de variables y AUC).
- Genera las figuras estáticas del informe y la presentación.

Requiere haber ejecutado antes:  python -m src.pipeline
Ejecutar desde codigo_y_data:    python -m src.auditoria
"""
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from src import config as cfg
from src.pipeline import p90

C = cfg.COL
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": C["gris"], "axes.labelcolor": C["tinta"],
                     "xtick.color": C["gris_txt"], "ytick.color": C["gris_txt"], "axes.titleweight": "bold",
                     "axes.titlesize": 11.5, "axes.titlelocation": "left", "figure.dpi": 110})


def cargar() -> pd.DataFrame:
    return pd.read_csv(cfg.DIR_PROC / "pedidos_integrados.csv.gz", parse_dates=["fecha", "fecha_siguiente", "semana"])


def pct(x, d=1):
    return f"{x * 100:.{d}f} %".replace(".", ",")


def miles(x):
    return f"{x:,.0f}".replace(",", ".")


# ====================================================================== A1-A6
def recalculos(df: pd.DataFrame) -> tuple:
    A = cfg.ANEXO
    n_ped, n_rec = len(df), int(df["n_reclamos"].sum())
    men = df.groupby("mes").agg(pedidos=("pedido_id", "size"), ticket_prod=("monto_productos_clp", "mean"),
                                ticket_total=("ticket_total_clp", "mean"), cargo=("cargo_servicio_clp", "mean"),
                                clientes=("cliente_id", "nunique"))
    ciudad = df.groupby("ciudad_bodega").agg(pedidos=("pedido_id", "size"), atraso=("atrasado", "mean"),
                                             p90=("tiempo_entrega_min", p90))
    ciudad["share"] = ciudad["pedidos"] / n_ped
    stgo = df[df["ciudad_bodega"] == "Santiago"]
    simpson = (stgo.groupby(["bodega", "tipo_pedido"]).agg(pedidos=("pedido_id", "size"), atrasados=("atrasado", "sum"))
               .assign(tasa=lambda d: d.atrasados / d.pedidos).reset_index())
    agg_b = stgo.groupby("bodega").agg(pedidos=("pedido_id", "size"), atrasados=("atrasado", "sum"))
    agg_b["tasa"] = agg_b.atrasados / agg_b.pedidos
    agg_b["pct_complejos"] = stgo.groupby("bodega")["complejo"].mean()

    obs = df[df["recompra_30d"].notna()]
    a5 = obs.groupby(["atrasado", "calif_grupo"], observed=True)["recompra_30d"].mean().unstack()
    rec_atraso = obs.groupby("atrasado")["recompra_30d"].mean()
    cal = df["estrellas"].dropna()
    un_pedido = (df.groupby("cliente_id").size() == 1).mean()

    def S(b, t):
        return simpson.set_index(["bodega", "tipo_pedido"]).loc[(b, t), "tasa"]

    filas = [
        dict(afirmacion="A1", tema="Calidad de servicio",
             dice_memo="1,2 % de reclamos (25.200 / 2.100.000 visitas)",
             tipo_error="Denominador incorrecto",
             recalculo_anexo=f"25.200 / 180.000 pedidos = {pct(A['reclamos_q3'] / A['pedidos_q3'])}",
             recalculo_csv=f"{miles(n_rec)} / {miles(n_ped)} pedidos = {pct(n_rec / n_ped)}",
             lectura_correcta="Los reclamos se miden sobre pedidos, no sobre visitas: 1 de cada 7 pedidos termina en reclamo.",
             decision_erronea="Concluir que el servicio es excelente y no invertir en calidad operativa."),
        dict(afirmacion="A2", tema="Crecimiento",
             dice_memo="Pedidos acumulados > 3,3 M y ticket en fuerte alza ($41.200 en sep.)",
             tipo_error="Acumulado + cambio de definición",
             recalculo_anexo="Pedidos mensuales 62.000 → 60.000 → 58.000 (−6,5 %); el acumulado sube aunque cada mes se vende menos.",
             recalculo_csv=(f"Pedidos {miles(men.loc[7, 'pedidos'])} → {miles(men.loc[8, 'pedidos'])} → {miles(men.loc[9, 'pedidos'])} "
                            f"({pct(men.loc[9, 'pedidos'] / men.loc[7, 'pedidos'] - 1)}). Ticket de productos plano "
                            f"(${miles(men.loc[7, 'ticket_prod'])} → ${miles(men.loc[9, 'ticket_prod'])}); el alza viene del cargo de servicio de $1.990 desde agosto."),
             lectura_correcta="El negocio se contrae mes a mes; el ticket sube por un cargo nuevo, no porque los clientes compren más.",
             decision_erronea="Creer que hay crecimiento y premiarlo con cupones."),
        dict(afirmacion="A3", tema="Concentración",
             dice_memo="Santiago es la mejor ciudad: concentra el 55 % de los pedidos",
             tipo_error="Volumen confundido con desempeño",
             recalculo_anexo="Santiago: 24,0 % de atraso y p90 de 78 min (meta < 60), el peor de las 5 ciudades.",
             recalculo_csv=(f"Santiago: {pct(ciudad.loc['Santiago', 'share'])} de los pedidos, {pct(ciudad.loc['Santiago', 'atraso'])} de atraso "
                            f"(resto: {pct(df.loc[df.ciudad_bodega != 'Santiago', 'atrasado'].mean())}) y p90 de {ciudad.loc['Santiago', 'p90']:.0f} min."),
             lectura_correcta="Santiago concentra volumen, pero es la ciudad con peor tasa de atraso y la única fuera de la meta de p90.",
             decision_erronea="No invertir en la operación de Santiago, que es donde está el problema."),
        dict(afirmacion="A4", tema="Desempeño de bodegas",
             dice_memo="Centro es la peor de Santiago (22,0 % vs 15,6 % de Norte); cerrarla",
             tipo_error="Paradoja de Simpson",
             recalculo_anexo="Por tipo, Centro atrasa menos: complejos 25 % vs 30 % y simples 10 % vs 12 %. Centro atiende 80 % de pedidos complejos; Norte, 20 %.",
             recalculo_csv=(f"Total: Centro {pct(agg_b.loc['Centro', 'tasa'])} vs Norte {pct(agg_b.loc['Norte', 'tasa'])}. "
                            f"Complejos: Centro {pct(S('Centro', 'Complejo'))} vs Norte {pct(S('Norte', 'Complejo'))}; "
                            f"simples: {pct(S('Centro', 'Simple'))} vs {pct(S('Norte', 'Simple'))}. "
                            f"Sur (externo): {pct(agg_b.loc['Sur', 'tasa'])}."),
             lectura_correcta="Centro no es la peor: atiende más pedidos complejos. Dentro de cada tipo es la mejor. La peor es Sur, que el dashboard omitía.",
             decision_erronea="Cerrar la bodega más eficiente y derivar sus pedidos complejos a Norte, que los atiende peor."),
        dict(afirmacion="A5", tema="Fidelización",
             dice_memo="El problema es la calidad de los productos: quien califica 1-2★ no vuelve",
             tipo_error="Causalidad incorrecta (variable de confusión)",
             recalculo_anexo="Tabla D: dentro de cada segmento (atrasado / a tiempo), 1-2★ y 4-5★ difieren en menos de 3 pp de recompra.",
             recalculo_csv=(f"Recompra a 30 días: a tiempo {pct(rec_atraso.loc[False])} vs atrasado {pct(rec_atraso.loc[True])}. "
                            f"Dentro de 'a tiempo': 1-2★ {pct(a5.loc[False, '1-2'])} vs 4-5★ {pct(a5.loc[False, '4-5'])}."),
             lectura_correcta="Lo que explica la fuga es el atraso; la mala calificación es un síntoma del atraso, no la causa.",
             decision_erronea="Invertir en catálogo y calidad de producto en vez de en la entrega."),
        dict(afirmacion="A6", tema="Satisfacción",
             dice_memo="Clientes altamente felices: encuesta 4,6 / 5",
             tipo_error="Sesgo de supervivencia / selección",
             recalculo_anexo="4.100 respuestas, enviadas solo al confirmar el 2.º pedido: excluye a quienes se fueron tras el 1.º.",
             recalculo_csv=(f"Calificación de {miles(len(cal))} pedidos: promedio {cal.mean():.2f}".replace(f"{cal.mean():.2f}", f"{cal.mean():.2f}".replace(".", ","))
                            + f" / 5 y {pct((cal <= 2).mean())} con 1-2★. "
                            f"El {pct(un_pedido)} de los clientes hizo un solo pedido en el trimestre."),
             lectura_correcta="El 4,6 representa solo a clientes retenidos; la calificación de todos los pedidos es 3,1.",
             decision_erronea="Dar por resuelta la satisfacción con una muestra que oculta a quienes se fueron."),
    ]
    extras = dict(men=men, ciudad=ciudad, simpson=simpson, agg_b=agg_b, a5=a5, rec_atraso=rec_atraso,
                  un_pedido=un_pedido, n_ped=n_ped, n_rec=n_rec, cal=cal)
    return pd.DataFrame(filas), extras


# ====================================================================== Random Forest
VARS_TABLA_E = {"atrasado": "Pedido atrasado", "faltantes": "Productos faltantes o sustituidos",
                "frio_roto": "Congelados fuera de temperatura", "reclamo_tardio": "Reclamo sin respuesta > 24 h",
                "con_cupon": "Uso de cupón de descuento", "estrellas": "Calificación del pedido",
                "ciudad": "Ciudad de origen"}
TABLA_E = {"Pedido atrasado": 31, "Productos faltantes o sustituidos": 24, "Congelados fuera de temperatura": 17,
           "Reclamo sin respuesta > 24 h": 12, "Uso de cupón de descuento": 8, "Calificación del pedido": 5,
           "Ciudad de origen": 3}


def modelo_fuga(df: pd.DataFrame, semilla: int = 42) -> tuple:
    """Random Forest para 'no recompra a 30 días'. Importancia por permutación (caída de AUC en prueba)."""
    d = df[df["recompra_30d"].notna()].copy()
    X = pd.DataFrame({
        "atrasado": d["atrasado"].astype(int),
        "faltantes": d["faltantes"].astype(int),
        "frio_roto": d["frio_roto"].astype(int),
        "reclamo_tardio": d["reclamo_tardio"].fillna(False).astype(int),
        "con_cupon": d["con_cupon"].astype(int),
        "estrellas": d["estrellas"].fillna(0),          # 0 = pedido sin calificación
        "ciudad": d["ciudad_bodega"].astype("category").cat.codes,
    })
    y = (d["recompra_30d"] == 0).astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=semilla, stratify=y)
    rf = RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=50, n_jobs=-1,
                                random_state=semilla, class_weight="balanced")
    rf.fit(Xtr, ytr)
    auc = roc_auc_score(yte, rf.predict_proba(Xte)[:, 1])
    perm = permutation_importance(rf, Xte, yte, scoring="roc_auc", n_repeats=5, random_state=semilla, n_jobs=-1)
    imp = pd.DataFrame({"variable": [VARS_TABLA_E[c] for c in X.columns],
                        "importancia_permutacion": perm.importances_mean.clip(min=0),
                        "importancia_gini": rf.feature_importances_})
    imp["importancia_csv_pct"] = imp["importancia_permutacion"] / imp["importancia_permutacion"].sum() * 100
    imp["importancia_tabla_e_pct"] = imp["variable"].map(TABLA_E)
    imp = imp.sort_values("importancia_csv_pct", ascending=False)
    meta = {"auc_prueba": round(float(auc), 4), "auc_anexo": 0.81, "n_entrenamiento": int(len(Xtr)),
            "n_prueba": int(len(Xte)), "tasa_no_recompra": round(float(y.mean()), 4),
            "objetivo": "No recompra a 30 días (pedidos con 30 días de seguimiento: 01-jul a 31-ago)"}
    return imp, meta


# ====================================================================== figuras
def _guardar(fig, nombre):
    cfg.DIR_FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(cfg.DIR_FIG / nombre, dpi=200, bbox_inches="tight")
    plt.close(fig)


def figuras(df, ex, imp):
    # A2 · pedidos mensuales y ticket descompuesto
    men = ex["men"]
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.2))
    x = [cfg.MESES[m][:3] for m in men.index]
    ax[0].bar(x, men["pedidos"], color=[C["gris"], C["gris"], C["alerta"]], width=0.6)
    for i, v in enumerate(men["pedidos"]):
        ax[0].text(i, v + 1500, miles(v), ha="center", fontsize=9, color=C["tinta"], fontweight="bold")
    ax[0].set_title("Pedidos por mes: el negocio se contrae")
    ax[0].set_yticks([]); ax[0].spines["left"].set_visible(False)
    ax[1].bar(x, men["ticket_prod"], color=C["ok"], width=0.6, label="Productos")
    ax[1].bar(x, men["cargo"], bottom=men["ticket_prod"], color=C["alerta"], width=0.6, label="Cargo de servicio")
    for i, (a, b) in enumerate(zip(men["ticket_prod"], men["cargo"])):
        ax[1].text(i, a + b + 400, f"${miles(a + b)}", ha="center", fontsize=9, color=C["tinta"], fontweight="bold")
    ax[1].set_title("Ticket promedio: el alza es el cargo nuevo")
    ax[1].set_yticks([]); ax[1].spines["left"].set_visible(False)
    ax[1].legend(frameon=False, fontsize=8.5, loc="lower right")
    ax[1].set_ylim(0, 46000)
    _guardar(fig, "fig_A2_pedidos_ticket.png")

    # A3 · volumen vs tasa por ciudad
    ci = ex["ciudad"].sort_values("pedidos", ascending=False)
    fig, ax1 = plt.subplots(figsize=(6.4, 3.2))
    cols = [C["alerta"] if c == "Santiago" else C["gris"] for c in ci.index]
    ax1.bar(ci.index, ci["pedidos"], color=cols, width=0.6)
    ax1.set_ylabel("Pedidos Q3")
    ax2 = ax1.twinx()
    ax2.plot(ci.index, ci["atraso"] * 100, "o-", color=C["tinta"], lw=1.6)
    for i, v in enumerate(ci["atraso"]):
        ax2.text(i, v * 100 + 1.4, pct(v), ha="center", fontsize=8.5, color=C["tinta"], fontweight="bold")
    ax2.set_ylim(0, 30); ax2.set_ylabel("% de pedidos atrasados (línea)")
    ax2.spines["right"].set_visible(True)
    ax1.set_title("Santiago: más volumen y también más atraso")
    _guardar(fig, "fig_A3_volumen_vs_tasa.png")

    # A4 · Simpson
    s = ex["simpson"].pivot(index="bodega", columns="tipo_pedido", values="tasa").loc[["Centro", "Norte", "Sur"]]
    ab = ex["agg_b"].loc[["Centro", "Norte", "Sur"]]
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.2), gridspec_kw={"width_ratios": [1, 1.6]})
    ax[0].bar(ab.index, ab["tasa"] * 100, color=[C["marca"], C["ok"], C["alerta"]], width=0.6)
    for i, v in enumerate(ab["tasa"]):
        ax[0].text(i, v * 100 + 0.8, pct(v), ha="center", fontsize=9, fontweight="bold", color=C["tinta"])
    ax[0].set_title("Lo que muestra el memo (total)"); ax[0].set_ylim(0, 52); ax[0].set_ylabel("% atrasados")
    w = 0.38; idx = np.arange(3)
    ax[1].bar(idx - w / 2, s["Simple"] * 100, w, color=C["gris"], label="Simple")
    ax[1].bar(idx + w / 2, s["Complejo"] * 100, w, color=C["alerta"], label="Complejo")
    for i in idx:
        ax[1].text(i - w / 2, s["Simple"].iloc[i] * 100 + 0.8, pct(s["Simple"].iloc[i]), ha="center", fontsize=8.5)
        ax[1].text(i + w / 2, s["Complejo"].iloc[i] * 100 + 0.8, pct(s["Complejo"].iloc[i]), ha="center", fontsize=8.5, fontweight="bold")
    ax[1].set_xticks(idx, [f"{b}\n({pct(ab.loc[b, 'pct_complejos'], 0)} complejos)" for b in s.index])
    ax[1].set_title("Separado por tipo de pedido: Centro es la mejor"); ax[1].set_ylim(0, 52)
    ax[1].legend(frameon=False, fontsize=8.5)
    _guardar(fig, "fig_A4_simpson.png")

    # A5 · recompra por atraso y calificación
    a5 = ex["a5"]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    grupos = ["1-2", "3", "4-5"]; idx = np.arange(3); w = 0.38
    ax.bar(idx - w / 2, a5.loc[False, grupos] * 100, w, color=C["ok"], label="Entregado a tiempo")
    ax.bar(idx + w / 2, a5.loc[True, grupos] * 100, w, color=C["alerta"], label="Atrasado")
    for i, g in enumerate(grupos):
        ax.text(i - w / 2, a5.loc[False, g] * 100 + 1, pct(a5.loc[False, g], 0), ha="center", fontsize=8.5)
        ax.text(i + w / 2, a5.loc[True, g] * 100 + 1, pct(a5.loc[True, g], 0), ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(idx, [f"{g} ★" for g in grupos]); ax.set_ylim(0, 80); ax.set_ylabel("Recompra a 30 días")
    ax.set_title("La recompra depende del atraso, no de la calificación")
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", ncol=2)
    _guardar(fig, "fig_A5_recompra.png")

    # Random Forest vs Tabla E
    im = imp.sort_values("importancia_tabla_e_pct")
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    y = np.arange(len(im)); h = 0.38
    ax.barh(y + h / 2, im["importancia_tabla_e_pct"], h, color=C["gris"], label="Tabla E (Anexo)")
    ax.barh(y - h / 2, im["importancia_csv_pct"], h, color=C["marca"], label="Recalculado con CSV")
    for i, v in enumerate(im["importancia_csv_pct"]):
        ax.text(v + 0.6, i - h / 2, f"{v:.0f} %", va="center", fontsize=8.5, color=C["tinta"])
    ax.set_yticks(y, im["variable"]); ax.set_xlabel("Importancia relativa (%)")
    ax.set_title("¿Qué predice la fuga? Operación > cupones")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    _guardar(fig, "fig_RF_importancia.png")

    # Clientes activos: tres definiciones
    A = cfg.ANEXO
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    defs = [("Cuentas históricas (D1)", A["cuentas_historicas"], C["gris"]),
            ("Con medio de pago válido (D3)", A["clientes_medio_pago"], C["gris"]),
            ("Activos últimos 30 días (D2)", A["clientes_activos_30d"], C["marca"])]
    for i, (l, v, c) in enumerate(defs):
        ax.barh(i, v, color=c, height=0.6)
        ax.text(v + 6000, i, miles(v), va="center", fontsize=9, fontweight="bold", color=C["tinta"])
    ax.set_yticks(range(3), [d[0] for d in defs]); ax.invert_yaxis(); ax.set_xticks([])
    ax.spines["bottom"].set_visible(False); ax.set_xlim(0, 470000)
    ax.set_title("Tres 'clientes activos' distintos (Anexo)")
    _guardar(fig, "fig_clientes_activos.png")


def main():
    cfg.DIR_RES.mkdir(parents=True, exist_ok=True)
    df = cargar()
    aud, ex = recalculos(df)
    aud.to_csv(cfg.DIR_RES / "auditoria_A1_A6.csv", index=False, encoding="utf-8-sig")
    ex["simpson"].to_csv(cfg.DIR_RES / "simpson_bodega_tipo.csv", index=False)
    imp, meta = modelo_fuga(df)
    imp.to_csv(cfg.DIR_RES / "importancia_random_forest.csv", index=False)
    (cfg.DIR_RES / "modelo_fuga.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    figuras(df, ex, imp)
    print(aud[["afirmacion", "tipo_error", "recalculo_csv"]].to_string(index=False))
    print("\nRandom Forest:", meta)
    print(imp.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
