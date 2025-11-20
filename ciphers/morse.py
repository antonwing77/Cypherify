from .base_cipher import BaseCipher
from typing import Dict, List, Any

class MorseCipher(BaseCipher):
    MORSE_CODE = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..',
        '!': '-.-.--', ' ': '/'
    }
    
    def get_name(self) -> str:
        return "Morse Code"
    
    def get_description(self) -> str:
        return """
        Morse code is a method of encoding text using sequences of dots (.) and dashes (-).
        
        **History**: Developed in the 1830s-1840s for telegraph communication.
        
        **Format**: Letters separated by spaces, words separated by slashes (/).
        
        **Not encryption**: Morse code is an encoding system, not a cipher.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return []
    
    def encrypt(self, plaintext: str, **params) -> Dict[str, Any]:
        steps = []
        
        steps.append({
            'title': 'Step 1: Convert to Morse',
            'description': 'Each letter converts to dots (.) and dashes (-)'
        })
        
        result = []
        examples = []
        
        for char in plaintext.upper():
            if char in self.MORSE_CODE:
                code = self.MORSE_CODE[char]
                result.append(code)
                if len(examples) < 10:
                    examples.append(f'{char}→{code}')
        
        steps.append({
            'title': 'Step 2: Character Mapping',
            'description': 'Examples: ' + ', '.join(examples) + ('...' if len(examples) >= 10 else '')
        })
        
        morse = ' '.join(result)
        
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Morse code:\n{morse[:300]}{"..." if len(morse) > 300 else ""}'
        })
        
        return {
            'result': morse,
            'steps': steps,
            'visualization_data': None
        }
    
    def decrypt(self, ciphertext: str, **params) -> Dict[str, Any]:
        steps = []
        
        # Create reverse dictionary
        reverse_morse = {v: k for k, v in self.MORSE_CODE.items()}
        
        steps.append({
            'title': 'Step 1: Parse Morse Code',
            'description': 'Split by spaces and decode each symbol'
        })
        
        result = []
        examples = []
        
        for code in ciphertext.split(' '):
            if code in reverse_morse:
                char = reverse_morse[code]
                result.append(char)
                if len(examples) < 10:
                    examples.append(f'{code}→{char}')
        
        steps.append({
            'title': 'Step 2: Decode Symbols',
            'description': 'Examples: ' + ', '.join(examples) + ('...' if len(examples) >= 10 else '')
        })
        
        plaintext = ''.join(result)
        
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Decoded message: {plaintext}'
        })
        
        return {
            'result': plaintext,
            'steps': steps,
            'visualization_data': None
        }
