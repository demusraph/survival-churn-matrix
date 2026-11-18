import unittest
from pydantic import ValidationError
from src.survival_churn_matrix.models import Event, CohortRequest

class TestValidation(unittest.TestCase):
    """
    Exhaustive validation suite for survival-churn-matrix schema enforcement.
    """

    def test_event_valid_input(self):
        """Test successful instantiation of a valid Event."""
        event = Event(customer_id="user_1", time=10.5, event_observed=True)
        self.assertEqual(event.customer_id, "user_1")
        self.assertEqual(event.time, 10.5)
        self.assertTrue(event.event_observed)

    def test_event_invalid_time_zero(self):
        """Test that time must be strictly greater than 0."""
        with self.assertRaises(ValidationError):
            Event(customer_id="user_1", time=0.0, event_observed=True)

    def test_event_invalid_time_negative(self):
        """Test that negative time raises validation error."""
        with self.assertRaises(ValidationError):
            Event(customer_id="user_1", time=-5.0, event_observed=True)

    def test_event_missing_fields(self):
        """Test that missing required fields raise ValidationError."""
        with self.assertRaises(ValidationError):
            Event(customer_id="user_1")

    def test_cohort_request_valid(self):
        """Test successful instantiation of a valid CohortRequest."""
        events = [Event(customer_id="u1", time=1.0, event_observed=False)]
        cohort = CohortRequest(cohort_id="c1", events=events)
        self.assertEqual(len(cohort.events), 1)
        self.assertEqual(cohort.cohort_id, "c1")

    def test_cohort_request_empty_events(self):
        """Test that empty events list triggers custom validator."""
        with self.assertRaises(ValidationError) as cm:
            CohortRequest(cohort_id="c1", events=[])
        self.assertIn("Cohort must contain at least one event.", str(cm.exception))

    def test_cohort_request_invalid_event_type(self):
        """Test that invalid event data inside list triggers validation."""
        with self.assertRaises(ValidationError):
            CohortRequest(cohort_id="c1", events=[{"customer_id": "u1", "time": -1, "event_observed": True}])

    def test_event_type_coercion(self):
        """Test that valid numeric strings are coerced to floats."""
        event = Event(customer_id="u1", time="10", event_observed=1)
        self.assertEqual(event.time, 10.0)
        self.assertTrue(event.event_observed)

    def test_cohort_request_multiple_events(self):
        """Test cohort with multiple valid events."""
        events = [
            Event(customer_id="u1", time=1.0, event_observed=True),
            Event(customer_id="u2", time=2.0, event_observed=False)
        ]
        cohort = CohortRequest(cohort_id="c1", events=events)
        self.assertEqual(len(cohort.events), 2)
        self.assertEqual(cohort.events[1].time, 2.0)

    def test_event_boolean_coercion(self):
        """Test that truthy/falsy values are coerced to bool."""
        event = Event(customer_id="u1", time=5.0, event_observed=0)
        self.assertFalse(event.event_observed)
        event2 = Event(customer_id="u2", time=5.0, event_observed=1)
        self.assertTrue(event2.event_observed)

if __name__ == "__main__":
    unittest.main()