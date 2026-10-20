"""Unit tests for the Sporadic Server (SS) simulation and visualization."""

import os
import tempfile
import unittest

import sporadic_server_sim


class SporadicServerSimTest(unittest.TestCase):
  """Validates the exact Sporadic Server execution trace and visualization."""

  def setUp(self):
    super().setUp()
    self.result = sporadic_server_sim.run_simulation(
        horizon=sporadic_server_sim.SIMULATION_HORIZON,
        dt=sporadic_server_sim.DT,
        periodic_tasks=sporadic_server_sim.PERIODIC_TASKS,
        server_config=sporadic_server_sim.SERVER_CONFIG,
        aperiodic_jobs=sporadic_server_sim.APERIODIC_JOBS,
    )

  def test_no_periodic_deadline_misses(self):
    """Verifies that all periodic deadlines are met."""
    self.assertEqual(self.result.deadline_misses, [])

  def test_exact_cpu_utilization_totals(self):
    """Verifies total CPU execution times for the 6-task RM workload."""
    cpu_totals = self.result.cpu_totals
    self.assertAlmostEqual(cpu_totals.get(r"$\tau_1$", 0.0), 5.0, places=3)
    self.assertAlmostEqual(cpu_totals.get(r"$\tau_2$", 0.0), 3.0, places=3)
    self.assertAlmostEqual(cpu_totals.get(r"$\tau_3$", 0.0), 3.0, places=3)
    self.assertAlmostEqual(cpu_totals.get(r"$\tau_4$", 0.0), 3.0, places=3)
    self.assertAlmostEqual(cpu_totals.get(r"$\tau_5$", 0.0), 4.0, places=3)
    self.assertAlmostEqual(cpu_totals.get(r"$\tau_6$", 0.0), 2.0, places=3)
    self.assertAlmostEqual(cpu_totals.get(r"$S_s$", 0.0), 6.0, places=3)
    self.assertAlmostEqual(cpu_totals.get("Idle", 0.0), 4.0, places=3)
    total_time = sum(cpu_totals.values())
    self.assertAlmostEqual(total_time, 30.0, places=3)

  def test_exact_activation_times(self):
    """Verifies the 6 activation instants t_A."""
    expected_activations = [3.0, 5.0, 15.0, 17.0, 27.0, 29.0]
    actual_activations = [a.activation_time for a in self.result.activations]
    self.assertEqual(len(actual_activations), len(expected_activations))
    for actual, expected in zip(actual_activations, expected_activations):
      self.assertAlmostEqual(actual, expected, places=3)

  def test_exact_replenishment_times_and_amounts(self):
    """Verifies the 6 scheduled replenishment events (t_R, amount)."""
    expected_replenishments = [
        (15.0, 1.0),
        (17.0, 1.0),
        (27.0, 1.0),
        (29.0, 1.0),
        (39.0, 1.0),
        (41.0, 1.0),
    ]
    actual_replenishments = [
        (r.replenishment_time, r.amount) for r in self.result.replenishments
    ]
    self.assertEqual(len(actual_replenishments), len(expected_replenishments))
    for (act_t, act_amt), (exp_t, exp_amt) in zip(
        actual_replenishments, expected_replenishments
    ):
      self.assertAlmostEqual(act_t, exp_t, places=3)
      self.assertAlmostEqual(act_amt, exp_amt, places=3)

  def test_aperiodic_jobs_completion_status(self):
    """Verifies aperiodic job completions and remaining compute times."""
    records = self.result.job_records
    self.assertAlmostEqual(records["J1"].completion_time, 4.0, places=3)
    self.assertAlmostEqual(records["J2"].completion_time, 6.0, places=3)
    self.assertAlmostEqual(records["J3"].completion_time, 18.0, places=3)
    self.assertAlmostEqual(records["J4"].completion_time, 28.0, places=3)

    self.assertIsNone(records["J5"].completion_time)
    self.assertAlmostEqual(records["J5"].remaining_time, 0.5, places=3)

    self.assertIsNone(records["J6"].completion_time)
    self.assertAlmostEqual(records["J6"].remaining_time, 1.0, places=3)

  def test_sporadic_server_preemption_preserves_activation_window(self):
    """Verifies preemption by higher priority task preserves active window."""
    tau1 = sporadic_server_sim.PeriodicTask(
        name=r"$\tau_1$",
        priority=3,
        compute_time=2.0,
        deadline=6.0,
        period=6.0,
        color="#1f4e79",
    )
    server = sporadic_server_sim.SporadicServerConfig(
        name=r"$S_s$",
        priority=2,
        budget=2.0,
        period=8.0,
        deadline=8.0,
        color="#16a085",
    )
    job = sporadic_server_sim.AperiodicJob(
        "J_preempt", arrival_time=5.0, compute_time=2.0
    )

    result = sporadic_server_sim.run_simulation(
        horizon=15.0,
        dt=0.1,
        periodic_tasks=[tau1],
        server_config=server,
        aperiodic_jobs=[job],
    )

    # Ss runs [5, 6], preempted by tau1 [6, 8], resumes [8, 9], finishes at 9.0
    self.assertEqual(len(result.activations), 1)
    act = result.activations[0]
    self.assertAlmostEqual(act.activation_time, 5.0, places=3)
    self.assertAlmostEqual(act.closed_time, 9.0, places=3)
    self.assertAlmostEqual(act.amount_consumed, 2.0, places=3)

    # Full replenishment (2.0) occurs at t_R = 5.0 + 8.0 = 13.0
    self.assertEqual(len(result.replenishments), 1)
    repl = result.replenishments[0]
    self.assertAlmostEqual(repl.replenishment_time, 13.0, places=3)
    self.assertAlmostEqual(repl.amount, 2.0, places=3)

    # Job completed at 9.0
    self.assertAlmostEqual(
        result.job_records["J_preempt"].completion_time, 9.0, places=3
    )

  def test_plot_simulation_generates_image(self):
    """Verifies plot_simulation generates a non-empty PNG file."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
      tmp_path = tmp_file.name

    try:
      sporadic_server_sim.plot_simulation(
          self.result,
          output_path=tmp_path,
          show=False,
      )
      self.assertTrue(os.path.exists(tmp_path))
      self.assertGreater(os.path.getsize(tmp_path), 1000)
    finally:
      if os.path.exists(tmp_path):
        os.remove(tmp_path)

  def test_schedulability_and_rta_analysis(self):
    """Verifies theoretical RTA and utilization bounds (Point 5)."""
    sched = self.result.schedulability
    self.assertIsNotNone(sched)
    self.assertAlmostEqual(sched.utilization_periodic, 37.0 / 60.0, places=3)
    self.assertAlmostEqual(sched.utilization_server, 2.0 / 12.0, places=3)
    self.assertAlmostEqual(sched.utilization_total, 47.0 / 60.0, places=3)
    self.assertTrue(sched.all_schedulable)

    rta_dict = {tm.name: tm.response_time for tm in sched.task_metrics}
    self.assertAlmostEqual(rta_dict[r"$\tau_1$"], 1.0, places=3)
    self.assertAlmostEqual(rta_dict[r"$\tau_2$"], 2.0, places=3)
    self.assertAlmostEqual(rta_dict[r"$\tau_3$"], 3.0, places=3)
    self.assertAlmostEqual(rta_dict[r"$S_s$"], 5.0, places=3)
    self.assertAlmostEqual(rta_dict[r"$\tau_4$"], 7.5, places=3)
    self.assertAlmostEqual(rta_dict[r"$\tau_5$"], 9.5, places=3)
    self.assertAlmostEqual(rta_dict[r"$\tau_6$"], 18.0, places=3)

    self.assertAlmostEqual(sched.avg_aperiodic_response_time, 6.75, places=2)
    self.assertAlmostEqual(sched.max_aperiodic_response_time, 15.0, places=2)

  def test_export_csv_and_json(self):
    """Verifies trace export to CSV and JSON (Point 4)."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_csv:
      csv_path = tmp_csv.name
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_json:
      json_path = tmp_json.name

    try:
      sporadic_server_sim.export_trace_to_csv(self.result, csv_path)
      self.assertTrue(os.path.exists(csv_path))
      self.assertGreater(os.path.getsize(csv_path), 100)

      sporadic_server_sim.export_trace_to_json(self.result, json_path)
      self.assertTrue(os.path.exists(json_path))
      self.assertGreater(os.path.getsize(json_path), 100)
    finally:
      if os.path.exists(csv_path):
        os.remove(csv_path)
      if os.path.exists(json_path):
        os.remove(json_path)

  def test_export_interactive_html(self):
    """Verifies interactive dashboard HTML export."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_html:
      html_path = tmp_html.name

    try:
      sporadic_server_sim.export_interactive_html(self.result, html_path)
      self.assertTrue(os.path.exists(html_path))
      self.assertGreater(os.path.getsize(html_path), 500)
    finally:
      if os.path.exists(html_path):
        os.remove(html_path)


if __name__ == "__main__":
  unittest.main()
