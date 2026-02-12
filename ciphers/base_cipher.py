from abc import ABC, abstractmethod

class BaseCipher(ABC):
    """Base class for all ciphers."""
    
    @abstractmethod
    def encrypt(self, plaintext: str, **kwargs) -> dict:
        """Encrypt the given plaintext."""
        pass
    
    @abstractmethod
    def decrypt(self, ciphertext: str, **kwargs) -> dict:
        """Decrypt the given ciphertext."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the cipher."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a short description of the cipher."""
        pass
    
    @abstractmethod
    def get_parameters(self) -> list:
        """Return a list of parameters for the cipher."""
        pass
    
    def get_security_warning(self) -> str:
        """Return security warning for educational purposes."""
        return "WARNING: EDUCATIONAL ONLY - NOT FOR REAL-WORLD SECURITY USE"

    # By Anton Wingeier