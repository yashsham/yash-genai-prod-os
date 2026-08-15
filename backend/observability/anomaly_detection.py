from abc import ABC, abstractmethod

class AnomalyDetector(ABC):
    """
    Interface for detecting anomalous usage patterns.
    """

    @abstractmethod
    def detect(self, metric: str, value: float, context: str) -> bool:
        """
        Checks if a metric value is anomalous given the context.
        returns:
             True if anomalous (requires alert), False otherwise.
        """
        pass

class ThresholdDetector(AnomalyDetector):
    """
    Simple threshold-based anomaly detection.
    """
    
    THRESHOLDS = {
        "requests_per_minute": 100,
        "token_usage": 50000
    }

    def detect(self, metric: str, value: float, context: str) -> bool:
        limit = self.THRESHOLDS.get(metric, float('inf'))
        if value > limit:
            return True
        return False
