from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

class SecurityAuditLogger(ABC):
    """
    Interface for immutable security logging.
    Ensures that all security-critical events (auth failures, prompt injections) are logged.
    """

    @abstractmethod
    def log_event(self, event_type: str, severity: str, details: Dict[str, Any], user_id: str = None):
        """
        Logs a security event.
        params:
            event_type: e.g., 'INJECTION_ATTEMPT', 'UNAUTHORIZED_ACCESS'
            severity: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
            details: Contextual data
            user_id: Actor identifier
        """
        pass

import json
import time

class ConsoleJSONLogger(SecurityAuditLogger):
    """
    Logs security events to STDOUT in structured JSON format.
    Ideal for ingestion by Splunk/Datadog.
    """

    def log_event(self, event_type: str, severity: str, details: Dict[str, Any], user_id: str = None):
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id or "anonymous",
            "details": details
        }
        print(json.dumps(log_entry))
