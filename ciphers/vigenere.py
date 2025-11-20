from .base_cipher import BaseCipher
from typing import Dict, List, Any
from collections import Counter
import string

class VigenereCipher(BaseCipher):
    def get_name(self) -> str:
        return "Vigenère Cipher"
    
    def get_description(self) -> str:
        return """
        The Vigenère cipher uses a keyword to apply multiple Caesar shifts. Each letter 
        in the keyword determines the shift for the corresponding plaintext letter.
        
        **History**: Invented in the 16th century, it was considered unbreakable for centuries 
        until frequency analysis techniques were developed.
        
        **Weakness**: Vulnerable to Kasiski examination and frequency analysis when the key 
        length is known or can be determined.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'keyword',
                'type': 'text',
                'label': 'Keyword (letters only)',
                'default': 'KEY'
            },
            {
                'name': 'brute_force',
                'type': 'checkbox',
                'label': 'Brute Force Mode (try common keywords)',
                'default': False
            }
        ]
    
    def encrypt(self, plaintext: str, keyword: str = 'KEY', **params) -> Dict[str, Any]:
        keyword = ''.join(c for c in keyword.upper() if c.isalpha())
        if not keyword:
            keyword = 'KEY'
        
        steps = []
        result = []
        
        steps.append({
            'title': 'Step 1: Initialize',
            'description': f'Keyword: {keyword}. Key length: {len(keyword)}. The keyword repeats to match text length.'
        })
        
        key_index = 0
        transformations = []
        
        for i, char in enumerate(plaintext):
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(keyword[key_index % len(keyword)]) - ord('A')
                shifted = chr((ord(char) - base + shift) % 26 + base)
                
                if len(transformations) < 10:
                    transformations.append(
                        f'{char} + {keyword[key_index % len(keyword)]}({shift}) = {shifted}'
                    )
                
                result.append(shifted)
                key_index += 1
            else:
                result.append(char)
        
        steps.append({
            'title': 'Step 2: Apply Shifts',
            'description': 'Transformations: ' + ', '.join(transformations) + 
                          ('...' if len(transformations) >= 10 else '')
        })
        
        ciphertext = ''.join(result)
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Final ciphertext: {ciphertext}'
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
    
    def decrypt(self, ciphertext: str, keyword: str = 'KEY', brute_force: bool = False, **params) -> Dict[str, Any]:
        if brute_force:
            return self._brute_force_decrypt(ciphertext)
        
        keyword = ''.join(c for c in keyword.upper() if c.isalpha())
        if not keyword:
            keyword = 'KEY'
        
        # Decrypt by using negative shifts
        steps = []
        result = []
        
        steps.append({
            'title': 'Step 1: Initialize',
            'description': f'Keyword: {keyword}. Decrypting by reversing the shift operation.'
        })
        
        key_index = 0
        transformations = []
        
        for char in ciphertext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(keyword[key_index % len(keyword)]) - ord('A')
                shifted = chr((ord(char) - base - shift) % 26 + base)
                
                if len(transformations) < 10:
                    transformations.append(
                        f'{char} - {keyword[key_index % len(keyword)]}({shift}) = {shifted}'
                    )
                
                result.append(shifted)
                key_index += 1
            else:
                result.append(char)
        
        steps.append({
            'title': 'Step 2: Reverse Shifts',
            'description': 'Transformations: ' + ', '.join(transformations) + 
                          ('...' if len(transformations) >= 10 else '')
        })
        
        plaintext = ''.join(result)
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Final plaintext: {plaintext}'
        })
        
        return {
            'result': plaintext,
            'steps': steps,
            'visualization_data': None
        }
    
    def _brute_force_decrypt(self, ciphertext: str) -> Dict[str, Any]:
        """Try common keywords to decrypt Vigenère cipher."""
        steps = []
        
        # Common keywords to try
        common_keywords = [
            'KEY', 'SECRET', 'CIPHER', 'CODE', 'PASSWORD', 'CRYPTO',
            'HELLO', 'WORLD', 'TEST', 'MESSAGE', 'SECURITY', 'PRIVATE',
            'A', 'AB', 'ABC', 'ABCD', 'THE', 'AND', 'FOR'
        ]
        
        steps.append({
            'title': 'Brute Force Attack',
            'description': f'Trying {len(common_keywords)} common keywords. Real attacks would try many more! AI will analyze to find the correct one.'
        })
        
        all_results = []
        structured_results = []  # For AI analysis
        
        for keyword in common_keywords:
            result = []
            key_index = 0
            
            for char in ciphertext:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    shift = ord(keyword[key_index % len(keyword)]) - ord('A')
                    shifted = chr((ord(char) - base - shift) % 26 + base)
                    result.append(shifted)
                    key_index += 1
                else:
                    result.append(char)
            
            decrypted = ''.join(result)
            all_results.append(f"Keyword '{keyword:10s}': {decrypted[:60]}{'...' if len(decrypted) > 60 else ''}")
            structured_results.append((f"Keyword '{keyword}'", decrypted))
        
        steps.append({
            'title': 'Common Keywords Tried',
            'description': 'Results:\n\n' + '\n'.join(all_results)
        })
        
        steps.append({
            'title': 'How to Find the Answer',
            'description': 'Look for readable English text. Advanced attacks use frequency analysis and Kasiski examination to find key length.\n\n' +
                          'AI Teacher can analyze these results to identify the most likely correct decryption!'
        })
        
        result_text = '\n'.join(all_results)
        
        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None,
            'brute_force_results': structured_results
        }
