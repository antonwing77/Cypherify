from .base_cipher import BaseCipher
from typing import Dict, List, Any
import random
import json

class RSACipher(BaseCipher):
    def __init__(self):
        self.stored_keys = None
    
    def get_name(self) -> str:
        return "RSA (Rivest-Shamir-Adleman)"
    
    def get_description(self) -> str:
        return """
        RSA is an asymmetric (public-key) cryptosystem based on the difficulty of 
        factoring large prime numbers. Uses a public key for encryption and private key for decryption.
        
        **History**: Invented in 1977, it's one of the first practical public-key cryptosystems.
        
        **Security**: Secure with proper key sizes (2048+ bits). This demo uses small numbers 
        for educational visualization only.
        
        **Warning**: Small key sizes shown here are INSECURE and for demonstration only!
        
        **How it works**:
        1. Generate two large prime numbers (p, q)
        2. Calculate n = p × q and φ(n) = (p-1)(q-1)
        3. Choose public exponent e (commonly 65537)
        4. Calculate private exponent d (modular inverse of e mod φ(n))
        5. Public key: (e, n) - share this for encryption
        6. Private key: (d, n) - keep this secret for decryption
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'action_type',
                'type': 'select',
                'label': 'Action',
                'default': 'generate',
                'options': [
                    {'label': 'Generate New Keys', 'value': 'generate'},
                    {'label': 'Use Existing Keys', 'value': 'use_existing'}
                ]
            },
            {
                'name': 'public_key',
                'type': 'text',
                'label': 'Public Key (e,n) - for encryption',
                'default': ''
            },
            {
                'name': 'private_key',
                'type': 'text',
                'label': 'Private Key (d,n) - for decryption',
                'default': ''
            }
        ]
    
    def _generate_small_primes(self):
        """Generate small primes for educational demonstration."""
        small_primes = [61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157]
        p = random.choice(small_primes)
        q = random.choice([x for x in small_primes if x != p])
        return p, q
    
    def _gcd(self, a, b):
        while b:
            a, b = b, a % b
        return a
    
    def _mod_inverse(self, e, phi):
        """Extended Euclidean Algorithm for modular inverse."""
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        _, x, _ = extended_gcd(e, phi)
        return (x % phi + phi) % phi
    
    def _generate_keys(self):
        """Generate RSA key pair."""
        p, q = self._generate_small_primes()
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # Choose e
        e = 65537
        while e >= phi or self._gcd(e, phi) != 1:
            e = random.randint(3, phi - 1)
            if e >= phi:
                e = random.randint(3, min(65537, phi - 1))
        
        # Calculate d
        d = self._mod_inverse(e, phi)
        
        return {
            'p': p,
            'q': q,
            'n': n,
            'e': e,
            'd': d,
            'phi': phi,
            'public_key': f"{e},{n}",
            'private_key': f"{d},{n}"
        }
    
    def encrypt(self, plaintext: str, action_type: str = 'generate', public_key: str = '', **params) -> Dict[str, Any]:
        steps = []
        
        # Generate or use existing keys
        if action_type == 'generate' or not public_key:
            keys = self._generate_keys()
            self.stored_keys = keys
            
            steps.append({
                'title': 'Step 1: Generate Prime Numbers',
                'description': f'Selected primes: p={keys["p"]}, q={keys["q"]}\n(In real RSA, these would be 1024+ bit primes)'
            })
            
            steps.append({
                'title': 'Step 2: Calculate n and φ(n)',
                'description': f'n = p × q = {keys["p"]} × {keys["q"]} = {keys["n"]}\nφ(n) = (p-1) × (q-1) = {keys["p"]-1} × {keys["q"]-1} = {keys["phi"]}'
            })
            
            steps.append({
                'title': 'Step 3: Choose Public Exponent e',
                'description': f'e = {keys["e"]}\nMust be coprime with φ(n). Common choice is 65537 when possible.'
            })
            
            steps.append({
                'title': 'Step 4: Calculate Private Exponent d',
                'description': f'd = {keys["d"]}\nThis is the modular inverse of e mod φ(n).\n\n' +
                              f'PUBLIC KEY (for encryption): ({keys["e"]}, {keys["n"]})\n' +
                              f'PRIVATE KEY (for decryption): ({keys["d"]}, {keys["n"]})\n\n' +
                              f'Share the public key, keep the private key secret!'
            })
        else:
            # Parse provided public key
            try:
                e, n = map(int, public_key.split(','))
                keys = {'e': e, 'n': n, 'public_key': public_key}
                steps.append({
                    'title': 'Step 1: Using Provided Public Key',
                    'description': f'Public Key: e={e}, n={n}\nThis key will be used for encryption.'
                })
            except:
                return {
                    'result': 'Error: Invalid public key format. Use format: e,n (e.g., 17,3233)',
                    'steps': [{'title': 'Error', 'description': 'Invalid public key format. Expected: e,n'}],
                    'visualization_data': None
                }
        
        # Encrypt each character
        e = keys['e']
        n = keys['n']
        ciphertext_nums = []
        encryption_examples = []
        
        step_num = len(steps) + 1
        for i, char in enumerate(plaintext[:50]):  # Limit for demo
            m = ord(char)
            if m >= n:
                steps.append({
                    'title': 'Error',
                    'description': f'Character value {m} exceeds n={n}. Need larger primes or shorter text.'
                })
                return {'result': 'Error: n too small for text', 'steps': steps, 'visualization_data': None}
            
            c = pow(m, e, n)
            ciphertext_nums.append(c)
            
            if i < 5:
                encryption_examples.append(f"'{char}'({m}) → {c}")
        
        steps.append({
            'title': f'Step {step_num}: Encrypt Characters',
            'description': f'For each character m: c = m^e mod n = m^{e} mod {n}\n\n' +
                          f'Examples:\n' + '\n'.join(encryption_examples) +
                          (f'\n...and {len(plaintext) - 5} more characters' if len(plaintext) > 5 else '')
        })
        
        result = ','.join(map(str, ciphertext_nums))
        
        steps.append({
            'title': f'Step {step_num + 1}: Complete',
            'description': f'Encrypted message (comma-separated numbers):\n{result[:200]}{"..." if len(result) > 200 else ""}\n\n' +
                          f'TO DECRYPT: Use the private key ({keys.get("d", "?")}, {n})'
        })
        
        # Visualization data
        viz_data = None
        if action_type == 'generate':
            viz_data = {
                'type': 'rsa_keys',
                'p': keys['p'],
                'q': keys['q'],
                'n': keys['n'],
                'e': keys['e'],
                'd': keys['d'],
                'phi': keys['phi']
            }
        
        return {
            'result': result,
            'steps': steps,
            'visualization_data': viz_data
        }
    
    def decrypt(self, ciphertext: str, action_type: str = 'generate', private_key: str = '', **params) -> Dict[str, Any]:
        steps = []
        
        # Get private key
        if self.stored_keys and action_type == 'generate':
            d = self.stored_keys['d']
            n = self.stored_keys['n']
            steps.append({
                'title': 'Step 1: Using Generated Private Key',
                'description': f'Private Key: d={d}, n={n}\nThis key will decrypt the message encrypted with the corresponding public key.'
            })
        elif private_key:
            try:
                d, n = map(int, private_key.split(','))
                steps.append({
                    'title': 'Step 1: Using Provided Private Key',
                    'description': f'Private Key: d={d}, n={n}'
                })
            except:
                return {
                    'result': 'Error: Invalid private key format. Use format: d,n (e.g., 2753,3233)',
                    'steps': [{'title': 'Error', 'description': 'Invalid private key format. Expected: d,n'}],
                    'visualization_data': None
                }
        else:
            return {
                'result': 'Error: No private key available. Generate keys first or provide a private key.',
                'steps': [{'title': 'Error', 'description': 'No private key available for decryption.'}],
                'visualization_data': None
            }
        
        # Parse ciphertext
        try:
            ciphertext_nums = list(map(int, ciphertext.split(',')))
        except:
            return {
                'result': 'Error: Invalid ciphertext format. Expected comma-separated numbers.',
                'steps': steps + [{'title': 'Error', 'description': 'Invalid ciphertext format.'}],
                'visualization_data': None
            }
        
        steps.append({
            'title': 'Step 2: Parse Ciphertext',
            'description': f'Received {len(ciphertext_nums)} encrypted values.'
        })
        
        # Decrypt each number
        plaintext_chars = []
        decryption_examples = []
        
        for i, c in enumerate(ciphertext_nums):
            m = pow(c, d, n)
            try:
                char = chr(m)
                plaintext_chars.append(char)
                
                if i < 5:
                    decryption_examples.append(f"{c} → {m} ('{char}')")
            except:
                plaintext_chars.append('?')
        
        steps.append({
            'title': 'Step 3: Decrypt Values',
            'description': f'For each ciphertext c: m = c^d mod n = c^{d} mod {n}\n\n' +
                          f'Examples:\n' + '\n'.join(decryption_examples) +
                          (f'\n...and {len(ciphertext_nums) - 5} more values' if len(ciphertext_nums) > 5 else '')
        })
        
        result = ''.join(plaintext_chars)
        
        steps.append({
            'title': 'Step 4: Complete',
            'description': f'Decrypted message:\n{result}'
        })
        
        return {
            'result': result,
            'steps': steps,
            'visualization_data': None
        }
