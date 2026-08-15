from backend.data_security.encryption import MockAESEncryption

class VectorSecurity:
    """
    Handles encryption/decryption of vector payloads.
    """
    
    def __init__(self):
        self.cipher = MockAESEncryption()

    def encrypt_payload(self, text: str) -> str:
        return self.cipher.encrypt_field(text)

    def decrypt_payload(self, encrypted_text: str) -> str:
        return self.cipher.decrypt_field(encrypted_text)
