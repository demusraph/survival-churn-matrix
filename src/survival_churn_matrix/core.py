import numpy as np
from scipy import stats
from typing import List, Tuple
from .models import Event, SurvivalPoint

class KaplanMeierEstimator:
    """
    Computes the Kaplan-Meier survival function: S(t) = Product(1 - d_i / n_i)
    with Greenwood's formula for confidence intervals.
    """
    
    @staticmethod
    def compute(events: List[Event]) -> List[SurvivalPoint]:
        # Convert to structured numpy array for vectorized processing
        data = np.array([(e.time, int(e.event_observed)) for e in events], 
                        dtype=[('time', 'f8'), ('observed', 'i4')])
        
        # Sort by time
        data = np.sort(data, order='time')
        
        times = np.unique(data['time'])
        n = len(data)
        
        survival_probs = []
        current_s = 1.0
        var_s = 0.0
        
        for t in times:
            # Number at risk
            n_i = np.sum(data['time'] >= t)
            # Number of events at time t
            d_i = np.sum((data['time'] == t) & (data['observed'] == 1))
            
            if n_i > 0:
                # Greenwood's formula for variance
                if d_i > 0 and n_i > d_i:
                    var_s += d_i / (n_i * (n_i - d_i))
                
                current_s *= (1 - d_i / n_i)
            
            # 95% Confidence Interval
            se = current_s * np.sqrt(var_s)
            ci_lower = max(0, current_s - 1.96 * se)
            ci_upper = min(1, current_s + 1.96 * se)
            
            survival_probs.append(SurvivalPoint(
                time=float(t),
                survival_probability=float(current_s),
                confidence_interval_lower=float(ci_lower),
                confidence_interval_upper=float(ci_upper)
            ))
            
        return survival_probs

class LogRankTest:
    """
    Performs the Log-Rank test to compare two cohorts.
    """
    
    @staticmethod
    def compare(cohort_a: List[Event], cohort_b: List[Event]) -> float:
        # Implementation of the Mantel-Haenszel test statistic
        all_times = sorted(list(set([e.time for e in cohort_a + cohort_b])))
        
        obs_a, exp_a = 0.0, 0.0
        var_sum = 0.0
        
        for t in all_times:
            n_a = sum(1 for e in cohort_a if e.time >= t)
            n_b = sum(1 for e in cohort_b if e.time >= t)
            d_a = sum(1 for e in cohort_a if e.time == t and e.event_observed)
            d_b = sum(1 for e in cohort_b if e.time == t and e.event_observed)
            
            n_total = n_a + n_b
            d_total = d_a + d_b
            
            if n_total > 1:
                exp_a += (n_a / n_total) * d_total
                var_sum += (n_a * n_b * d_total * (n_total - d_total)) / (n_total**2 * (n_total - 1))
                obs_a += d_a
        
        z = (obs_a - exp_a) / np.sqrt(var_sum) if var_sum > 0 else 0
        return float(2 * (1 - stats.norm.cdf(abs(z))))