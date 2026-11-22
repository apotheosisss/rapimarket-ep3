# Transcripción del trabajo en papel — EP3 Parte 1 (RapiMarket)

Transcripción fiel de las hojas escritas a mano en clases. Solo se normalizó la ortografía de las palabras que se leen con claridad.
Las referencias "tabla C", "tabla E", "D1/D2/D3" y "anexo" remiten al enunciado (ver `Enunciado_Parte1.md`).
Las lecturas dudosas fueron confirmadas por el grupo. Marcas usadas: **[tachado]** texto tachado en la hoja.

---

## T1

1.- El comité ejecutivo es quien decide la inversión, y como audiencia secundaria es el área de operaciones. El comité tiene un nivel técnico medio bajo, y el de operaciones es medio alto, además de que tendrá un uso diario con filtros y drill down. Se deberá decidir antes de 2027.

2.- Decidir dónde destinar los USD 3M para detener la caída que hubo de la recompra antes de 2027.

3.- Árbol de preguntas:

- **¿Se están reteniendo los clientes?**
  - ¿La fuga que hay se asocia a la entrega?
    - ¿Qué bodega en Santiago atrasa más según el pedido?
  - ¿En qué ciudad hay más atrasos?
  - ¿Cuáles variables pueden predecir esa fuga?
    - ¿Cuántos pedidos llegan con cosas faltantes o con la cadena de frío rota?

4.- Las afirmaciones que presentó marketing son erróneas, además que los cupones no son lo más importante según la tabla E. A2 y A6 de hecho se contradicen.

---

## T2 — Auditoría de las afirmaciones del Memo de Marketing

| Afirmación | Tipo de error | Evidencia y resultado | Lectura correcta | Decisión errónea que provoca |
|---|---|---|---|---|
| A1 | Denominador incorrecto | Una visita no es una compra, los reclamos hay que compararlos con los pedidos. | Al ser calculado entre visitas y compras solo se registra 1,2 % de reclamos. | Esconde fallas críticas de calidad de servicio. |
| A2 | Acumulado | Los acumulados siempre suben; los pedidos cada mes caen: 62.000, 60.000 y 58.000 respectivamente. | El acumulado crece, pero los pedidos han ido disminuyendo. | Hace creer que todo va mejor. |
| A3 | Volumen confundido con desempeño | Santiago es el que registra mayor cantidad de atrasos. | Santiago concentra la mayor cantidad de pedidos, pero más atrasos. | Creer que Santiago está excelente cuando no es así. |
| A4 | Paradoja de Simpson | Individualmente es el peor porque concentra 24.000 pedidos, que es la mayor cantidad de pedidos, a diferencia de otros que en 6.000 pedidos registran un 10 % de atrasos. | Por volumen, Centro concentra mayor cantidad de atrasos. | Malas estrategias logísticas. |
| A5 | Causalidad incorrecta | En escala, los pedidos con retraso son menos, pero relacionarlos con la calidad del producto es irresponsable. | Los pedidos con retraso generan abandono. | Creer que lo malo es el producto. |

*(A6 no aparece en esta hoja porque venía resuelta como fila de ejemplo en el enunciado: sesgo de supervivencia / selección.)*

---

## T3

**Errores**

1. D1: Fuente poco formal para datos cuantitativos.
2. D1-3: Paletas de colores excesivamente saturadas, poco comunicativas.
3. D1-D2: Títulos poco comunicativos o no abarcan el problema.
4. D1: Visualización gráfica pobre, sin relación a KPIs.
5. D1: Demasiado ruido visual por colores/diseño.
6. D2: Colores poco representativos para datos principales.
7. D2: Gráfico mal escalado.
8. D3: El gráfico de tendencia es poco representativo, difícil de interpretar.

**3 problemas de sistema**

- Reclamos en aumento y pedidos entregados en baja; los clientes que deciden NO volver a comprar van en aumento.
- La encuesta de satisfacción solo se hizo a clientes que se quedaron, introduciendo un riesgo de supervivencia [sesgo de supervivencia] en los datos.
- Los atrasos tienen mayor impacto en las fugas, concentrándose en bodegas Sur; propiedad externa y en pedidos complejos de bodega Centro.

**Confusión de clientes activos**

61.300 vs 412.000 = 412 % *(valor de referencia para destacar cuántas veces supera la base histórica a los clientes activos)*

Solo una cuarta parte de los usuarios históricos se mantiene activo al día de hoy, y menos de la mitad de los históricos poseen un medio de pago válido.

**Latencia de datos**

- Vista de Marketing: semanal, ya que las estrategias se definen con largos plazos.
- Vista de Despachos: inmediato, se necesita saber al momento cómo van las operaciones.
- Vista de Finanzas: diario, es importante saber cómo nos fue en el día para identificar tendencias o posibles riesgos.

---

## T4

1.-
1. Se puede conservar la tabla de D2, donde muestra las cifras por centro; ahí se puede agregar el centro sur y los tipos de pedido.
2. En el D1 se puede conservar el anexo, o sea todas las cifras en la parte superior, pero la forma en que se interpretan está mal; se debe corregir eso y se conservará.

2.- Matriz de impacto y esfuerzo:

