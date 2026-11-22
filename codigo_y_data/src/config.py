"""Configuración común: rutas relativas al proyecto, umbrales de negocio, metas y paleta.

Todas las rutas se construyen a partir de la ubicación de este archivo, para que el
proyecto se ejecute igual en cualquier computador (sin rutas absolutas locales).
"""
from pathlib import Path

# ------------------------------------------------------------------ rutas
RAIZ_CODIGO = Path(__file__).resolve().parents[1]          # .../codigo_y_data
RAIZ_PROYECTO = RAIZ_CODIGO.parent                          # .../EP3_GrupoXX_RapiMarket
DIR_RAW = RAIZ_CODIGO / "data" / "raw"
DIR_PROC = RAIZ_CODIGO / "data" / "processed"
DIR_RES = RAIZ_CODIGO / "resultados"
DIR_FIG = RAIZ_CODIGO / "figuras"

ARCHIVOS_RAW = ["clientes", "bodegas", "pedidos", "reclamos", "calificaciones", "cupones"]

# ------------------------------------------------------------------ reglas de negocio
# Un congelado está "fuera de temperatura" si llega sobre -15 °C. Los datos muestran un corte
# natural entre -15 °C y -10 °C (ningún pedido entre esos valores).
UMBRAL_FRIO_C = -15.0
UMBRAL_RETRASO_GRAVE_MIN = 60        # retraso grave: entrega sobre 60 minutos
UMBRAL_RESPUESTA_RECLAMO_H = 24      # reclamo sin respuesta en más de 24 horas
VENTANA_RECOMPRA_DIAS = 30           # recompra: el cliente vuelve a pedir dentro de 30 días

# ------------------------------------------------------------------ metas (de la Parte 1 y el Anexo)
META_P90_MIN = 60          # Tabla B: p90 de entrega < 60 min
META_RECOMPRA = 0.41       # T6: volver al 41 % de recompra a 30 días (nivel de julio)
META_ATRASO = 0.12         # referencia: tasa de atraso de las ciudades sin problemas (Tabla B)
META_RECLAMOS_100 = 12.6   # referencia: reclamos por cada 100 pedidos de julio en el Anexo (7.800 / 62.000)

# ------------------------------------------------------------------ datos que no vienen en los CSV (Anexo oficial)
ANEXO = {
    "visitas_app_mes": 700_000,
    "visitas_app_q3": 2_100_000,
    "reclamos_q3": 25_200,
    "pedidos_q3": 180_000,
    "cuentas_historicas": 412_000,
    "clientes_medio_pago": 148_000,
    "clientes_activos_30d": 61_300,
    "encuesta_respuestas": 4_100,
    "encuesta_nota": 4.6,
    "acumulado_jun": 3_160_000,
    "acumulado_sep": 3_340_000,
}

# ------------------------------------------------------------------ paleta (segura para daltonismo, WCAG 2.1)
# Azul = cumple / referencia; naranja = alerta / bajo meta; gris = contexto. Contrastes sobre blanco:
# MARCA 11,6:1 · OK 5,4:1 · ALERTA_TXT 5,8:1 · TINTA 15,8:1 · GRIS_TXT 5,4:1 (texto >= 4,5:1).
COL = {
    "marca": "#1B3A5C",
    "ok": "#2B6CB0",
    "alerta": "#D9630B",
    "alerta_txt": "#A8480A",
    "tinta": "#1F2328",
    "gris_txt": "#5F6B7A",
    "gris": "#A7B1BC",
    "borde": "#DCE2E8",
    "fondo": "#F5F7FA",
}
SEQ_NARANJA = ["#FFF4E8", "#FDD2A6", "#F9A25A", "#E3711F", "#A8480A"]
COL_BODEGA = {"Centro": "#1B3A5C", "Norte": "#2B6CB0", "Sur": "#D9630B"}
MESES = {7: "Julio", 8: "Agosto", 9: "Septiembre"}
