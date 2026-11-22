# RapiMarket Q3 2026 · Front-end analítico para el Comité Ejecutivo

**Evaluación Parcial N° 3 · Parte 2 (encargo grupal) · ADY1104 Visualización de Datos · Duoc UC**
Grupo 11 · Integrantes: Claudio Aro, Guillermo Cerda, Manuel Díaz · Docente: Claudio Andrés Gonzalez Peñaloza

Solución que transforma el diagnóstico y el wireframe hechos a mano en la Parte 1 en un dashboard interactivo,
con pipeline de datos reproducible, auditoría numérica del Memo de Marketing y una recomendación ejecutiva
bajo la Pirámide de Minto.

> **Recomendación:** destinar los USD 3.000.000 a la operación (última milla, control de stock, cadena de frío y
> respuesta a reclamos) y nada a cupones. La fuga de clientes la explica la entrega, no la falta de descuentos.

## Estructura de la carpeta

```
EP3_Grupo11_RapiMarket/
├── README.md                     <- este archivo
├── DECLARACION_IA.md             <- reporte obligatorio del uso ético de IA
├── requirements.txt              <- dependencias de Python
├── .streamlit/config.toml        <- tema visual del dashboard
├── informes/
│   ├── Informe_Ejecutivo_RapiMarket.pdf        <- 4 páginas: diagnóstico, A1-A6, Simpson, propuesta Minto
│   └── fuente/                                  <- HTML generado (fuente del PDF)
├── dashboard/
│   ├── app.py                    <- dashboard interactivo (Streamlit + Plotly), 5 páginas
│   ├── requirements.txt          <- dependencias mínimas del dashboard (Streamlit Cloud)
│   └── capturas/                 <- capturas de las 5 páginas
├── presentacion/
│   ├── Presentacion_Ejecutiva_RapiMarket.pdf    <- 7 láminas para el Comité Ejecutivo
│   └── fuente/
├── guion_y_papel/
│   ├── Guion_y_evidencias_Parte1.pdf            <- fotos del guion a mano, T1-T6 y wireframe + transcripción
│   ├── fotos/                    <- fotos originales de las hojas (y el wireframe rotado para lectura)
│   ├── Transcripcion_Parte1.md   <- transcripción revisada por el grupo
│   └── Enunciado_Parte1_referencia.md           <- enunciado y Anexo de la Parte 1 (referencia)
└── codigo_y_data/
    ├── run_all.py                <- ejecuta toda la solución desde cero
    ├── data/raw/                 <- los 6 CSV originales (no se modifican)
    ├── data/processed/           <- tabla integrada y KPIs (generados)
    ├── src/
    │   ├── config.py             <- rutas relativas, umbrales, metas y paleta
    │   ├── pipeline.py           <- Fase 1: calidad, joins y variables derivadas
    │   ├── auditoria.py          <- Fase 2: recálculo A1-A6, Simpson, Random Forest y figuras
    │   ├── documentos.py         <- Fase 4: informe ejecutivo y presentación (HTML -> PDF)
    │   └── guion_pdf.py          <- Fase 5: PDF del guion y evidencias de la Parte 1
    ├── resultados/               <- tablas de auditoría, calidad e importancia del modelo
    └── figuras/                  <- figuras estáticas del informe y la presentación
```

## Cómo ejecutar (Python 3.10 o superior)

Todas las rutas son relativas al proyecto: funciona en cualquier carpeta y sistema operativo.

```bash
# 1. Crear un entorno e instalar dependencias (desde la raíz del proyecto)
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux / Mac: source .venv/bin/activate
pip install -r requirements.txt

# 2. Regenerar toda la solución desde los CSV (pipeline, auditoría, figuras e informes)
python codigo_y_data/run_all.py

# 3. Abrir el dashboard
streamlit run dashboard/app.py
```

El dashboard también funciona sin el paso 2: si no encuentra los datos procesados, ejecuta el pipeline al iniciar.

## Publicar en Streamlit Community Cloud

El repositorio ya está preparado: los datos procesados y los resultados vienen incluidos, `dashboard/requirements.txt`
trae solo las 4 dependencias del dashboard (Cloud lo lee antes que el de la raíz) y `.streamlit/config.toml` define el tema.

