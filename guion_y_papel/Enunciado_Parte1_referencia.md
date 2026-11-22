# EP3 Parte 1 — "El Comité que Leyó Mal los Datos" (enunciado transcrito)

Transcripción de las fotos del enunciado impreso. Algunas partes se ven muy tenues en las fotos: van marcadas con **[?]**.

**ADY1104 · Evaluación Parcial 3 (Parte 1).** Documento del estudiante | Auditoría crítica en papel y rediseño visual — Caso RapiMarket.

- Presupuesto inversión H1 2027: **USD 3.000.000** (decisión del Comité Ejecutivo)
- Duración total de la evaluación: **120 minutos** (2 sesiones de 60 min, clases 1 y 2)
- Puntaje total sumativo: **100 puntos** (6 tareas integradoras a mano)
- Modalidad 100 % análoga: **0 dispositivos** (solo lápiz y papel milimetrado)

## I. Reglas de la sesión y formato de entrega

**Modalidad de trabajo:** la actividad se realiza en grupos de máximo 3 integrantes, de forma 100 % presencial, a mano y en papel. Se proporcionarán hojas blancas para el desarrollo conceptual y papel milimetrado para el trazado de gráficos y wireframes. **Restricción de dispositivos:** queda estrictamente prohibido el uso de computadores, teléfonos celulares, tablets o asistentes de inteligencia artificial. Se autoriza únicamente el uso de calculadora simple no programable.

**Custodia de insumos:** cada hoja debe incluir el número de grupo, los nombres completos de los integrantes y el código de la tarea. Al finalizar la **Clase 1**, el docente retirará y custodiará las hojas firmadas, devolviéndolas al inicio de la **Clase 2**. La entrega final en papel de la Clase 2 constituye el insumo obligatorio no modificable para la Parte 2 en computador.

| Clase | Tarea | Tiempo | Puntaje |
|---|---|---|---|
| Clase 1 | T1 · Problema de negocio, audiencias y árbol de preguntas analíticas | 15 min | 10 pts |
| Clase 1 | T2 · Auditoría del análisis equivocado (Memo de Marketing y recálculos) | 25 min | 25 pts |
| Clase 1 | T3 · Auditoría del sistema actual de dashboards (D1, D2, D3) | 20 min | 20 pts |
| Clase 2 | T4 · Fortalezas del sistema actual y priorización de mejoras | 15 min | 10 pts |
| Clase 2 | T5 · Diseño de la solución propuesta (wireframe en papel milimetrado y UX) | 30 min | 25 pts |
| Clase 2 | T6 · Recomendación ejecutiva (Pirámide de Minto, 3 actos y limitaciones) | 15 min | 10 pts |
| **Total** | 2 sesiones de cátedra / 6 tareas integradas en papel | 120 min | 100 pts |

## II. El caso de negocio: RapiMarket Q3 2026

**Contexto corporativo:** RapiMarket es una plataforma tecnológica de entregas de supermercado a domicilio que opera en Santiago, Valparaíso, Concepción, La Serena y Temuco. Al cierre del tercer trimestre de 2026 (julio a septiembre), el Comité Ejecutivo debe definir el destino de una inversión estratégica de **USD 3.000.000** para el primer semestre de 2027.

Existen tres posturas internas encontradas sobre dónde invertir el capital:

1. **Marketing:** campaña masiva de cupones de descuento para acelerar la adquisición y retención.
2. **Operaciones:** invertir en flota y bodegas propias en Santiago para reemplazar al operador logístico externo en la zona Sur.
3. **Calidad y cadena de frío:** mejorar el control de stock y los sistemas de refrigeración de productos frescos y congelados.

Actualmente, Santiago se abastece desde tres bodegas: Centro y Norte (propiedad de RapiMarket) y Sur (operada por un tercero externo).

### Transcripción del Memo de la Gerencia de Marketing (análisis a auditar)

**DE:** Gerencia de Marketing | **PARA:** Comité Ejecutivo | **ASUNTO:** Evaluación Q3 y Propuesta Inversión 2027

- **A1 (Calidad de servicio):** La calidad del servicio es excelente: registramos solo 1,2 % de reclamos (25.200 reclamos sobre 2.100.000 visitas a la app).
- **A2 (Crecimiento):** Seguimos creciendo de forma imparable: los pedidos acumulados superaron los 3,3 millones (3.340.000) y el ticket promedio está en fuerte alza ($41.200 en septiembre).
- **A3 (Concentración):** Santiago es nuestra mejor ciudad al concentrar el 55 % de los pedidos totales, por lo que no requiere inversión operativa.
- **A4 (Desempeño de bodegas):** La Bodega Centro es la peor de Santiago con 22,0 % de pedidos atrasados frente al 15,6 % de Bodega Norte. Proponemos cerrarla y derivar sus pedidos a Norte.
- **A5 (Fidelización):** El problema principal radica en la calidad de los productos: los clientes que califican con 1–2 estrellas no vuelven a comprar.
- **A6 (Satisfacción):** Los clientes están altamente felices: la encuesta de satisfacción del trimestre arrojó 4,6 de 5 estrellas.

