import time
from typing import Dict, Any, Tuple
from enum import Enum

class CircuitState(Enum):
    CLOSED = "CLOSED"       # Normal operation
    HALF_OPEN = "HALF_OPEN" # Soft limit breach (80%-95% budget utilization): route to cheap model / trim context
    OPEN = "OPEN"           # Hard limit breach or anomaly spike: block requests

class CostCircuitBreaker:
    """
    Automated Financial Circuit Breaker & Velocity Tripwire Safeguard.
    Prevents Denial-of-Wallet (DoW) attacks, infinite loops, and runaway bills.
    """
    
    def __init__(self, soft_limit_percent: float = 0.80, hard_limit_percent: float = 1.00):
        self.state = CircuitState.CLOSED
        self.soft_limit_percent = soft_limit_percent
        self.hard_limit_percent = hard_limit_percent
        
        # Velocity tracking: spend timestamps in last 10 minutes
        self.recent_spend_events = [] # list of (timestamp, amount)
        self.velocity_threshold_usd_per_min = 5.00 # max $5/min velocity

    def evaluate_state(self, current_spend: float, budget_limit: float) -> Tuple[CircuitState, str]:
        """
        Evaluates current budget utilization against soft and hard thresholds.
        """
        utilization = current_spend / budget_limit if budget_limit > 0 else 0.0
        
        # Velocity check: sum spend in last 60 seconds
        now = time.time()
        self.recent_spend_events = [(t, amt) for t, amt in self.recent_spend_events if now - t < 60]
        recent_velocity = sum(amt for t, amt in self.recent_spend_events)

        if recent_velocity > self.velocity_threshold_usd_per_min:
            self.state = CircuitState.OPEN
            return CircuitState.OPEN, f"TRIPWIRE: Spend velocity alert (${recent_velocity:.2f}/min > limit ${self.velocity_threshold_usd_per_min:.2f}/min)"

        if utilization >= self.hard_limit_percent:
            self.state = CircuitState.OPEN
            return CircuitState.OPEN, f"Hard limit reached (100% budget utilized: ${current_spend:.2f} / ${budget_limit:.2f})"

        if utilization >= self.soft_limit_percent:
            self.state = CircuitState.HALF_OPEN
            return CircuitState.HALF_OPEN, f"Soft limit breach ({utilization*100:.1f}% budget utilized). Degrading to cost-effective models."

        self.state = CircuitState.CLOSED
        return CircuitState.CLOSED, "Normal operating conditions."

    def record_spend(self, amount: float):
        """
        Records spend event timestamp for real-time velocity monitoring.
        """
        self.recent_spend_events.append((time.time(), amount))
