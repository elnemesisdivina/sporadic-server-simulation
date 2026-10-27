# Simulador del Servidor Esporádico (Sporadic Server) en Tiempo Real

[![Versión](https://img.shields.io/badge/versión-2.1.0-blue.svg)](sporadic_server_sim.py)
[![Pruebas](https://img.shields.io/badge/pruebas-10%2F10%20pasadas-brightgreen.svg)](sporadic_server_sim_test.py)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green.svg)](LICENSE)

Especificación matemática, verificación algorítmica y visualización interactiva del algoritmo de planificación expulsiva con prioridades estáticas **Servidor Esporádico (Sporadic Server, SS)** bajo asignación de prioridades por **Tasa Monótona (Rate-Monotonic, RM)**.

---

## 📌 Descripción General y Propósito

Este paquete proporciona una implementación autónoma en Python 3 para simular, verificar y visualizar el comportamiento del **Servidor Esporádico (SS)**. Su objetivo es demostrar cómo se atienden peticiones aperiódicas ($J_1 \dots J_6$) garantizando tiempos de respuesta mínimos sin comprometer los plazos estrictos (*hard deadlines*) de las tareas periódicas ($\tau_1 \dots \tau_6$).

El algoritmo sigue la formulación teórica de Sprunt, Sha y Lehoczky (1989), tal como se describe en el texto canónico de Giorgio Buttazzo:  
*Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications* (Capítulo 5, Sección 5.6, págs. 143–149).

### 🚀 Novedades de la Versión 2.1.0

1. **Despacho Matemático Unificado y Reevaluación en CPU Idle**:
   * Implementación de la función formal `is_server_ready(queue_len, budget_ticks)`.
   * El servidor esporádico compite formalmente como una tarea más en el planificador Rate-Monotonic según su período $T_s$.
   * Reevaluación inmediata: cuando una tarea periódica previa termina o la CPU queda libre, el planificador despacha de inmediato al servidor si está en estado *Ready*.
2. **Carga Dinámica de Cargas por JSON (`--tasks-json`)**:
   * Los parámetros de tareas ya no están cableados (*hardcoded*). Se pueden definir diferentes escenarios mediante archivos JSON.
   * Incluye dos casos de estudio: `example_schedulable.json` ($U \approx 0.783 \le 1.0$) y `example_unschedulable.json` ($U = 1.35 > 1.0$).
3. **Detección Automática de Planificabilidad y Advertencias en Consola**:
   * Evaluación de utilización hiperbólica y cota de Liu & Layland.
   * Análisis exacto de tiempos de respuesta en el peor caso (**RTA**) por iteración de punto fijo (Teorema 5.1 de Buttazzo).
   * Alertas en consola con formato de color: verde para conjuntos planificables y rojo para sobrecargas o incumplimientos de plazos.
4. **Dashboard Interactivo HTML5/SVG con Animación y HUD Dinámico**:
   * Control temporal de reproducción, pausa, retroceso, avance y velocidad variable.
   * Visualizador en vivo (HUD) que refleja con precisión las transiciones de estado: `OCIOSO (Listo)`, `EJECUTANDO (-1/s)`, `DESALOJADO (por τ_i)` y `SUSPENDIDO (C_s=0)`.
5. **Código Totalmente Comentado en Español**:
   * Documentación interna exhaustiva y pedagógica paso a paso para facilitar la explicación técnica en revisiones académicas.

---

## 📂 Archivos del Repositorio

* [`sporadic_server_sim.py`](sporadic_server_sim.py): Motor principal de simulación discreta, analizador de planificabilidad RTA, generador de gráficas Matplotlib y exportador a HTML/CSV/JSON.
* [`sporadic_server_sim_test.py`](sporadic_server_sim_test.py): Suite de pruebas unitarias (`unittest`) que valida 10 invariantes teóricos y matemáticos del algoritmo.
* [`example_schedulable.json`](example_schedulable.json): Configuración de carga planificable ($U \le 1.0$, 0 violaciones de plazo).
* [`example_unschedulable.json`](example_unschedulable.json): Configuración de carga sobrecargada ($U = 1.35 > 1.0$) para observar violaciones de plazo y el comportamiento del servidor.
* [`sporadic_server_simulation.png`](sporadic_server_simulation.png): Gráfica generada en alta resolución (300 DPI) con el diagrama de Gantt y la curva de presupuesto $C_s(t)$.
* [`sporadic_server_interactive.html`](sporadic_server_interactive.html): Dashboard animado e interactivo autónomo (sin dependencias de red).

---

## 📐 Reglas Algorítmicas del Servidor Esporádico

El Servidor Esporádico $S_s$ cuenta con una capacidad máxima de presupuesto $C_s$, un período de reposición $T_s$ y una prioridad asignada $P_s$. Se rige por las siguientes reglas formales:

1. **Condición de Disponibilidad (`isReady`)**:  
   El servidor puede competir por el procesador si y solo si:
   $$\text{cola aperiódica no vacía} \quad \land \quad C_s(t) > 0$$
2. **Consumo de Presupuesto**:  
   El presupuesto $C_s(t)$ se decrementa a tasa unitaria ($-1$ por unidad de tiempo) **únicamente mientras $S_s$ ejecuta un trabajo aperiódico en la CPU**.
3. **Preservación de Presupuesto**:  
   La capacidad no se consume mientras el servidor permanece ocioso (sin peticiones en cola) o mientras está desalojado (*preempted*) por tareas periódicas de mayor prioridad ($\tau_1, \tau_2, \tau_3$).
4. **Instante de Activación ($t_A$)**:  
   Se registra en el instante en que $S_s$ comienza a ejecutar una petición aperiódica con $C_s > 0$ a su nivel de prioridad $P_s$.
5. **Conservación de Ventana ante Desalojo**:  
   Si una tarea periódica de mayor prioridad desaloja al servidor mientras su ventana está abierta, el instante $t_A$ se conserva intacto y la ventana continúa abierta hasta que el presupuesto se agote o la cola quede vacía.
6. **Programación de Recargas ($t_R$)**:  
   Al cerrarse la ventana de activación (por vaciarse la cola o agotarse el presupuesto), la cantidad consumida $RA$ se programa para reponerse exactamente en:
   $$t_R = t_A + T_s$$
7. **Suspensión**:  
   Si $C_s(t) = 0$, el servidor no puede competir por la CPU hasta que una recarga programada restaure presupuesto positivo.
8. **Cota de Capacidad**:  
   Las recargas nunca incrementan $C_s(t)$ por encima de su capacidad máxima inicial $C_{s,\max}$.

---

## 📊 Conjunto de Cargas y Análisis Teórico

### Carga Periódica por Defecto (Planificable)

| Tarea | Prioridad ($P_i$) | Cómputo ($C_i$) | Período ($T_i$) | Plazo ($D_i$) | Utilización ($U_i$) | Peor Caso $R_i$ (RTA) | ¿Planificable? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $\tau_1$ | 7 (Máxima) | 1.0 | 6.0 | 6.0 | 0.1667 | 1.0 | **SÍ** ($1.0 \le 6.0$) |
| $\tau_2$ | 6 | 1.0 | 10.0 | 10.0 | 0.1000 | 2.0 | **SÍ** ($2.0 \le 10.0$) |
| $\tau_3$ | 5 | 1.0 | 12.0 | 12.0 | 0.0833 | 3.0 | **SÍ** ($3.0 \le 12.0$) |
| **$S_s$** | **4 (Servidor)** | **2.0** | **12.0** | **12.0** | **0.1667** | **5.0** | **SÍ ($5.0 \le 12.0$)** |
| $\tau_4$ | 3 | 1.5 | 15.0 | 15.0 | 0.1000 | 7.5 | **SÍ** ($7.5 \le 15.0$) |
| $\tau_5$ | 2 | 2.0 | 20.0 | 20.0 | 0.1000 | 9.5 | **SÍ** ($9.5 \le 20.0$) |
| $\tau_6$ | 1 (Mínima) | 2.0 | 30.0 | 30.0 | 0.0667 | 18.0 | **SÍ** ($18.0 \le 30.0$) |

### Factor de Utilización del Procesador

$$
U_{total} = \sum_{i=1}^6 \frac{C_i}{T_i} + \frac{C_s}{T_s} = \frac{1}{6} + \frac{1}{10} + \frac{1}{12} + \frac{2}{12} + \frac{1.5}{15} + \frac{2}{20} + \frac{2}{30} = \frac{47}{60} \approx 0.7833 \le 1.0
$$

La cota de Liu & Layland para $n = 7$ tareas es $U_{LL} = 7 \cdot (2^{1/7} - 1) \approx 0.7286$. Como $U_{total} > U_{LL}$, la condición suficiente no concluye, por lo que se requiere el Análisis de Tiempo de Respuesta (**RTA**) para demostrar planificabilidad estricta.

### Análisis de Tiempo de Respuesta (Teorema 5.1 de Buttazzo)

Por el Teorema 5.1 de Giorgio Buttazzo, el Servidor Esporádico $(C_s, T_s)$ produce exactamente la misma interferencia máxima sobre las tareas de menor prioridad que una tarea periódica equivalente. La iteración de punto fijo:

$$
R_i^{(k+1)} = C_i + \sum_{j \in hp(i)} \left\lceil \frac{R_i^{(k)}}{T_j} \right\rceil C_j
$$

demuestra que el 100% de las tareas periódicas y el servidor cumplen sus plazos ($R_i \le D_i$).

---

## 🛠️ Guía de Ejecución y Pruebas

El entorno utiliza [`uv`](https://github.com/astral-sh/uv) para ejecutar el script de manera reproducible y automática:

### 1. Ejecutar la Simulación por Defecto (Ventana GUI Matplotlib)
```bash
uv run --with matplotlib python sporadic_server_sim.py
```

### 2. Ejecutar en Modo Headless (Generación de PNG y Dashboard HTML)
```bash
uv run --with matplotlib python sporadic_server_sim.py --no-show
```

### 3. Abrir el Dashboard Interactivo en el Navegador
```bash
# macOS
open sporadic_server_interactive.html

# Linux
xdg-open sporadic_server_interactive.html
```

### 4. Ejecutar con Cargas Personalizadas desde JSON

* **Caso Planificable ($U \le 1.0$, 0 violaciones de plazo):**
  ```bash
  uv run --with matplotlib python sporadic_server_sim.py --no-show --tasks-json example_schedulable.json
  ```

* **Caso No Planificable / Sobrecargado ($U = 1.35 > 1.0$):**
  ```bash
  uv run --with matplotlib python sporadic_server_sim.py --no-show --tasks-json example_unschedulable.json
  ```

### 5. Exportar Trazas a Formato CSV y JSON
```bash
uv run --with matplotlib python sporadic_server_sim.py --no-show --export-csv execution_trace.csv --export-json simulation_data.json
```

### 6. Ejecutar la Suite de Pruebas Unitarias
```bash
uv run --with matplotlib python -m unittest sporadic_server_sim_test.py -v
```

---

## 📝 Formato del Archivo JSON de Tareas

Para crear tus propios escenarios de prueba, define un archivo `.json` con la siguiente estructura:

```json
{
  "horizon": 30.0,
  "dt": 0.1,
  "periodic_tasks": [
    {
      "name": "$\\tau_1$",
      "priority": 7,
      "compute_time": 1.0,
      "deadline": 6.0,
      "period": 6.0,
      "color": "#0072B2"
    }
  ],
  "server": {
    "name": "$S_s$",
    "priority": 4,
    "budget": 2.0,
    "period": 12.0,
    "deadline": 12.0,
    "color": "#16a085"
  },
  "aperiodic_jobs": [
    {
      "name": "J1",
      "arrival_time": 2.0,
      "compute_time": 1.0
    }
  ]
}
```
*Si se omiten los colores, el simulador asigna automáticamente una paleta de alto contraste optimizada para accesibilidad visual.*

---

## ✅ Cobertura de Pruebas Unitarias (`unittest`)

| Invariante / Propiedad Verificada | Método de Prueba | Resultado |
| :--- | :--- | :---: |
| **Cumplimiento de Plazos Periódicos (0 misses)** | `test_no_periodic_deadline_misses` | **Pass** |
| **Conservación Exacta del Tiempo de CPU** | `test_exact_cpu_utilization_totals` | **Pass** |
| **Instantes de Activación ($t_A$)** | `test_exact_activation_times` | **Pass** |
| **Instantes y Montos de Recarga ($t_R$)** | `test_exact_replenishment_times_and_amounts` | **Pass** |
| **Preservación de Ventana ante Desalojo** | `test_sporadic_server_preemption_preserves_activation_window` | **Pass** |
| **Ejecución y Despacho FIFO Aperiódico** | `test_aperiodic_jobs_completion_status` | **Pass** |
| **Generación de Figura PNG** | `test_plot_simulation_generates_image` | **Pass** |
| **Análisis de Planificabilidad y RTA** | `test_schedulability_and_rta_analysis` | **Pass** |
| **Exportación a CSV y JSON** | `test_export_csv_and_json` | **Pass** |
| **Generación de Dashboard HTML Interactivo** | `test_export_interactive_html` | **Pass** |