**RECOMENDACIÓN FINAL:** Destinar la totalidad de los USD 3.000.000 a cupones de descuento para atraer y fidelizar usuarios.

## III. Diagnóstico del sistema de dashboards actual

El Comité Ejecutivo opera actualmente con tres dashboards desconectados, construidos de forma independiente por cada área:

- **D1 (Marketing - Q3 calendario):** muestra tarjetas de KPIs en colores saturados (Clientes activos: 412.000; Visitas app: 2,1M; Reclamos: 1,2 %; Pedidos Q3: 180.000; Satisfacción: 4,6/5; Cupones: 45.000; Ticket sep: $41.200). Incluye un gráfico de torta en 3D para "Pedidos por ciudad" y una curva de "Crecimiento imparable de pedidos" con eje Y acumulado sin cero.
- **D2 (Operaciones - últimos 30 días móviles, actualiz. semanal):** muestra Clientes activos (61.300), Tiempo promedio de entrega (38 min - luz verde), Pedidos entregados (99,1 % - luz verde) y Reclamos abiertos (2.480 - luz roja). Presenta una tabla de bodegas donde omite a la Bodega Sur por ser operador externo y un gráfico de líneas cruzadas con doble eje Y y sin escala clara.
- **D3 (Finanzas - trimestre fiscal jun-ago):** reporta Clientes con medio de pago válido (148.000), Ventas trimestre (CLP 7.335 M) y Margen agosto (6,4 % vs meta 7 %). Muestra gráficos de barra desfasados, desalineados del Q3 calendario.

*Nota de evaluación:* las incoherencias cromáticas (semáforos sin texto explicativo) y la falta de unificación en métricas clave forman parte de los errores a auditar.

### Hoja impresa de los dashboards (descripción)

- **D1 "DASHBOARD MARKETING Q3 2026 ★★★"** (fondo oscuro): tarjetas Clientes activos 412.000 · Visitas app 2,1 M · Reclamos 1,2 % · Pedidos Q3 180.000 · Satisfacción 4,6/5 · Cupones usados 45.000 · Ticket sep $41.200. Torta 3D "Pedidos por ciudad" (Santiago, Valparaíso, Concepción, Otras). Línea "¡Crecimiento imparable de pedidos!" de junio a septiembre hasta "3.340.000 acumulados", con el eje marcado "???".
- **D2 "Monitor de Despachos · últimos 30 días · actualizado lun 08:00":** Clientes activos 61.300 · Tiempo de entrega promedio 38 min · Pedidos entregados 99,1 % · Reclamos abiertos 2.480 (con semáforos sin texto). Tabla "Bodegas propias Santiago (Q3)": Centro 30.000 pedidos, 22,0 % atrasados, mediana 43 min; Norte 30.000, 15,6 %, 36 min. Notas: "Bodega Sur: operador externo, no reporta a este dashboard" y "Clic en una bodega para ver el detalle por comuna". Gráfico "Pedidos y atrasos" con dos líneas cruzadas y doble eje sin rótulos claros.
- **D3 "Cierre financiero · Trimestre fiscal jun–ago 2026":** Clientes con medio de pago válido 148.000 · Ventas trimestre CLP 7.335 M · Margen agosto 6,4 %. Barras "Ticket promedio en fuerte alza" (jun, jul, ago) con eje desde 38.500 hasta 41.500 CLP por pedido. Línea "Margen mensual vs meta (%)": 6,1 % · 6,0 % · 6,4 %, con meta 7 %.

## IV. Anexo Oficial de Datos Corporativos (Q3 2026)

Utilice estrictamente los siguientes datos auditados para realizar los recálculos en las tareas T1 a T6.

### Tabla A · Pedidos, reclamos y métricas de recompra Q3 2026

| Mes | Pedidos entregados | Reclamos formales | Visitas a la app | Recompra a 30 días | Ticket promedio |
|---|---|---|---|---|---|
| Julio | 62.000 | 7.800 | 700.000 | 41 % | CLP 39.100 |
| Agosto | 60.000 | 8.400 | 700.000 | 37 % | CLP 41.000 |
| Septiembre | 58.000 | 9.000 | 700.000 | 33 % | CLP 41.200 |
| **Total Q3** | **180.000** | **25.200** | **2.100.000** | — (media: 37 %) | — (prom.: CLP 40.4xx [?]) |

