from .base_cipher import BaseCipher
from typing import Dict, List, Any
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
import json

class AESCipher(BaseCipher):
    def __init__(self):
        self._last_keys = None

    def get_name(self) -> str:
        return "AES (Advanced Encryption Standard)"

    def get_description(self) -> str:
        return """
        **Hybrid Encryption** — the way real email encryption (PGP/GPG) works.

        1. **Generate Keys**: Creates an RSA-2048 key pair (public + private)
        2. **Encrypt**: Generates a random AES-256 key, encrypts your message with AES,
           then encrypts the AES key with the recipient's RSA public key
        3. **Decrypt**: Uses the RSA private key to recover the AES key, then decrypts the message

        **How to use for email**: Generate keys, share your **public key** with anyone.
        They encrypt messages with it. Only your **private key** can decrypt them.

        **Security**: RSA-2048 + AES-256-CBC. Production-grade key sizes.
        """

    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'mode',
                'type': 'select',
                'label': 'Mode',
                'default': 'generate',
                'options': [
                    {'label': 'Generate Key Pair', 'value': 'generate'},
                    {'label': 'Use Existing Keys', 'value': 'existing'}
                ]
            },
            {
                'name': 'public_key',
                'type': 'textarea',
                'label': 'Public Key (Base64 — paste recipient\'s public key here)',
                'default': ''
            },
            {
                'name': 'private_key',
                'type': 'textarea',
                'label': 'Private Key (Base64 — keep this SECRET)',
                'default': ''
            }

