# Sporadic Server (SS) Real-Time Scheduling Simulation

Mathematical specification, algorithmic verification, and visual reference for
the Sporadic Server (SS) fixed-priority preemptive scheduling algorithm under
Rate-Monotonic (RM) priority assignment.

## Overview & Purpose

This package provides a standalone Python 3 simulation and visualization for the
**Sporadic Server (SS)** algorithm. It shows how soft aperiodic requests ($J_1
\dots J_6$) are serviced with low response times without causing any hard
deadline misses across 6 periodic tasks ($\tau_1 \dots \tau_6$).

The implementation follows the formulation by Sprunt, Sha, and Lehoczky (1989)
as presented in Giorgio Buttazzo's *Hard Real-Time Computing Systems* (Chapter
5, Section 5.6, pp. 143–149).

Files in this directory:

-   `sporadic_server_sim.py`: Standalone Python 3 simulation engine and
    two-panel `matplotlib` plotter.
-   `sporadic_server_sim_test.py`: Unit test suite (`unittest`) verifying
    scheduling invariants and the ground-truth trace.
-   `sporadic_server_simulation.png`: High-resolution (300 DPI) plot of the
    6-task RM simulation.

### Simulation Execution Plot

![Sporadic Server Simulation](./sporadic_server_simulation.png)

## Scheduling Rules & Theoretical Nuances

### Core SS Algorithm Rules

The Sporadic Server $S_s$ has a maximum capacity (budget) $C_s$, a replenishment
period $T_s$, and an intermediate priority level $P_s$. It follows seven rules:

1.  **Budget Consumption**: Server capacity $C_s(t)$ decreases at unit rate
    ($-1$ per unit time) only while $S_s$ executes an aperiodic job on the CPU.
2.  **Budget Preservation**: Capacity stays constant whenever $S_s$ is idle (no
    pending requests) or preempted by higher-priority tasks ($\tau_1, \tau_2,
    \tau_3$).
3.  **Activation Instant ($t_A$)**: Set at the instant $S_s$ begins (or resumes
    after suspension or an empty queue) executing an aperiodic request with
    $C_s > 0$ at priority level $P_s$.
4.  **Mid-Window Preemption by Higher-Priority Tasks**: If $\tau_1, \tau_2,$ or
    $\tau_3$ preempts $S_s$ while an activation window is open, the window stays
    open and $t_A$ is preserved. Preemption pauses consumption without splitting
    the replenishment interval.
5.  **Replenishment Scheduling ($t_R$)**: When the active window closes (either
    $C_s = 0$ or the aperiodic queue becomes empty), the capacity consumed
    during that window ($RA$) is scheduled to replenish at $t_R = t_A + T_s$.
6.  **Server Suspension**: Whenever $C_s(t) = 0$, $S_s$ cannot contend for the
    CPU until a scheduled replenishment restores $C_s > 0$.
7.  **Capacity Bound**: Replenishments never raise $C_s(t)$ above $C_{s,\max}$.

### Sprunt-Sha-Lehoczky vs. Queue-Aware Activation

> [!IMPORTANT] **Theoretical Alignment on Activation Rule ($t_A$)**: In the
> original Sprunt-Sha-Lehoczky (1989) definition and Buttazzo Figure 5.17, $t_A$
> is set as soon as CPU priority satisfies $P_{exe} \ge P_s$, even when the
> aperiodic queue is empty. In this simulation, $t_A$ is set only when $C_s > 0$
> **and** at least one aperiodic request is pending in the queue.

<!-- mdformat off(reason: keep standard single-line GFM table rows for Markdown previewers) -->
| Scheduling Feature | Pure SSL89 / Buttazzo Fig. 5.17 | Queue-Aware $t_A$ (Implemented Here) |
| :--- | :--- | :--- |
| **Empty-Queue Activation** | Sets $t_A$ when $P_{exe} \ge P_s$ even with an empty queue | Waits until an aperiodic job arrives and executes |
| **Dummy Replenishments** | Can schedule zero-amount replenishment events | Eliminates dummy replenishments |
| **Worst-Case Interference** | Bounded by periodic task $(C_s, T_s)$ (Theorem 5.1) | Identical worst-case bound; lower or equal average interference |
| **Implementation** | Tracks CPU priority transitions even when queue is empty | Event-driven on queue arrival and server dispatch |
<!-- mdformat on -->