**Notas complementarias** (texto tenue en la foto):
- Pedidos acumulados históricos: 3.160.000 al cierre de junio y 3.340.000 al cierre de septiembre.
- Junio registró 63.000 pedidos con ticket promedio de CLP 38.900. Desde el 1 de agosto se aplica un cargo fijo de servicio de CLP 1.990 por pedido.
- Base de clientes: 412.000 cuentas creadas desde 2021; 148.000 con medio de pago válido; 61.300 con al menos 1 pedido en los últimos 30 días.
- El 21 % del total de pedidos entregados registró al menos un producto faltante o sustituido en caja.

### Tabla B · Desempeño operativo por ciudad (Q3 2026)

| Ciudad | Pedidos entregados | % del total | % pedidos atrasados | Tiempo mediano | Tiempo percentil 90 (p90) |
|---|---|---|---|---|---|
| Santiago | 99.000 | 55 % | 24,0 % | 41 min | 78 min (meta: < 60 min) |
| Valparaíso | 30.000 | 17 % | 12,0 % | 35 min | 55 min |
| Concepción | 25.000 | 14 % | 13,0 % | 36 min | 58 min |
| La Serena | 14.000 | 8 % | 10,0 % | 33 min | 50 min |
| Temuco | 12.000 | 7 % | 11,0 % | 34 min | 52 min |
| **Total / prom.** | **180.000** | **100 %** | **18,9 %** | **38 min** | **68 min** |

### Tabla C · Desglose operativo por bodega en Santiago y tipo de pedido (Paradoja de Simpson)

| Bodega | Operador | Tipo de pedido | Pedidos totales | Pedidos atrasados | Tasa % atraso efectiva |
|---|---|---|---|---|---|
| Centro | Propia | Complejo (>30 prod / congelados / >6 km) | 24.000 | 6.000 | 25,0 % |
| Centro | Propia | Simple (estándar / cercanía) | 6.000 | 600 | 10,0 % |
| Norte | Propia | Complejo (>30 prod / congelados / >6 km) | 6.000 | 1.800 | 30,0 % |
| Norte | Propia | Simple (estándar / cercanía) | 24.000 | 2.880 | 12,0 % |
| Sur | Externo (tercero) | Complejo (>30 prod / congelados / >6 km) | 13.000 | 6.240 | 48,0 % |
| Sur | Externo (tercero) | Simple (estándar / cercanía) | 26.000 | 6.240 | 24,0 % |

### Tabla D · Matriz de calificaciones de servicio y atrasos (n = 72.000 encuestados)

| Segmento de pedido | Pedidos totales | % calificados 1-2 estrellas | % sin recompra a 30 días |
|---|---|---|---|
| Pedido atrasado | 13.300 | 40,0 % | 58,0 % |
| Pedido a tiempo | 58.700 | 9,0 % | 29,0 % |

*Hallazgo analítico:* dentro de cada segmento (atrasado vs a tiempo), la tasa de recompra entre quienes califican 1-2★ difiere en menos de 3 puntos porcentuales respecto a quienes califican 4-5★.

### Tabla E · Importancia relativa en modelo predictivo de fuga (Random Forest - AUC = 0,81)

| Variable operativa / servicio | Importancia relativa | Impacto en fuga de clientes |
|---|---|---|
| Pedido atrasado | 31,0 % | Principal factor explicativo de fuga |
| Productos faltantes o sustituidos | 24,0 % | Alta insatisfacción en recepción de caja |
| Congelados recibidos fuera de temperatura | 17,0 % | Rompe cadena de frío (1 de cada 9 pedidos) |
| Reclamo sin respuesta > 24 horas | 12,0 % | Sin recompra sube de 31 % a 61 % |
| Uso de cupón de descuento | 8,0 % | Bajo impacto en retención de largo plazo |
| Calificación de productos | 5,0 % | Factor secundario sintomático |
| Ciudad de origen | 3,0 % | Impacto marginal no determinante |

*Nota técnica:* la encuesta de satisfacción trimestral (4,6/5) tuvo 4.100 respuestas y se envió únicamente al confirmar el segundo pedido de un cliente (sesgo de supervivencia).

## V. Encargo práctico · Clase 1 (60 minutos | 55 puntos)

