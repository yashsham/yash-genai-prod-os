from abc import ABC, abstractmethod

class ExecutionSandbox(ABC):
    """
    Interface for sandboxed execution of agent code/tools.
    """

    @abstractmethod
    def execute_code(self, code: str, language: str) -> str:
        """
        Executes code in an isolated environment (e.g., Docker container, gVisor).
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        Destroys the sandbox environment after execution.
        """
        pass

import subprocess

class SubprocessMockSandbox(ExecutionSandbox):
    """
    MOCK Sandbox: Runs code using local subprocess (INSECURE for production).
    Real implementation would use Docker/gVisor.
    """

    def execute_code(self, code: str, language: str) -> str:
        if language != "python":
            return "Error: Only python supported in mock."
        
        try:
            # Dangerous in real life, okay for structure demo
            result = subprocess.run(
                ["python", "-c", code], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "Error: Execution timed out."

    def cleanup(self):
        print("Mock sandbox cleanup: nothing to do.")
