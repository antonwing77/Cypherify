from .base_cipher import BaseCipher
from typing import Dict, List, Any

class A1Z26Cipher(BaseCipher):
    def get_name(self) -> str:
        return "A1Z26"
    
    def get_description(self) -> str:
        return """
        A1Z26 is a simple substitution cipher where each letter is replaced by its position 
        in the alphabet (A=1, B=2, ..., Z=26).
        
        **Format**: Numbers are separated by dashes or spaces.
        
        **Uses**: Common in puzzles and geocaching.
        
        **Weakness**: Not a true encryption method, merely encoding. No "brute force" needed - 
        it's immediately reversible if you know it's A1Z26. The only "attack" is recognizing 
        the pattern of numbers 1-26.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'separator',
                'type': 'select',
                'label': 'Number Separator',
                'default': '-',
                'options': [
                    {'label': 'Dash (-)', 'value': '-'},
                    {'label': 'Space ( )', 'value': ' '},
                    {'label': 'Comma (,)', 'value': ','}
                ]
            }
        ]
    
    def encrypt(self, plaintext: str, separator: str = '-', **params) -> Dict[str, Any]:
        steps = []
        
        steps.append({
            'title': 'Step 1: Convert Letters to Numbers',
            'description': 'Each letter maps to its position: A=1, B=2, C=3, ..., Z=26'
        })
        
        numbers = []
        examples = []
        
        for char in plaintext:
            if char.isalpha():
                pos = ord(char.upper()) - ord('A') + 1
                numbers.append(str(pos))
                if len(examples) < 10:
                    examples.append(f'{char}→{pos}')
            elif char == ' ':
                numbers.append('0')
        
        steps.append({
            'title': 'Step 2: Character Mapping',
            'description': 'Examples: ' + ', '.join(examples) + ('...' if len(examples) >= 10 else '')
        })
        
        result = separator.join(numbers)
        
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Result (separated by "{separator}"): {result[:200]}{"..." if len(result) > 200 else ""}'
        })
        
        return {
            'result': result,
            'steps': steps,
            'visualization_data': None
        }

    # By Anton Wingeier
    
    def decrypt(self, ciphertext: str, separator: str = '-', **params) -> Dict[str, Any]:
        steps = []
        
        steps.append({
            'title': 'Step 1: Parse Numbers',
            'description': f'Split by separator "{separator}" and convert back to letters'
        })
        
        # Try multiple separators if the specified one doesn't work
        numbers = []
        for sep in [separator, '-', ' ', ',']:
            try:
                numbers = [int(n.strip()) for n in ciphertext.split(sep) if n.strip().isdigit()]
                if numbers:
                    break
            except:
                continue
        
        if not numbers:
            return {
                'result': 'Error: Could not parse numbers from input',
                'steps': steps,
                'visualization_data': None
            }
        
        result = []
        examples = []
        
        for num in numbers:
            if 1 <= num <= 26:
                char = chr(num - 1 + ord('A'))
                result.append(char)
                if len(examples) < 10:
                    examples.append(f'{num}→{char}')
            elif num == 0:
                result.append(' ')
        
        steps.append({
            'title': 'Step 2: Convert to Letters',
            'description': 'Examples: ' + ', '.join(examples) + ('...' if len(examples) >= 10 else '')
        })
        
        plaintext = ''.join(result)
        
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Result: {plaintext}'
        })
        
        return {
            'result': plaintext,
            'steps': steps,
            'visualization_data': None
        }
