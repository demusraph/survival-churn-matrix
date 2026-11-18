import unittest
import numpy as np
from src.survival_churn_matrix.models import Event, CohortRequest
from src.survival_churn_matrix.core import KaplanMeierEstimator, LogRankTest

class TestBoundaries(unittest.TestCase):
    """
    Exhaustive boundary condition testing for SurvivalChurn Matrix core logic.
    """

    def test_single_event_survival(self):
        """Test behavior with exactly one event."""
        events = [Event(customer_id="1", time=10.0, event_observed=True)]
        result = KaplanMeierEstimator.compute(events)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].survival_probability, 0.0)

    def test_all_censored_events(self):
        """Test survival probability remains 1.0 when no events are observed."""
        events = [
            Event(customer_id="1", time=10.0, event_observed=False),
            Event(customer_id="2", time=20.0, event_observed=False)
        ]
        result = KaplanMeierEstimator.compute(events)
        for point in result:
            self.assertEqual(point.survival_probability, 1.0)

    def test_zero_time_boundary(self):
        """Ensure Pydantic validation catches non-positive time."""
        with self.assertRaises(ValueError):
            Event(customer_id="err", time=0.0, event_observed=True)

    def test_empty_cohort_validation(self):
        """Ensure CohortRequest rejects empty event lists."""
        with self.assertRaises(ValueError):
            CohortRequest(cohort_id="test", events=[])

    def test_identical_time_events(self):
        """Test handling of multiple events occurring at the exact same time."""
        events = [
            Event(customer_id="1", time=5.0, event_observed=True),
            Event(customer_id="2", time=5.0, event_observed=True)
        ]
        result = KaplanMeierEstimator.compute(events)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].survival_probability, 0.0)

    def test_log_rank_identical_cohorts(self):
        """Log-rank test for identical cohorts should return p-value of 1.0."""
        cohort = [Event(customer_id="1", time=10.0, event_observed=True)]
        p_val = LogRankTest.compare(cohort, cohort)
        self.assertEqual(p_val, 1.0)

    def test_log_rank_zero_variance(self):
        """Test log-rank stability when variance is zero."""
        cohort_a = [Event(customer_id="1", time=10.0, event_observed=False)]
        cohort_b = [Event(customer_id="2", time=10.0, event_observed=False)]
        p_val = LogRankTest.compare(cohort_a, cohort_b)
        self.assertEqual(p_val, 1.0)

    def test_confidence_interval_bounds(self):
        """Verify CI bounds are clamped between 0 and 1."""
        events = [Event(customer_id="1", time=1.0, event_observed=True)]
        result = KaplanMeierEstimator.compute(events)
        self.assertGreaterEqual(result[0].confidence_interval_lower, 0.0)
        self.assertLessEqual(result[0].confidence_interval_upper, 1.0)

    def test_mixed_censoring_and_events(self):
        """Test survival curve calculation with mixed event types."""
        events = [
            Event(customer_id="1", time=10.0, event_observed=True),
            Event(customer_id="2", time=10.0, event_observed=False)
        ]
        result = KaplanMeierEstimator.compute(events)
        # 1 event, 1 censored at t=10. n=2, d=1. S(10) = 1 - 1/2 = 0.5
        self.assertEqual(result[0].survival_probability, 0.5)

    def test_large_time_gaps(self):
        """Test stability with non-sequential, large time gaps."""
        events = [
            Event(customer_id="1", time=1.0, event_observed=True),
            Event(customer_id="2", time=1000.0, event_observed=True)
        ]
        result = KaplanMeierEstimator.compute(events)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1].survival_probability, 0.0)

if __name__ == "__main__":
    unittest.main()