## Task Set & Schedulability Proof

### Periodic Task Set and Server Parameters

The default workload runs 6 Rate-Monotonic periodic tasks ($\tau_1 \dots
\tau_6$) and 1 intermediate-priority Sporadic Server ($S_s$):

<!-- mdformat off(reason: keep standard single-line GFM table rows for Markdown previewers) -->
| Task | Priority ($P_i$) | Compute ($C_i$) | Period ($T_i$) | Deadline ($D_i$) | Utilization ($U_i$) | Worst-Case $R_i$ | Schedulable? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| $\tau_1$ | 7 (Highest) | 1.0 | 6.0 | 6.0 | 0.1667 | 1.0 | Yes ($1.0 \le 6.0$) |
| $\tau_2$ | 6 | 1.0 | 10.0 | 10.0 | 0.1000 | 2.0 | Yes ($2.0 \le 10.0$) |
| $\tau_3$ | 5 (Intermediate) | 1.0 | 12.0 | 12.0 | 0.0833 | 3.0 | Yes ($3.0 \le 12.0$) |
| **$S_s$** | **4 (Server)** | **2.0** | **12.0** | **12.0** | **0.1667** | **5.0** | **Yes ($5.0 \le 12.0$)** |
| $\tau_4$ | 3 | 1.5 | 15.0 | 15.0 | 0.1000 | 7.5 | Yes ($7.5 \le 15.0$) |
| $\tau_5$ | 2 | 2.0 | 20.0 | 20.0 | 0.1000 | 9.5 | Yes ($9.5 \le 20.0$) |
| $\tau_6$ | 1 (Lowest) | 2.0 | 30.0 | 30.0 | 0.0667 | 18.0 | Yes ($18.0 \le 30.0$) |
<!-- mdformat on -->

### Processor Utilization

$$
U = \sum_{i=1}^6 \frac{C_i}{T_i} + \frac{C_s}{T_s} = \frac{1}{6} + \frac{1}{10} + \frac{1}{12} + \frac{2}{12} + \frac{1.5}{15} + \frac{2}{20} + \frac{2}{30} = \frac{47}{60} \approx 0.7833 \le 1.0
$$

### Worst-Case Response-Time Analysis (Buttazzo Theorem 5.1)

By Buttazzo Theorem 5.1 (p. 146), a Sporadic Server $(C_s, T_s)$ imposes the
same worst-case interference on lower-priority periodic tasks as a hard periodic
task with compute time $C_s$ and period $T_s$. Using the response-time
recurrence:

$$
R_i^{(k+1)} = C_i + \sum_{j \in hp(i)} \left\lceil \frac{R_i^{(k)}}{T_j} \right\rceil C_j
$$

-   **$\tau_1$**: $R_1 = 1.0 \le 6.0$.
-   **$\tau_2$**: $R_2 = 1.0 + \lceil 2.0 / 6 \rceil (1.0) = 2.0 \le 10.0$.
-   **$\tau_3$**: $R_3 = 1.0 + \lceil 3.0 / 6 \rceil (1.0) + \lceil 3.0 / 10
    \rceil (1.0) = 3.0 \le 12.0$.
-   **$S_s$**: $R_s = 2.0 + 1(1.0) + 1(1.0) + 1(1.0) = 5.0 \le 12.0$.
-   **$\tau_4$**: $R_4^{(0)} = 1.5 \to 6.5 \to 7.5 \le 15.0$.
-   **$\tau_5$**: $R_5^{(0)} = 2.0 \to 8.5 \to 9.5 \le 20.0$.
-   **$\tau_6$**: $R_6^{(0)} = 2.0 \to 10.5 \to 12.5 \to 16.5 \to 18.0 \le
    30.0$.

All 6 periodic tasks and the Sporadic Server meet 100% of their deadlines under
worst-case arrival phasing.

### Aperiodic Workload

<!-- mdformat off(reason: keep standard single-line GFM table rows for Markdown previewers) -->
| Job | Arrival Time ($a_j$) | Compute Time ($e_j$) | Queue Order |
| :--- | :--- | :--- | :--- |
| $J_1$ | 2.0 | 1.0 | FIFO #1 |
| $J_2$ | 5.0 | 1.0 | FIFO #2 |
| $J_3$ | 9.0 | 2.0 | FIFO #3 |
| $J_4$ | 13.0 | 1.0 | FIFO #4 |
| $J_5$ | 17.0 | 1.5 | FIFO #5 |
| $J_6$ | 22.0 | 1.0 | FIFO #6 |
<!-- mdformat on -->

