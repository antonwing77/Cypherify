from .base_cipher import BaseCipher
from typing import Dict, List, Any
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

class AESCipher(BaseCipher):
    def get_name(self) -> str:
        return "AES (Advanced Encryption Standard)"
    
    def get_description(self) -> str:
        return """
        AES is a symmetric block cipher that encrypts data in 128-bit blocks using keys 
        of 128, 192, or 256 bits. It's the current U.S. government standard.
        
        **History**: Selected in 2001 after a competition, replacing DES.
        
        **Security**: Considered secure when properly implemented with appropriate key 
        management, random IVs, and authenticated encryption modes.
        
        **Note**: This demo uses CBC mode for educational purposes. Real applications 
        should use authenticated modes like GCM.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'key',
                'type': 'text',
                'label': 'Key (16, 24, or 32 characters)',
                'default': 'SIXTEENBYTE_KEY!'
            }

# By Anton Wingeier
        ]
    
    def encrypt(self, plaintext: str, key: str = 'SIXTEENBYTE_KEY!', **params) -> Dict[str, Any]:
        steps = []
        
        # Prepare key
        key_bytes = key.encode('utf-8')
        if len(key_bytes) not in [16, 24, 32]:
            key_bytes = key_bytes[:16].ljust(16, b'\0')
        
        steps.append({
            'title': 'Step 1: Key Preparation',
            'description': f'Key length: {len(key_bytes)} bytes ({len(key_bytes)*8} bits). AES supports 128, 192, or 256-bit keys.'
        })
        
        # Generate IV
        iv = get_random_bytes(16)
        steps.append({
            'title': 'Step 2: Generate IV',
            'description': f'Initialization Vector (IV): {base64.b64encode(iv).decode()[:20]}... (16 bytes). IV ensures same plaintext produces different ciphertext.'
        })
        
        # Pad plaintext
        plaintext_bytes = plaintext.encode('utf-8')
        padded = pad(plaintext_bytes, AES.block_size)
        steps.append({
            'title': 'Step 3: Padding',
            'description': f'Original: {len(plaintext_bytes)} bytes → Padded: {len(padded)} bytes. AES requires input to be multiple of 16 bytes.'
        })
        
        # Encrypt
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        ciphertext_bytes = cipher.encrypt(padded)
        
        steps.append({
            'title': 'Step 4: Encryption',
            'description': f'Applied AES-CBC encryption. Processed {len(ciphertext_bytes)//16} blocks of 16 bytes each.'
        })
        
        # Combine IV and ciphertext
        result = base64.b64encode(iv + ciphertext_bytes).decode('utf-8')
        
        steps.append({
            'title': 'Step 5: Encode Result',
            'description': f'Combined IV + ciphertext and encoded as Base64. Final length: {len(result)} characters.'
        })
        
        return {
            'result': result,
            'steps': steps,
            'visualization_data': {
                'type': 'block_structure',
                'blocks': len(ciphertext_bytes) // 16,
                'key_size': len(key_bytes) * 8
            }
        }
    
    def decrypt(self, ciphertext: str, key: str = 'SIXTEENBYTE_KEY!', **params) -> Dict[str, Any]:
        steps = []
        
        try:
            # Prepare key
            key_bytes = key.encode('utf-8')
            if len(key_bytes) not in [16, 24, 32]:
                key_bytes = key_bytes[:16].ljust(16, b'\0')
            
            steps.append({
                'title': 'Step 1: Key Preparation',
                'description': f'Using key of length {len(key_bytes)} bytes ({len(key_bytes)*8} bits).'
            })
            
            # Decode
            data = base64.b64decode(ciphertext)
            steps.append({
                'title': 'Step 2: Decode Input',
                'description': f'Decoded Base64 input: {len(data)} bytes total.'
            })
            
            # Extract IV and ciphertext
            iv = data[:16]
            ciphertext_bytes = data[16:]
            
            steps.append({
                'title': 'Step 3: Extract IV',
                'description': f'Extracted 16-byte IV. Remaining ciphertext: {len(ciphertext_bytes)} bytes.'
            })
            
            # Decrypt
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
            padded_plaintext = cipher.decrypt(ciphertext_bytes)
            
            steps.append({
                'title': 'Step 4: Decryption',
                'description': f'Applied AES-CBC decryption. Processed {len(ciphertext_bytes)//16} blocks.'
            })
            
            # Unpad
            plaintext_bytes = unpad(padded_plaintext, AES.block_size)
            result = plaintext_bytes.decode('utf-8')
            
            steps.append({
                'title': 'Step 5: Remove Padding',
                'description': f'Removed PKCS7 padding. Final plaintext: {len(result)} characters.'
            })
            
            return {
                'result': result,
                'steps': steps,
                'visualization_data': None
            }
        except Exception as e:
            return {
                'result': f'Decryption failed: {str(e)}',
                'steps': steps + [{'title': 'Error', 'description': str(e)}],
                'visualization_data': None
            }
