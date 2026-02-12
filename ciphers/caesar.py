from .base_cipher import BaseCipher
from typing import Dict, List, Any
from collections import Counter

class CaesarCipher(BaseCipher):
    def get_name(self) -> str:
        return "Caesar Cipher"
    
    def get_description(self) -> str:
        return """
        The Caesar cipher is one of the simplest encryption techniques. It shifts each letter 
        in the plaintext by a fixed number of positions down the alphabet.
        
        **History**: Named after Julius Caesar, who used it for military communications.
        
        **Weakness**: Extremely vulnerable to brute force (only 25 possible keys) and 
        frequency analysis.
        
        **Brute Force**: Try all 25 possible shifts to find the correct decryption!
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'shift',
                'type': 'number',
                'label': 'Shift (0-25)',
                'default': 3,
                'min': 0,
                'max': 25
            },
            {
                'name': 'brute_force',
                'type': 'checkbox',
                'label': 'Brute Force Mode (try all shifts)',
                'default': False
            }
        ]
    
    def encrypt(self, plaintext: str, shift: int = 3, brute_force: bool = False, **params) -> Dict[str, Any]:
        shift = int(shift) % 26
        steps = []
        result = []
        
        steps.append({
            'title': 'Step 1: Initialize',
            'description': f'Shift value: {shift}. We will shift each letter {shift} positions forward.'
        })
        
        char_transformations = []
        for char in plaintext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = chr((ord(char) - base + shift) % 26 + base)
                char_transformations.append(f'{char} → {shifted}')
                result.append(shifted)
            else:
                result.append(char)
        
        steps.append({
            'title': 'Step 2: Character Transformation',
            'description': 'Transformations: ' + ', '.join(char_transformations[:10]) + 
                          ('...' if len(char_transformations) > 10 else '')
        })
        
        ciphertext = ''.join(result)
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Final ciphertext: {ciphertext}'
        })
        
        # Frequency analysis data
        freq_data = Counter([c.upper() for c in ciphertext if c.isalpha()])
        
        return {
            'result': ciphertext,
            'steps': steps,
            'visualization_data': {
                'type': 'frequency',
                'data': freq_data
            }
        }
    
    def decrypt(self, ciphertext: str, shift: int = 3, brute_force: bool = False, **params) -> Dict[str, Any]:
        if brute_force:
            return self._brute_force_decrypt(ciphertext)
        
        shift = int(shift) % 26
        return self.encrypt(ciphertext, shift=-shift)
    
    def _brute_force_decrypt(self, ciphertext: str) -> Dict[str, Any]:
        """Try all possible shifts and return all results."""
        steps = []
        
        steps.append({
            'title': 'Brute Force Attack',
            'description': 'Trying all 26 possible shifts (0-25). Look for readable text!'
        })
        
        all_results = []
        structured_results = []  # For AI analysis
        
        for shift in range(26):
            result = []
            for char in ciphertext:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    shifted = chr((ord(char) - base - shift) % 26 + base)
                    result.append(shifted)
                else:
                    result.append(char)
            
            decrypted = ''.join(result)
            score = self._score_text(decrypted)
            all_results.append(f"Shift {shift:2d}: {decrypted}")
            structured_results.append({
                'key': f'Shift {shift}',
                'text': decrypted,
                'score': score
            })
        
        # Sort by score for better ordering
        structured_results.sort(key=lambda x: x['score'], reverse=True)
        
        steps.append({
            'title': 'All Possible Shifts',
            'description': 'Results for all shifts:\n\n' + '\n'.join(all_results)
        })
        
        steps.append({
            'title': 'How to Find the Answer',
            'description': 'Look through the results above for text that makes sense. ' +
                          'Most results will be gibberish, but one should be readable English (or your target language).'
        })
        
        # Return all results concatenated
        result_text = '\n'.join(all_results)
        
        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None,
            'brute_force_results': structured_results
        }
    
    def _score_text(self, text: str) -> float:
        """Score how likely text is English using word dictionary."""
        if not text:
            return 0.0
        
        # Common English words (same as affine.py)
        common_words = {
            'THE', 'BE', 'TO', 'OF', 'AND', 'A', 'IN', 'THAT', 'HAVE', 'I',
            'IT', 'FOR', 'NOT', 'ON', 'WITH', 'HE', 'AS', 'YOU', 'DO', 'AT',
            'THIS', 'BUT', 'HIS', 'BY', 'FROM', 'THEY', 'WE', 'SAY', 'HER', 'SHE',
            'OR', 'AN', 'WILL', 'MY', 'ONE', 'ALL', 'WOULD', 'THERE', 'THEIR', 'WHAT',
            'SO', 'UP', 'OUT', 'IF', 'ABOUT', 'WHO', 'GET', 'WHICH', 'GO', 'ME',
            'WHEN', 'MAKE', 'CAN', 'LIKE', 'TIME', 'NO', 'JUST', 'HIM', 'KNOW', 'TAKE',
            'PEOPLE', 'INTO', 'YEAR', 'YOUR', 'GOOD', 'SOME', 'COULD', 'THEM', 'SEE', 'OTHER',
            'THAN', 'THEN', 'NOW', 'LOOK', 'ONLY', 'COME', 'ITS', 'OVER', 'THINK', 'ALSO',
            'BACK', 'AFTER', 'USE', 'TWO', 'HOW', 'OUR', 'WORK', 'FIRST', 'WELL', 'WAY',
            'EVEN', 'NEW', 'WANT', 'BECAUSE', 'ANY', 'THESE', 'GIVE', 'DAY', 'MOST', 'US',
            'IS', 'WAS', 'ARE', 'BEEN', 'HAS', 'HAD', 'WERE', 'SAID', 'DID', 'HAVING',
            'MAY', 'SHOULD', 'MUST', 'VERY', 'THROUGH', 'WHERE', 'MUCH', 'BEFORE', 'RIGHT', 'SUCH',
            'WALKED', 'DOG', 'TODAY', 'WALK'
        }
        
        text_upper = text.upper()
        
        # Extract words
        words = []
        current_word = []
        for char in text_upper:
            if char.isalpha():
                current_word.append(char)
            elif current_word:
                words.append(''.join(current_word))
                current_word = []
        if current_word:
            words.append(''.join(current_word))
        
        if not words:
            return 0.0
        
        # Count valid words
        valid_words = sum(1 for word in words if word in common_words)
        word_ratio = valid_words / len(words)
        
        # Bonus for longer valid words
        long_word_bonus = sum(len(word) * 2 for word in words if len(word) >= 4 and word in common_words)
        
        # Bonus for very common words
        very_common = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'WITH', 'WAS', 'SHE', 'WALKED', 'DOG', 'TODAY'}
        very_common_bonus = sum(15 for word in words if word in very_common)
        
        return (word_ratio * 100) + long_word_bonus + very_common_bonus

    # By Anton Wingeier
