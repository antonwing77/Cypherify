from .base_cipher import BaseCipher
from typing import Dict, List, Any
from collections import Counter

class ROT13Cipher(BaseCipher):
    def get_name(self) -> str:
        return "ROT13"
    
    def get_description(self) -> str:
        return """
        ROT13 is a simple letter substitution cipher that replaces a letter with the 13th letter 
        after it in the alphabet. It's a special case of the Caesar cipher with a fixed shift of 13.
        
        **Special Property**: ROT13 is its own inverse - applying ROT13 twice returns the original text.
        
        **Uses**: Commonly used to obscure spoilers, puzzles, or offensive content online.
        
        **Weakness**: Trivially broken since there's only one possible key. "Brute force" means just applying ROT13 once!
        
        **Breaking it**: Since ROT13 is its own inverse, just click "Decrypt" or "Encrypt" to reverse it.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return []
    
    def encrypt(self, plaintext: str, **params) -> Dict[str, Any]:
        steps = []
        result = []
        
        steps.append({
            'title': 'Step 1: Initialize',
            'description': 'ROT13 shifts each letter by 13 positions. A→N, B→O, ..., N→A, ..., Z→M'
        })
        
        transformations = []
        for char in plaintext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = chr((ord(char) - base + 13) % 26 + base)
                if len(transformations) < 10:
                    transformations.append(f'{char}→{shifted}')
                result.append(shifted)
            else:
                result.append(char)
        
        steps.append({
            'title': 'Step 2: Transform Characters',
            'description': 'Transformations: ' + ', '.join(transformations) + 
                          ('...' if len(transformations) >= 10 else '')
        })
        
        ciphertext = ''.join(result)
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Result: {ciphertext}\n\nNote: Applying ROT13 again will return the original text.'
        })
        
        freq_data = Counter([c.upper() for c in ciphertext if c.isalpha()])
        
        return {
            'result': ciphertext,
            'steps': steps,
            'visualization_data': {
                'type': 'frequency',
                'data': freq_data
            }
        }
    
    def decrypt(self, ciphertext: str, **params) -> Dict[str, Any]:
        # ROT13 is its own inverse
        return self.encrypt(ciphertext, **params)
