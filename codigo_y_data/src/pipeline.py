"""Fase 1 · Integración y data pipeline.

1. Carga los 6 CSV de RapiMarket y audita su calidad (tipos, nulos, duplicados, llaves huérfanas, outliers).
2. Une las tablas por cliente_id, pedido_id y bodega.
3. Calcula las variables derivadas que usan la auditoría y el dashboard.
4. Guarda la tabla integrada y los indicadores mensuales en data/processed.

Ejecutar desde la carpeta codigo_y_data:  python -m src.pipeline
"""
import pandas as pd
import numpy as np

from src import config as cfg


def cargar_raw() -> dict:
    """Lee los CSV originales sin modificarlos."""
    t = {n: pd.read_csv(cfg.DIR_RAW / f"{n}.csv") for n in cfg.ARCHIVOS_RAW}
    t["pedidos"]["fecha"] = pd.to_datetime(t["pedidos"]["fecha"])
    t["reclamos"]["fecha"] = pd.to_datetime(t["reclamos"]["fecha"])
    t["clientes"]["fecha_registro"] = pd.to_datetime(t["clientes"]["fecha_registro"])
    return t


def _outliers_iqr(s: pd.Series) -> int:
    q1, q3 = s.quantile([0.25, 0.75])
    lim = q3 + 1.5 * (q3 - q1)
    return int((s > lim).sum())


def auditar_calidad(t: dict) -> tuple:
    """Reporte de calidad por tabla: filas, nulos, duplicados de llave y llaves huérfanas."""
    llaves = {"clientes": "cliente_id", "bodegas": "bodega", "pedidos": "pedido_id",
              "reclamos": "reclamo_id", "calificaciones": "pedido_id", "cupones": "pedido_id"}
    ped = set(t["pedidos"]["pedido_id"])
    filas = []
    for n, df in t.items():
        huerfanas = 0
        if n in ("reclamos", "calificaciones", "cupones"):
            huerfanas = int((~df["pedido_id"].isin(ped)).sum())
        if n == "pedidos":
            huerfanas = int((~df["cliente_id"].isin(t["clientes"]["cliente_id"])).sum()
                            + (~df["bodega"].isin(t["bodegas"]["bodega"])).sum())
        filas.append({"tabla": n, "filas": len(df), "columnas": df.shape[1],
                      "nulos": int(df.isna().sum().sum()),
                      "duplicados_llave": int(df[llaves[n]].duplicated().sum()),
                      "filas_duplicadas": int(df.duplicated().sum()),
                      "llaves_huerfanas": huerfanas})
    rep = pd.DataFrame(filas)
    p = t["pedidos"]
    extra = pd.DataFrame([
        {"tabla": "pedidos", "control": "nulos en temp_llegada_c",
         "valor": int(p["temp_llegada_c"].isna().sum()),
         "tratamiento": "Esperado: solo los pedidos con congelados registran temperatura. Nulos en pedidos con congelados: "
                        f"{int(p.loc[p.con_congelados, 'temp_llegada_c'].isna().sum())}."},
        {"tabla": "pedidos", "control": "outliers tiempo_entrega_min (IQR)", "valor": _outliers_iqr(p["tiempo_entrega_min"]),
         "tratamiento": "Se conservan: son entregas lentas reales y son justamente el problema a medir. Se reportan p90 y mediana, robustos a extremos."},
        {"tabla": "pedidos", "control": "outliers monto_productos_clp (IQR)", "valor": _outliers_iqr(p["monto_productos_clp"]),
         "tratamiento": "Se conservan: compras grandes plausibles (hasta 76 productos). El ticket se informa con promedio y mediana."},
        {"tabla": "pedidos", "control": "atrasado coherente con tiempo > ventana",
         "valor": round(float((p["atrasado"] == (p["tiempo_entrega_min"] > p["ventana_min"])).mean()) * 100, 2),
         "tratamiento": "% de coincidencia. Se usa la marca 'atrasado' de la fuente (entrega fuera de la ventana de 45 min)."},
        {"tabla": "reclamos", "control": "outliers horas_respuesta (IQR)", "valor": _outliers_iqr(t["reclamos"]["horas_respuesta"]),
         "tratamiento": "Se conservan: las respuestas tardías son el indicador 'reclamo sin respuesta > 24 h'."},
    ])
    return rep, extra


