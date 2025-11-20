from .base_cipher import BaseCipher
from typing import Dict, List, Any

class ReverseCipher(BaseCipher):
    def get_name(self) -> str:
        return "Reverse Text"
    
    def get_description(self) -> str:
        return """
        A simple transformation that reverses the order of characters in the text.
        
        **Example**: "HELLO" becomes "OLLEH"
        
        **Not encryption**: This is a basic text transformation, providing no security.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return []
    
    def encrypt(self, plaintext: str, **params) -> Dict[str, Any]:
        steps = []
        
        steps.append({
            'title': 'Step 1: Reverse Characters',
            'description': f'Original length: {len(plaintext)} characters'
        })
        
        result = plaintext[::-1]
        
        steps.append({
            'title': 'Step 2: Complete',
            'description': f'Reversed text: {result}'
        })
        
        return {
            'result': result,
            'steps': steps,
            'visualization_data': None
        }
    
    def decrypt(self, ciphertext: str, **params) -> Dict[str, Any]:
        # Reversing is its own inverse
        return self.encrypt(ciphertext, **params)