## Ground-Truth Execution Trace ($t \in [0, 30]$)

### Detailed Chronological Event Log

The table below lists every scheduling interval over $t \in [0, 30]$ with step
resolution $\Delta t = 0.1$:

<!-- mdformat off(reason: keep standard single-line GFM table rows for Markdown previewers) -->
| Interval | Dur. | CPU Runner | Queue (Start $\to$ End) | $C_s$ (Start $\to$ End) | Events, Activations ($t_A$), and Replenishments ($t_R$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $[0.0, 1.0]$ | 1.0 | $\tau_1$ | $\emptyset \to \emptyset$ | $2.0 \to 2.0$ | $t=0$: All periodic tasks $\tau_1 \dots \tau_6$ release. $\tau_1$ ($P=7$) runs and finishes. |
| $[1.0, 2.0]$ | 1.0 | $\tau_2$ | $\emptyset \to \emptyset$ | $2.0 \to 2.0$ | $\tau_2$ ($P=6$) runs and finishes. |
| $[2.0, 3.0]$ | 1.0 | $\tau_3$ | $[J_1(1.0)] \to [J_1(1.0)]$ | $2.0 \to 2.0$ | $t=2.0$: $J_1$ arrives. $\tau_3$ ($P=5 > P_s=4$) runs first and finishes. |
| $[3.0, 4.0]$ | 1.0 | $S_s (J_1)$ | $[J_1(1.0)] \to \emptyset$ | $2.0 \to 1.0$ | **$t_{A,1} = 3.0$**. $J_1$ finishes at $4.0$ (queue empty) $\implies$ **$+1.0$ at $t_{R,1} = 15.0$**. |
| $[4.0, 5.0]$ | 1.0 | $\tau_4$ | $\emptyset \to \emptyset$ | $1.0 \to 1.0$ | $\tau_4$ runs $1.0$ of $1.5$ units ($0.5$ remaining). |
| $[5.0, 6.0]$ | 1.0 | $S_s (J_2)$ | $[J_2(1.0)] \to \emptyset$ | $1.0 \to 0.0$ | $t=5.0$: $J_2$ arrives, preempts $\tau_4$. **$t_{A,2} = 5.0$**. $J_2$ finishes & $C_s=0 \implies$ **$+1.0$ at $t_{R,2} = 17.0$**. |
| $[6.0, 7.0]$ | 1.0 | $\tau_1$ | $\emptyset \to \emptyset$ | $0.0 \to 0.0$ | $t=6.0$: $\tau_1$ releases and finishes. |
| $[7.0, 7.5]$ | 0.5 | $\tau_4$ | $\emptyset \to \emptyset$ | $0.0 \to 0.0$ | $\tau_4$ finishes remaining $0.5$ units at $t=7.5$. |
| $[7.5, 9.5]$ | 2.0 | $\tau_5$ | $\emptyset \to [J_3(2.0)]$ | $0.0 \to 0.0$ | $\tau_5$ runs $2.0$ units and finishes. $t=9.0$: $J_3$ arrives while $C_s=0$ ($S_s$ suspended). |
| $[9.5, 10.0]$ | 0.5 | $\tau_6$ | $[J_3(2.0)] \to [J_3(2.0)]$ | $0.0 \to 0.0$ | $\tau_6$ runs $0.5$ of $2.0$ units ($1.5$ remaining; $S_s$ suspended). |
| $[10.0, 11.0]$ | 1.0 | $\tau_2$ | $[J_3(2.0)] \to [J_3(2.0)]$ | $0.0 \to 0.0$ | $t=10.0$: $\tau_2$ releases, preempts $\tau_6$, and finishes. |
| $[11.0, 12.0]$ | 1.0 | $\tau_6$ | $[J_3(2.0)] \to [J_3(2.0)]$ | $0.0 \to 0.0$ | $\tau_6$ resumes for $1.0$ unit ($0.5$ remaining; $S_s$ suspended). |
| $[12.0, 13.0]$ | 1.0 | $\tau_1$ | $[J_3(2.0)] \to [J_3(2.0)]$ | $0.0 \to 0.0$ | $t=12.0$: $\tau_1, \tau_3$ release. $\tau_1$ runs and finishes. |
| $[13.0, 14.0]$ | 1.0 | $\tau_3$ | $[J_3(2.0), J_4(1.0)]$ | $0.0 \to 0.0$ | $t=13.0$: $J_4$ arrives while $C_s=0$. $\tau_3$ runs and finishes. |
| $[14.0, 14.5]$ | 0.5 | $\tau_6$ | $[J_3(2.0), J_4(1.0)]$ | $0.0 \to 0.0$ | $\tau_6$ finishes its remaining $0.5$ units at $t=14.5 \le 30.0$. |
| $[14.5, 15.0]$ | 0.5 | Idle | $[J_3(2.0), J_4(1.0)]$ | $0.0 \to 0.0$ | CPU idle ($S_s$ suspended, all released periodic jobs complete). |
| $[15.0, 16.0]$ | 1.0 | $S_s (J_3)$ | $[J_3(2.0), J_4(1.0)] \to [J_3(1.0), J_4(1.0)]$ | $1.0 \to 0.0$ | $t=15.0$: **$RA_1 = +1.0$ arrives** ($C_s=1$); $\tau_4$ releases. **$t_{A,3} = 15.0$**. Runs $1.0$ of $J_3$. $C_s=0 \implies$ **$+1.0$ at $t_{R,3} = 27.0$**. |
| $[16.0, 17.0]$ | 1.0 | $\tau_4$ | $[J_3(1.0), J_4(1.0)]$ | $0.0 \to 0.0$ | $\tau_4$ runs $1.0$ of $1.5$ units ($0.5$ remaining). $t=17.0$: $J_5$ arrives. |
| $[17.0, 18.0]$ | 1.0 | $S_s (J_3)$ | $[J_3(1.0), J_4(1.0), J_5(1.5)] \to [J_4(1.0), J_5(1.5)]$ | $1.0 \to 0.0$ | $t=17.0$: **$RA_2 = +1.0$ arrives** ($C_s=1$). **$t_{A,4} = 17.0$**. Preempts $\tau_4$, finishes $J_3$. $C_s=0 \implies$ **$+1.0$ at $t_{R,4} = 29.0$**. |
| $[18.0, 19.0]$ | 1.0 | $\tau_1$ | $[J_4(1.0), J_5(1.5)]$ | $0.0 \to 0.0$ | $t=18.0$: $\tau_1$ releases and finishes. |
| $[19.0, 19.5]$ | 0.5 | $\tau_4$ | $[J_4(1.0), J_5(1.5)]$ | $0.0 \to 0.0$ | $\tau_4$ finishes remaining $0.5$ units at $t=19.5 \le 30.0$. |
| $[19.5, 20.0]$ | 0.5 | Idle | $[J_4(1.0), J_5(1.5)]$ | $0.0 \to 0.0$ | CPU idle ($S_s$ suspended). |
| $[20.0, 21.0]$ | 1.0 | $\tau_2$ | $[J_4(1.0), J_5(1.5)]$ | $0.0 \to 0.0$ | $t=20.0$: $\tau_2, \tau_5$ release. $\tau_2$ runs and finishes. |
| $[21.0, 23.0]$ | 2.0 | $\tau_5$ | $[J_4(1.0), J_5(1.5), J_6(1.0)]$ | $0.0 \to 0.0$ | $\tau_5$ runs $2.0$ units and finishes. $t=22.0$: $J_6$ arrives while $C_s=0$. |
| $[23.0, 24.0]$ | 1.0 | Idle | $[J_4(1.0), J_5(1.5), J_6(1.0)]$ | $0.0 \to 0.0$ | CPU idle ($S_s$ suspended). |
| $[24.0, 25.0]$ | 1.0 | $\tau_1$ | $[J_4(1.0), J_5(1.5), J_6(1.0)]$ | $0.0 \to 0.0$ | $t=24.0$: $\tau_1, \tau_3$ release. $\tau_1$ runs and finishes. |
| $[25.0, 26.0]$ | 1.0 | $\tau_3$ | $[J_4(1.0), J_5(1.5), J_6(1.0)]$ | $0.0 \to 0.0$ | $\tau_3$ runs and finishes. |
| $[26.0, 27.0]$ | 1.0 | Idle | $[J_4(1.0), J_5(1.5), J_6(1.0)]$ | $0.0 \to 0.0$ | CPU idle ($S_s$ suspended). |
| $[27.0, 28.0]$ | 1.0 | $S_s (J_4)$ | $[J_4(1.0), J_5(1.5), J_6(1.0)] \to [J_5(1.5), J_6(1.0)]$ | $1.0 \to 0.0$ | $t=27.0$: **$RA_3 = +1.0$ arrives** ($C_s=1$). **$t_{A,5} = 27.0$**. Finishes $J_4$. $C_s=0 \implies$ **$+1.0$ at $t_{R,5} = 39.0$**. |
| $[28.0, 29.0]$ | 1.0 | Idle | $[J_5(1.5), J_6(1.0)]$ | $0.0 \to 0.0$ | CPU idle ($S_s$ suspended). |
| $[29.0, 30.0]$ | 1.0 | $S_s (J_5)$ | $[J_5(1.5), J_6(1.0)] \to [J_5(0.5), J_6(1.0)]$ | $1.0 \to 0.0$ | $t=29.0$: **$RA_4 = +1.0$ arrives** ($C_s=1$). **$t_{A,6} = 29.0$**. Runs $1.0$ of $J_5$. $C_s=0 \implies$ **$+1.0$ at $t_{R,6} = 41.0$**. |
<!-- mdformat on -->

### Summary of Activations and Replenishments

<!-- mdformat off(reason: keep standard single-line GFM table rows for Markdown previewers) -->
| Activation # | $t_A$ | Active Window | Jobs Serviced | Consumed ($RA$) | Reason Window Closed | Replenishment ($t_R = t_A + 12$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 3.0 | $[3.0, 4.0]$ | $J_1$ (1.0) | 1.0 | Queue empty | 15.0 (+1.0) |
| 2 | 5.0 | $[5.0, 6.0]$ | $J_2$ (1.0) | 1.0 | Budget exhausted ($C_s = 0$) | 17.0 (+1.0) |
| 3 | 15.0 | $[15.0, 16.0]$ | $J_3$ (1.0 of 2.0) | 1.0 | Budget exhausted ($C_s = 0$) | 27.0 (+1.0) |
| 4 | 17.0 | $[17.0, 18.0]$ | $J_3$ (1.0 of 2.0) | 1.0 | Budget exhausted ($C_s = 0$) | 29.0 (+1.0) |
| 5 | 27.0 | $[27.0, 28.0]$ | $J_4$ (1.0) | 1.0 | Budget exhausted ($C_s = 0$) | 39.0 (+1.0) |
| 6 | 29.0 | $[29.0, 30.0]$ | $J_5$ (1.0 of 1.5) | 1.0 | Budget exhausted ($C_s = 0$) | 41.0 (+1.0) |
<!-- mdformat on -->

### Processor Time Conservation Check

$$
\text{Total Time} = \tau_1(5.0) + \tau_2(3.0) + \tau_3(3.0) + \tau_4(3.0) + \tau_5(4.0) + \tau_6(2.0) + S_s(6.0) + \text{Idle}(4.0) = 30.0
$$

All 6 periodic tasks finish with 0 deadline misses over $t \in [0, 30]$.

## Numerical Precision & Visual Design

### Integer-Tick Arithmetic

Stepping time with floating-point increments (`t += dt`) accumulates IEEE-754
error (`0.1 + 0.2 != 0.3`). To stay deterministic, `sporadic_server_sim.py`
converts all time values to integer ticks:

```python
def to_ticks(val: float, dt: float) -> int:
  return int(round(val / dt))
```

With $\Delta t = 0.1$, time $28.5$ maps to integer tick `285`, so period checks
(`k % period_ticks == 0`) and replenishment checks (`k == r_tick`) never drift.

### Buttazzo Chapter 5 Visual Hierarchy

The plot layout follows Buttazzo Figures 5.17 and 5.18:

```text
+-------------------------------------------------------------+
|  Title & 2-Row Legend (Tasks + Server + Arrow Markers)     |
|                                                             |
|  [tau_1]  (P=7, highest priority, top row)                  |
|  [tau_2]  (P=6)                                             |
|  [tau_3]  (P=5, intermediate periodic task)                 |
|  [tau_4]  (P=3)                                             |
|  [tau_5]  (P=2)                                             |
|  [tau_6]  (P=1, lowest periodic task)                       |
|  [S_s ]   (P=4, bottom row directly above budget curve)     |
|    :                                   :                    |
|    : (dotted guidelines at t_A, t_I)   : (dashed at t_R)    |
|    v                                   v                    |
+-------------------------------------------------------------+
|  [C_s(t)] Server Capacity Step-Plot & Slanted t_A->t_R Pointers |
+-------------------------------------------------------------+
```

-   **Priority Layout**: Periodic tasks are stacked at the top in descending
    priority order, while the Sporadic Server ($S_s$) sits on the bottom row
    ($y = 0.0$) directly above the budget curve.
-   **Guideline Connections**: Vertical dotted lines connect activation instants
    ($t_A$) and window closing instants ($t_I$) from the $S_s$ track down into
    the capacity plot.
-   **Replenishment Pointers**: Slanted dotted arrows point from $(t_A,
    C_{s,\max})$ to $(t_R, C_s)$ with `+{amount}` labels.
-   **Offset Coinciding Arrows**: When a periodic release and deadline fall on
    the same timestamp ($t = 6, 10, 12, 18, 20, 24$), the release arrow is
    offset by $-0.08$ and the deadline arrow by $+0.08$ so both stay visible.

## Expert Evaluation Checklist & Test Coverage

Each theoretical property is verified by a unit test in
`sporadic_server_sim_test.py`:

<!-- mdformat off(reason: keep standard single-line GFM table rows for Markdown previewers) -->
| Invariant / Theoretical Property | Implementation Location | Unit Test Method | Status |
| :--- | :--- | :--- | :--- |
| **0 Periodic Deadline Misses** | `run_simulation` | `test_no_periodic_deadline_misses` | Pass |
| **Exact CPU Utilization** | `run_simulation` | `test_exact_cpu_utilization_totals` | Pass |
| **Activation Instants ($t_A$)** | `run_simulation` | `test_exact_activation_times` | Pass |
| **Replenishment Timing ($t_R = t_A + T_s$)** | `run_simulation` | `test_exact_replenishment_times_and_amounts` | Pass |
| **Mid-Window Preemption Preservation** | `run_simulation` | `test_sporadic_server_preemption_preserves_activation_window` | Pass |
| **Aperiodic FIFO Execution** | `run_simulation` | `test_aperiodic_jobs_completion_status` | Pass |
| **Figure Generation** | `plot_simulation` | `test_plot_simulation_generates_image` | Pass |
| **RTA & QoS Metrics Verification** | `compute_schedulability` | `test_schedulability_and_rta_analysis` | Pass |
| **CSV & JSON Trace Exporters** | `export_trace_to_csv/json` | `test_export_csv_and_json` | Pass |
| **Interactive HTML Dashboard** | `export_interactive_html` | `test_export_interactive_html` | Pass |
<!-- mdformat on -->

## How to Run, Test, and Customize

### Run the Simulation and Visualization

```bash
# Run simulation and view interactive Matplotlib window (with hover tooltips)
uv run --with matplotlib sporadic_server_sim.py

# Run in headless mode and generate both PNG (300 DPI) and interactive HTML:
uv run --with matplotlib sporadic_server_sim.py --no-show

# Open the interactive HTML dashboard in your browser (macOS):
open sporadic_server_interactive.html

# Export execution trace to CSV and JSON:
uv run --with matplotlib sporadic_server_sim.py --no-show --export-csv execution_trace.csv --export-json simulation_data.json
```

### Run the Unit Test Suite

```bash
uv run --with matplotlib python -m unittest sporadic_server_sim_test.py
```

### Customize Tasks & Server Parameters

Edit `PERIODIC_TASKS`, `SERVER_CONFIG`, or `APERIODIC_JOBS` at the top of
`sporadic_server_sim.py`:

```python
PERIODIC_TASKS = [
    PeriodicTask(name=r"$\tau_1$", priority=7, compute_time=1.0, deadline=6.0, period=6.0, color="#0072B2"),
    ...
]

SERVER_CONFIG = SporadicServerConfig(
    name=r"$S_s$", priority=4, budget=2.0, period=12.0, deadline=12.0, color="#16a085"
)
```