def integrar(t: dict) -> pd.DataFrame:
    """Une las 6 tablas a nivel de pedido y calcula variables derivadas."""
    p = t["pedidos"].drop_duplicates("pedido_id").copy()
    b = t["bodegas"].rename(columns={"ciudad": "ciudad_bodega"})
    c = t["clientes"]
    p = (p.merge(c, on="cliente_id", how="left", validate="many_to_one")
          .merge(b, on="bodega", how="left", validate="many_to_one"))

    rec = t["reclamos"].groupby("pedido_id").agg(n_reclamos=("reclamo_id", "size"),
                                                 categoria_reclamo=("categoria", "first"),
                                                 horas_respuesta=("horas_respuesta", "max"))
    p = p.merge(rec, on="pedido_id", how="left")
    p = p.merge(t["calificaciones"], on="pedido_id", how="left", validate="one_to_one")
    p = p.merge(t["cupones"], on="pedido_id", how="left", validate="one_to_one")

    p["n_reclamos"] = p["n_reclamos"].fillna(0).astype(int)
    p["con_reclamo"] = p["n_reclamos"] > 0
    p["reclamo_tardio"] = p["horas_respuesta"] > cfg.UMBRAL_RESPUESTA_RECLAMO_H
    p["con_cupon"] = p["descuento_pct"].notna()
    p["frio_roto"] = p["con_congelados"] & (p["temp_llegada_c"] > cfg.UMBRAL_FRIO_C)
    p["retraso_grave"] = p["tiempo_entrega_min"] > cfg.UMBRAL_RETRASO_GRAVE_MIN
    p["tipo_pedido"] = np.where(p["complejo"], "Complejo", "Simple")
    p["ticket_total_clp"] = p["monto_productos_clp"] + p["cargo_servicio_clp"]
    p["mes"] = p["fecha"].dt.month
    p["semana"] = p["fecha"].dt.to_period("W-SUN").dt.start_time
    p["calif_grupo"] = pd.cut(p["estrellas"], [0, 2, 3, 5], labels=["1-2", "3", "4-5"])

    # Recompra a 30 días: el cliente vuelve a pedir dentro de 30 días. Solo es observable para pedidos
    # con al menos 30 días de seguimiento (hasta el 31-ago); el resto queda censurado (NaN).
    p = p.sort_values(["cliente_id", "fecha", "pedido_id"])
    p["fecha_siguiente"] = p.groupby("cliente_id")["fecha"].shift(-1)
    dias = (p["fecha_siguiente"] - p["fecha"]).dt.days
    corte = p["fecha"].max() - pd.Timedelta(days=cfg.VENTANA_RECOMPRA_DIAS)
    p["recompra_30d"] = np.where(p["fecha"] <= corte, (dias <= cfg.VENTANA_RECOMPRA_DIAS).astype(float), np.nan)
    p["n_pedido_cliente"] = p.groupby("cliente_id").cumcount() + 1
    return p.sort_values("pedido_id").reset_index(drop=True)


def p90(s):
    return float(np.percentile(s, 90)) if len(s) else np.nan


def kpis(df: pd.DataFrame, por) -> pd.DataFrame:
    """Indicadores de negocio agregados por la(s) columna(s) indicada(s)."""
    g = df.groupby(por, observed=True)
    out = g.agg(pedidos=("pedido_id", "size"),
                clientes_activos=("cliente_id", "nunique"),
                atrasados=("atrasado", "sum"),
                tasa_atraso=("atrasado", "mean"),
                retraso_grave=("retraso_grave", "mean"),
                mediana_min=("tiempo_entrega_min", "median"),
                p90_min=("tiempo_entrega_min", p90),
                reclamos=("n_reclamos", "sum"),
                ventas_clp=("ticket_total_clp", "sum"),
                ticket_productos=("monto_productos_clp", "mean"),
                ticket_total=("ticket_total_clp", "mean"),
                faltantes=("faltantes", "mean"),
                recompra_30d=("recompra_30d", "mean"),
                uso_cupon=("con_cupon", "mean"))
    out["reclamos_100"] = out["reclamos"] / out["pedidos"] * 100
    frio = df[df["con_congelados"]].groupby(por, observed=True)["frio_roto"].mean().rename("frio_roto")
    tard = df[df["con_reclamo"]].groupby(por, observed=True)["reclamo_tardio"].mean().rename("reclamo_tardio")
    return out.join(frio).join(tard).reset_index()


def peor_bodega_p90(df: pd.DataFrame) -> pd.Series:
    """Bodega de Santiago con mayor p90 de entrega en cada mes (columna del wireframe)."""
    stgo = df[df["ciudad_bodega"] == "Santiago"]
    t = stgo.groupby(["mes", "bodega"])["tiempo_entrega_min"].apply(p90).reset_index()
    return t.loc[t.groupby("mes")["tiempo_entrega_min"].idxmax()].set_index("mes")["bodega"]


def main():
    cfg.DIR_PROC.mkdir(parents=True, exist_ok=True)
    cfg.DIR_RES.mkdir(parents=True, exist_ok=True)
    t = cargar_raw()
    rep, extra = auditar_calidad(t)
    rep.to_csv(cfg.DIR_RES / "calidad_tablas.csv", index=False)
    extra.to_csv(cfg.DIR_RES / "calidad_controles.csv", index=False)

    df = integrar(t)
    df.to_csv(cfg.DIR_PROC / "pedidos_integrados.csv.gz", index=False, compression="gzip")

    mens = kpis(df, "mes")
    mens["peor_bodega_p90"] = mens["mes"].map(peor_bodega_p90(df))
    mens["visitas_app_anexo"] = cfg.ANEXO["visitas_app_mes"]
    mens.to_csv(cfg.DIR_PROC / "kpis_mensuales.csv", index=False)
    kpis(df, ["ciudad_bodega"]).to_csv(cfg.DIR_PROC / "kpis_ciudad.csv", index=False)
    kpis(df, ["bodega", "tipo_pedido"]).to_csv(cfg.DIR_PROC / "kpis_bodega_tipo.csv", index=False)

    print("Calidad de tablas:\n", rep.to_string(index=False))
    print(f"\nTabla integrada: {len(df):,} pedidos x {df.shape[1]} columnas -> data/processed/pedidos_integrados.csv.gz")
    print(mens[["mes", "pedidos", "tasa_atraso", "p90_min", "reclamos_100", "recompra_30d", "peor_bodega_p90"]].to_string(index=False))


if __name__ == "__main__":
    main()