| | Esfuerzo bajo | Esfuerzo alto |
|---|---|---|
| **Impacto alto** | 1. Reclamos por pedidos.<br>2. Incluir el centro sur y separar por tipos.<br>3. Pedidos por mes sin la torta en 3D.<br>4. Encuesta cuando el cliente hace su primer pedido. | 1. Una alerta en tiempo real cuando hay algún atraso. |
| **Impacto bajo** | 1. Un semáforo con íconos, paleta de colores y texto para las personas con daltonismo. | 1. Un mapa que sea interactivo dividido por comunas. |

---

## T5

**KPI 1 — Clientes activos:** obtiene clientes de la base de datos que hayan usado la app durante el trimestre, indicando con una flecha ascendente o descendente comparándose contra el mes anterior. Responsable: Marketing.

**KPI 2 — Pedidos:** obtiene los pedidos del mes e indica con una flecha ascendente o descendente, según corresponda, en comparación al mes anterior. Su meta es aumentar o mantenerse. Responsable: Logística o despachos.

**KPI 3 — Ventas en el último trimestre:** al igual que los demás KPIs, indica si le fue peor o mejor que el trimestre anterior. Responsable: Marketing.

**KPI 4 — Reclamos:** obtiene los reclamos en el trimestre, indicando si han aumentado o disminuido contra el mes anterior. Responsable: Soporte al cliente.

2.- Usaremos distribución en Z para una vista estratégica. Siendo nuestra audiencia el Comité Ejecutivo, yendo desde los KPIs en cabecera, gráficos al centro y tablas con datos a detalle debajo.

3.- [tachado] en el wireframe y el drill down en otra página.

4.- El dashboard está pensado para lectura completa de primera vista, pero se puede acceder al detalle fácilmente al hacer clic en cualquier componente. Además, cuando el mouse pase por encima se levantarán un poco, indicando que se puede clickear; luego de eso se accederá a tablas que permiten acceder individualmente a cada dato.

---

## T6

Se deben destinar los 3M de dólares a operaciones. Nada se va a cupones. Probar en diciembre de 2026 para llevarlo a cabo en 2027.

1.- La fuga que hay es en el área operacional. Su importancia es:
- 31 % de atrasos.
- 24 % de pedidos con productos faltantes.
- 17 % de problemas con productos que rompieron la cadena de frío.
- Y el uso de cupones solo tiene un 8 % de importancia relativa.

2.- En Q3 la recompra bajó de un 41 % a un 33 %, los reclamos subieron de 7.800 a 9.000 y los pedidos entregados bajaron de 62.000 a 58.000.

3.- Santiago atrasa la mayoría de pedidos, tiene un p90 de 78 minutos, cuando la meta es de menos de 60 minutos.

Se debe aprobar antes de 2026 para llevarlo a cabo en 2027. Hay que instalar un control de stock y también de sensores en el centro sur para reducir los atrasos, lograr un p90 menor a 60 minutos y aumentar la recompra hasta llegar al 41 % o más.

---

## Guion de presentación (hoja sin número)

**Situación:** Los dashboards disponibles muestran que va todo bien, y marketing pide los dólares para invertirlos en cupones.

**Complicación:** Cuando uno revisa el anexo, se ve que no es así: los reclamos están subiendo, los pedidos bajando y la recompra también. Además, Santiago está atrasando un 24 % y la bodega sur no aparece en los datos. Además, el reporte de marketing es erróneo.

**Solución:** Destinar los 3 millones de dólares al área de operaciones, ya que según la tabla E el área de operaciones acumula al menos un 72 % de importancia relativa según las diferentes variables de esa área.

**Limitaciones:**

1. Hay datos que no se han capturado: no hay reportes del centro sur y está centrado solo en Santiago.
   *Mitigación:* enviar un grupo de control al centro sur, o que el operador del centro sur entregue los datos, y hacer lo mismo de la tabla C pero en otras regiones.
2. La encuesta solo llega hasta el segundo pedido.
   *Mitigación:* hacer una encuesta cuando el cliente hace su primer pedido y cuando se van.

---

## Wireframe (hoja milimetrada, horizontal)

**Encabezado, derecha:** filtros desplegables *Periodo ▾* y *Año ▾*.

**Fila superior — 4 tarjetas KPI** (cada una con valor, % y variación en p.p.):
1. Clientes activos — vs último mes
2. Pedidos último mes — vs último mes
3. Ventas trimestrales — vs último trimestre
4. Reclamos — vs último mes

**Fila central:**
- **Izquierda — "Clientes por zona":** barras horizontales para Santiago (la más larga, destacada con achurado), Valparaíso, Concepción, La Serena y Temuco.
- **Centro — "Ventas vs Meta":** gráfico de línea de enero a julio, con la línea de meta punteada. Leyenda: Ventas, Meta, Periodos.
- **Derecha — "Reclamos por bodega":** tres líneas por trimestre (Q1, Q2, Q3). Leyenda: Norte, Sur, Centro.

**Fila inferior — "Datos trimestrales"** (tabla):

| Trimestre | Clientes activos | Pedidos entregados | Pedidos atrasados | Reclamos | Ventas totales | Visitas App | Peor bodega (según p90) |
|---|---|---|---|---|---|---|---|
| Q1 | N° | N° | N° | N° | N° $ | N° | C / N / S |
| Q2 | N° | N° | N° | N° | N° $ | N° | C / N / S |
| Q3 | N° | N° | N° | N° | N° $ | N° | C / N / S |
