from .base_cipher import BaseCipher
from typing import Dict, List, Any

class BaconCipher(BaseCipher):
    # Bacon's cipher encoding (I/J and U/V are combined)
    BACON_DICT = {
        'A': 'AAAAA', 'B': 'AAAAB', 'C': 'AAABA', 'D': 'AAABB', 'E': 'AABAA',
        'F': 'AABAB', 'G': 'AABBA', 'H': 'AABBB', 'I': 'ABAAA', 'J': 'ABAAA',
        'K': 'ABAAB', 'L': 'ABABA', 'M': 'ABABB', 'N': 'ABBAA', 'O': 'ABBAB',
        'P': 'ABBBA', 'Q': 'ABBBB', 'R': 'BAAAA', 'S': 'BAAAB', 'T': 'BAABA',
        'U': 'BAABB', 'V': 'BAABB', 'W': 'BABAA', 'X': 'BABAB', 'Y': 'BABBA',
        'Z': 'BABBB'
    }
    
    def get_name(self) -> str:
        return "Bacon Cipher"
    
    def get_description(self) -> str:
        return """
        Bacon's cipher is a method of steganography created by Francis Bacon. Each letter 
        is encoded as a sequence of 5 A's and B's (or 0's and 1's).
        
        **History**: Invented in 1605, it can hide messages in the presentation of text 
        (e.g., using different fonts or typefaces).
        
        **Encoding**: Uses only two symbols to represent all 26 letters.
        
        **Note**: I and J share the same code, as do U and V (24-letter alphabet).
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'format',
                'type': 'select',
                'label': 'Output Format',
                'default': 'AB',
                'options': [
                    {'label': 'A/B', 'value': 'AB'},
                    {'label': '0/1 (Binary)', 'value': '01'}
                ]
            }
        ]
    
    def encrypt(self, plaintext: str, format: str = 'AB', **params) -> Dict[str, Any]:
        steps = []
        
        steps.append({
            'title': 'Step 1: Initialize',
            'description': f'Each letter encodes to 5 symbols ({"A/B" if format == "AB" else "0/1"}). I/J and U/V share codes.'
        })
        
        result = []
        examples = []
        
        for char in plaintext.upper():
            if char in self.BACON_DICT:
                code = self.BACON_DICT[char]
                if format == '01':
                    code = code.replace('A', '0').replace('B', '1')
                result.append(code)
                
                if len(examples) < 5:
                    examples.append(f'{char}→{code}')
        
        steps.append({
            'title': 'Step 2: Encode Characters',
            'description': 'Examples:\n' + '\n'.join(examples) + ('\n...' if len(examples) >= 5 else '')
        })
        
        ciphertext = ' '.join(result)
        
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Encoded message:\n{ciphertext[:300]}{"..." if len(ciphertext) > 300 else ""}'
        })
        
        return {
            'result': ciphertext,
            'steps': steps,
            'visualization_data': None
        }
    
    def decrypt(self, ciphertext: str, format: str = 'AB', **params) -> Dict[str, Any]:
        steps = []
        
        # Create reverse dictionary
        reverse_dict = {v: k for k, v in self.BACON_DICT.items() if k not in ['J', 'V']}
        
        steps.append({
            'title': 'Step 1: Parse Input',
            'description': 'Extract groups of 5 symbols and decode'
        })
        
        # Remove spaces and convert to standard format
        clean = ciphertext.replace(' ', '').replace('\n', '')
        if format == '01':
            clean = clean.replace('0', 'A').replace('1', 'B')
        
        # Only keep A and B
        clean = ''.join(c for c in clean.upper() if c in ['A', 'B'])
        
        result = []
        examples = []
        
        for i in range(0, len(clean), 5):
            code = clean[i:i+5]
            if len(code) == 5 and code in reverse_dict:
                char = reverse_dict[code]
                result.append(char)
                if len(examples) < 5:
                    examples.append(f'{code}→{char}')
        
        steps.append({
            'title': 'Step 2: Decode Groups',
            'description': 'Examples:\n' + '\n'.join(examples) + ('\n...' if len(examples) >= 5 else '')
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