### T1 · Problema de negocio, audiencias y árbol de preguntas (10 pts | 15 min)
1. Identifique la audiencia principal (quién decide la inversión de USD 3M) y una audiencia secundaria, indicando su nivel técnico y contexto de uso.
2. Redacte la decisión de negocio en una sola frase con plazo y monto implícito, y defina el objetivo de comunicación (informar, explicar, persuadir o monitorear).
3. Construya en su hoja un **árbol de preguntas analíticas de 3 niveles** (Monitoreo → Diagnóstico → Causa raíz) con al menos 5 preguntas accionables.
4. Explique en 3 líneas por qué el Memo de Marketing no responde a la decisión planteada.

### T2 · Auditoría del análisis equivocado (Memo de Marketing) (25 pts | 25 min)
Complete en su hoja la siguiente matriz auditando las afirmaciones A1 a A6. Muestre los recálculos explícitos empleando el Anexo de Datos.

Columnas: Afirmación · Tipo de error (Denominador, Acumulado, Simpson, Sesgo, etc.) · Evidencia y recálculo concreto · Lectura correcta de los datos · Decisión errónea que provoca.

Fila de ejemplo ya impresa en el enunciado:

| Afirm. | Tipo de error | Evidencia y recálculo concreto | Lectura correcta de los datos | Decisión errónea que provoca |
|---|---|---|---|---|
| A6 | Sesgo de supervivencia / selección | Encuesta de 4.100 respuestas se envió solo al confirmar el SEGUNDO pedido. | 4,6/5 representa solo a clientes retenidos; ignora al 59 % que fuga tras el 1er pedido. | Tomar decisiones con una muestra sesgada que oculta la insatisfacción real. |

**Requisito de trazado a mano:** en papel milimetrado, dibuje a mano el gráfico que desarticula la Paradoja de Simpson en A4 (atrasos por bodega separados por tipo de pedido) y el gráfico para A3 (volumen vs tasa).

### T3 · Auditoría del sistema actual de dashboards (20 pts | 20 min)
- **8 errores visuales:** identifique 8 fallas de diseño en D1, D2 y D3 indicando: dashboard, error, principio violado (Gestalt, jerarquía, integridad del eje, WCAG) y corrección concreta.
- **3 problemas de sistema:** compare definiciones, períodos (Q3 vs 30 días vs trimestre fiscal), frecuencias de actualización y filtros entre D1, D2 y D3.
- **Confusión de clientes activos:** explique el conflicto en el Comité al coexistir 412.000 (cuentas históricas), 61.300 (últimos 30 días) y 148.000 (medio de pago válido).
- **Latencia de datos:** justifique qué latencia requiere cada vista (tiempo real, diaria o batch semanal) y por qué la actualización semanal de D2 no sirve para corregir atrasos.

## VI. Encargo práctico · Clase 2 (60 minutos | 45 puntos)

### T4 · Fortalezas y priorización de mejoras (10 pts | 15 min)
- Identifique 2 fortalezas del sistema actual que conservaría en el nuevo diseño, respaldadas con evidencia del anexo.
- Clasifique al menos 6 mejoras propuestas en una matriz de **Impacto (Alto/Bajo) × Esfuerzo (Alto/Bajo)** y justifique el cuadrante prioritario para la Parte 2.

### T5 · Solución propuesta y wireframe en papel milimetrado (25 pts | 30 min)
1. **Diccionario de 4 KPIs unificados:** defina nombre, fórmula, fuente, frecuencia, meta y responsable. Un KPI debe unificar las 3 versiones de "clientes activos".
2. **Arquitectura de navegación:** plantee la estructura de vistas (estratégica, táctica, operativa), identificando audiencia y flujo de drill-down.
3. **Wireframe a mano en papel milimetrado:** trace a escala la vista principal para el Comité Ejecutivo. Detalle de cada componente: tipo de gráfico, variables, atributo visual codificado, filtros e interacciones.
4. **UX y accesibilidad WCAG 2.1:** indique 2 mecanismos de *Information Scent*, qué datos se ocultan por *Progressive Disclosure* y cómo garantizará la accesibilidad cromática sin depender solo de semáforos rojo/verde.

### T6 · Recomendación ejecutiva y Pirámide de Minto (10 pts | 15 min)
- Redacte la recomendación final al Comité bajo el modelo de **Pirámide de Minto**: titular activo con la decisión de inversión, 3 argumentos basados en cifras del Anexo y una acción concreta con plazo.
- Esboce el guion de comunicación en 3 actos (Situación → Complicación → Solución) para la defensa oral.
- Detalle 2 limitaciones o sesgos no resueltos por su propuesta (ej. datos no capturados) y cómo los mitigará.
