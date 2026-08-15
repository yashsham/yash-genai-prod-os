from abc import ABC, abstractmethod

class DataEncryptionPolicy(ABC):
    """
    Interface for defining data encryption standards and key management integration.
    """

    @abstractmethod
    def get_encryption_config(self) -> dict:
        """
        Returns the required encryption configuration (algorithm, key rotation policy).
        """
        pass
        
    @abstractmethod
    def encrypt_field(self, data: str) -> str:
        """
        Encrypts a single data field.
        """
        pass

    @abstractmethod
    def decrypt_field(self, data: str) -> str:
        """
        Decrypts a single data field.
        """
        pass

import base64

class MockAESEncryption(DataEncryptionPolicy):
    """
    DEMO ONLY: Uses Base64 as a visual placeholder for AES encryption.
    DO NOT USE IN PRODUCTION.
    """

    def get_encryption_config(self) -> dict:
        return {
            "algorithm": "AES-256-GCM",
            "key_rotation_days": 90,
            "provider": "MockHSM"
        }

    def encrypt_field(self, data: str) -> str:
        # Mock encryption: distinct prefix + base64
        encoded = base64.b64encode(data.encode()).decode()
        return f"enc_{encoded}"

    def decrypt_field(self, data: str) -> str:
        if not data.startswith("enc_"):
            raise ValueError("Invalid encrypted format")
        encoded = data[4:]
        return base64.b64decode(encoded).decode()