1. Subir esta carpeta a un repositorio de GitHub (público o privado).
2. Entrar a [share.streamlit.io](https://share.streamlit.io) con la misma cuenta de GitHub y elegir **Create app → Deploy a public app from GitHub**.
3. Completar: **Repository** = el repositorio · **Branch** = `main` · **Main file path** = `dashboard/app.py`.
4. En *Advanced settings* elegir **Python 3.12** y pulsar **Deploy**. En unos minutos queda en `https://<nombre>.streamlit.app`.

No se necesitan secretos ni variables de entorno.
Los PDF se imprimen con Microsoft Edge o Google Chrome en modo headless; si no hay ninguno, se genera el HTML en
`fuente/` para imprimirlo desde el navegador.

## Dashboard (Streamlit)

| Página | Audiencia | Contenido |
|---|---|---|
| **Vista estratégica** | Comité Ejecutivo | Traducción del wireframe: filtros Periodo/Año, 4 KPIs con variación (clientes activos, pedidos, ventas, reclamos), franja de metas, Clientes por zona, Ventas vs Meta, Reclamos por bodega y tabla de datos trimestrales con "Peor bodega (según p90)". |
| **Vista operativa** | Operaciones | Drill-down: se abre con un clic en una ciudad. KPIs operativos con meta, Paradoja de Simpson (total vs por tipo), p90 por ciudad vs meta, tendencia semanal por bodega y tabla de pedidos con mayor retraso. |
| **Auditoría del memo (A1–A6)** | Comité / analistas | Recálculo de cada afirmación con el Anexo y con los CSV, y evidencia visual por afirmación. |
| **Fuga de clientes** | Comité / analistas | Importancia de variables del Random Forest vs Tabla E y recompra a 30 días según cada factor operativo. |
| **Calidad de datos y método** | Analistas | Auditoría de calidad, diccionario de KPIs unificados, supuestos y límites. |

**Interactividad:** filtros por ciudad, bodega y tipo de pedido (barra lateral), selector de período, drill-down por clic,
tooltips con detalle en todos los gráficos y conmutador "total / por tipo" en el gráfico de Simpson.

**Accesibilidad (WCAG 2.1):** paleta azul (cumple) / naranja (alerta) / gris (contexto), segura para daltonismo; el
estado nunca depende solo del color (ícono ✔/⚠, texto "Cumple meta / Bajo meta", formas y tipos de línea distintos,
patrón rayado en barras de alerta); contraste de texto ≥ 4,5:1.

## Decisiones de datos

- **Calidad:** sin duplicados ni llaves huérfanas en las 6 tablas. Los nulos de `temp_llegada_c` son esperables (pedidos sin congelados). Los extremos de tiempo y monto se conservan porque son el fenómeno a medir; se reportan mediana y p90.
- **Atraso:** marca `atrasado` de la fuente (entrega fuera de la ventana de 45 min; coincide en 99,98 % con tiempo > ventana).
- **Congelado fuera de temperatura:** llega sobre −15 °C. Los datos muestran un corte natural entre −15 °C y −10 °C (11,1 % de los pedidos con congelados, "1 de cada 9" como en el Anexo).
- **Recompra a 30 días:** solo para pedidos con 30 días de seguimiento (hasta el 31-ago-2026); septiembre queda censurado.
- **Clientes activos (KPI unificado):** clientes distintos con al menos un pedido en el período, en lugar de las tres cifras de D1, D2 y D3.
- **Datos que no traen los CSV:** visitas a la app (se toman del Anexo) y comunas (el filtro geográfico es por ciudad y bodega).
- **Modelo de fuga:** Random Forest con las 7 variables de la Tabla E, objetivo "no recompra a 30 días", importancia por permutación. AUC en prueba 0,64 (Anexo: 0,81); el orden de las variables coincide en lo principal.

## Resultados principales

| Hallazgo | Anexo | CSV del grupo |
|---|---|---|
| Reclamos sobre pedidos (A1) | 14,0 % | 14,2 % |
| Pedidos julio → septiembre (A2) | 62.000 → 58.000 | 98.822 → 37.818 |
| Atraso en Santiago vs resto (A3) | 24,0 % | 23,0 % vs 11,5 % |
| Simpson Centro vs Norte, pedidos complejos (A4) | 25 % vs 30 % | 24,2 % vs 28,2 % |
| Recompra a tiempo vs atrasado (A5) | 71 % vs 42 % | 68,0 % vs 40,6 % |
| Calificación real de los pedidos (A6) | encuesta 4,6/5 sesgada | 3,1/5 en 77.600 pedidos |