# By Anton Wingeier
        ]

    def _generate_keypair(self):
        """Generate an RSA-2048 key pair, return PEM bytes."""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem, pub_pem

    def _pem_to_b64(self, pem_bytes: bytes) -> str:
        """Compress PEM to single-line Base64 for easy copy-paste."""
        return base64.b64encode(pem_bytes).decode('utf-8')

    def _b64_to_pem(self, b64_str: str) -> bytes:
        """Restore PEM from single-line Base64."""
        return base64.b64decode(b64_str)

    def encrypt(self, plaintext: str, mode: str = 'generate', public_key: str = '', **params) -> Dict[str, Any]:
        steps = []

        # --- Key pair ---
        if mode == 'generate' or not public_key.strip():
            priv_pem, pub_pem = self._generate_keypair()
            pub_b64 = self._pem_to_b64(pub_pem)
            priv_b64 = self._pem_to_b64(priv_pem)
            self._last_keys = {'public': pub_b64, 'private': priv_b64}

            steps.append({
                'title': 'Step 1: Generate RSA-2048 Key Pair',
                'description': (
                    'Generated a fresh RSA-2048 key pair.\n\n'
                    f'PUBLIC KEY (share this — anyone can encrypt to you):\n{pub_b64[:80]}...\n\n'
                    f'PRIVATE KEY (keep SECRET — only you can decrypt):\n{priv_b64[:80]}...\n\n'
                    'Copy both keys from the parameter fields above. '
                    'Share the public key; guard the private key.'
                )
            })
        else:
            pub_b64 = public_key.strip()
            try:
                pub_pem = self._b64_to_pem(pub_b64)
            except Exception as e:
                expected_len = 604
                return {
                    'result': f'Error: Invalid public key. Make sure you copied the ENTIRE key ({expected_len} characters). Your key is {len(pub_b64)} characters. ({e})',
                    'steps': [{'title': 'Error', 'description': f'The public key appears truncated or corrupted. Expected ~{expected_len} characters, got {len(pub_b64)}. Make sure you copied the complete key.'}],
                    'visualization_data': None
                }
            priv_b64 = params.get('private_key', '')
            steps.append({
                'title': 'Step 1: Using Provided Public Key',
                'description': f'Public key loaded ({len(pub_b64)} chars). Will encrypt with this key.'
            })

        # Load RSA public key object
        try:
            rsa_pub = serialization.load_pem_public_key(
                pub_pem if isinstance(pub_pem, bytes) else pub_pem.encode()
            )
        except Exception as e:
            return {
                'result': f'Error: Invalid public key — {e}',
                'steps': steps + [{'title': 'Error', 'description': str(e)}],
                'visualization_data': None
            }

        # --- AES session key ---
        aes_key = get_random_bytes(32)  # AES-256
        iv = get_random_bytes(16)

        steps.append({
            'title': 'Step 2: Generate Random AES-256 Session Key',
            'description': (
                f'AES key: {base64.b64encode(aes_key).decode()[:20]}... (32 bytes / 256 bits)\n'
                f'IV: {base64.b64encode(iv).decode()[:20]}... (16 bytes)\n\n'
                'A fresh random key is created for every message. '
                'This key encrypts the actual text (fast). '
                'RSA encrypts only this small key (secure).'
            )
        })

        # --- Encrypt message with AES ---
        plaintext_bytes = plaintext.encode('utf-8')
        padded = pad(plaintext_bytes, AES.block_size)
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(padded)

        steps.append({
            'title': 'Step 3: Encrypt Message with AES-256-CBC',
            'description': (
                f'Plaintext: {len(plaintext_bytes)} bytes → Padded: {len(padded)} bytes → '
                f'{len(ciphertext) // 16} blocks encrypted.\n\n'
                'AES is fast and handles large messages efficiently.'
            )
        })

        # --- Encrypt AES key with RSA public key ---
        encrypted_aes_key = rsa_pub.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        steps.append({
            'title': 'Step 4: Encrypt AES Key with RSA Public Key',
            'description': (
                f'RSA-OAEP encrypted the 32-byte AES key → {len(encrypted_aes_key)} bytes.\n\n'
                'Only the matching private key can recover the AES key. '
                'This is how PGP/GPG email encryption works.'
            )
        })

        # --- Package everything ---
        package = {
            'encrypted_key': base64.b64encode(encrypted_aes_key).decode(),
            'iv': base64.b64encode(iv).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode()
        }
        result_str = base64.b64encode(json.dumps(package).encode()).decode()

        steps.append({
            'title': 'Step 5: Package & Encode',
            'description': (
                f'Combined encrypted AES key + IV + ciphertext into one Base64 string.\n'
                f'Final message: {len(result_str)} characters.\n\n'
                'Send this entire string to anyone. Only the private key holder can decrypt it.'
            )
        })

        # If we generated keys, show them prominently
        if mode == 'generate' or not public_key.strip():
            steps.append({
                'title': 'IMPORTANT: Save Your Keys',
                'description': (
                    f'PUBLIC KEY (share freely):\n{pub_b64}\n\n'
                    f'PRIVATE KEY (keep secret):\n{priv_b64}\n\n'
                    'The public and private keys have been filled into the parameter fields above. '
                    'Copy them now — they cannot be regenerated.'
                )
            })

        ret = {
            'result': result_str,
            'steps': steps,
            'visualization_data': {
                'type': 'block_structure',
                'blocks': len(ciphertext) // 16,
                'key_size': 256
            }
        }
        # Attach keys so the UI can display them with copy buttons
        if mode == 'generate' or not public_key.strip():
            ret['generated_keys'] = {
                'public': pub_b64,
                'private': priv_b64
            }
        return ret

    def decrypt(self, ciphertext: str, mode: str = 'generate', private_key: str = '', **params) -> Dict[str, Any]:
        steps = []

        # --- Get private key ---
        priv_b64 = private_key.strip() if private_key else ''
        if not priv_b64 and self._last_keys:
            priv_b64 = self._last_keys['private']
            steps.append({
                'title': 'Step 1: Using Generated Private Key',
                'description': 'Using the private key from the last key generation.'
            })
        elif priv_b64:
            steps.append({
                'title': 'Step 1: Using Provided Private Key',
                'description': f'Private key loaded ({len(priv_b64)} chars).'
            })
        else:
            return {
                'result': 'Error: No private key available. Generate keys first or paste your private key.',
                'steps': [{'title': 'Error', 'description': 'No private key provided. Generate a key pair first, then paste the private key.'}],
                'visualization_data': None
            }

        # Load RSA private key
        try:
            priv_pem = self._b64_to_pem(priv_b64)
            rsa_priv = serialization.load_pem_private_key(priv_pem, password=None)
        except Exception as e:
            return {
                'result': f'Error: Invalid private key — {e}',
                'steps': steps + [{'title': 'Error', 'description': f'Could not load private key: {e}'}],
                'visualization_data': None
            }

        # --- Unpackage ---
        try:
            package = json.loads(base64.b64decode(ciphertext.strip()))
            encrypted_aes_key = base64.b64decode(package['encrypted_key'])
            iv = base64.b64decode(package['iv'])
            ct_bytes = base64.b64decode(package['ciphertext'])
        except Exception as e:
            return {
                'result': f'Error: Invalid encrypted message format — {e}',
                'steps': steps + [{'title': 'Error', 'description': f'Could not parse encrypted message: {e}'}],
                'visualization_data': None
            }

        steps.append({
            'title': 'Step 2: Unpackage Encrypted Message',
            'description': (
                f'Extracted:\n'
                f'- Encrypted AES key: {len(encrypted_aes_key)} bytes\n'
                f'- IV: {len(iv)} bytes\n'
                f'- Ciphertext: {len(ct_bytes)} bytes ({len(ct_bytes) // 16} blocks)'
            )
        })

        # --- Decrypt AES key with RSA private key ---
        try:
            aes_key = rsa_priv.decrypt(
                encrypted_aes_key,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except Exception as e:
            return {
                'result': 'Error: Decryption failed — wrong private key or corrupted message.',
                'steps': steps + [{'title': 'Error', 'description': f'RSA decryption failed: {e}. This usually means the private key does not match the public key used to encrypt.'}],
                'visualization_data': None
            }

        steps.append({
            'title': 'Step 3: Decrypt AES Key with RSA Private Key',
            'description': (
                f'RSA-OAEP decrypted the AES session key: {len(aes_key)} bytes (AES-{len(aes_key)*8}).\n\n'
                'Only the correct private key could recover this.'
            )
        })

        # --- Decrypt message with AES ---
        try:
            cipher = AES.new(aes_key, AES.MODE_CBC, iv)
            padded_plaintext = cipher.decrypt(ct_bytes)
            plaintext = unpad(padded_plaintext, AES.block_size).decode('utf-8')
        except Exception as e:
            return {
                'result': f'Error: AES decryption failed — {e}',
                'steps': steps + [{'title': 'Error', 'description': f'AES decryption failed: {e}'}],
                'visualization_data': None
            }

        steps.append({
            'title': 'Step 4: Decrypt Message with AES-256-CBC',
            'description': (
                f'Decrypted {len(ct_bytes)} bytes → {len(plaintext)} characters of plaintext.\n\n'
                'Message successfully recovered!'
            )
        })

        return {
            'result': plaintext,
            'steps': steps,
            'visualization_data': None
        }
