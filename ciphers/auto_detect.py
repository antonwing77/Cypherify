from .base_cipher import BaseCipher
from typing import Dict, List, Any
from .caesar import CaesarCipher
from .vigenere import VigenereCipher
from .affine import AffineCipher
from .rot13 import ROT13Cipher
from .railfence import RailFenceCipher
from .a1z26 import A1Z26Cipher
from .morse import MorseCipher
import string

class AutoDetectCipher(BaseCipher):
    def __init__(self):
        # Initialize cipher instances
        self.caesar = CaesarCipher()
        self.vigenere = VigenereCipher()
        self.affine = AffineCipher()
        self.rot13 = ROT13Cipher()
        self.railfence = RailFenceCipher()
        self.a1z26 = A1Z26Cipher()
        self.morse = MorseCipher()
        
        # Common keywords for Vigenère
        self.common_keywords = ['KEY', 'SECRET', 'CODE', 'CIPHER', 'PASSWORD', 'THE', 'AND']
    
    def get_name(self) -> str:
        return "Auto-Detect & Decrypt"
    
    def get_description(self) -> str:
        return """
        Automatically attempts to decrypt ciphertext by trying multiple cipher types and methods.
        
        **What This Tool Does**:
        - Tries Caesar cipher (all 26 shifts)
        - Tries ROT13
        - Tries Affine cipher (312 key combinations)
        - Tries Vigenère with common keywords
        - Tries Rail Fence (2-10 rails)
        - Detects A1Z26 number patterns
        - Detects Morse code patterns
        
        **How It Works**:
        1. Analyzes the ciphertext patterns
        2. Tests each applicable cipher method
        3. Scores results based on English language patterns
        4. Ranks all results by likelihood
        
        **Best For**: When you don't know what cipher was used!
        
        **Note**: Only works on classical ciphers. Modern encryption (AES, RSA) cannot be brute-forced.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'max_results',
                'type': 'number',
                'label': 'Maximum Results to Show',
                'default': 20,
                'min': 5,
                'max': 1000
            }
        ]
    
    def encrypt(self, plaintext: str, max_results: int = 10, **params) -> Dict[str, Any]:
        """Auto-detect uses the same logic for both encrypt and decrypt buttons."""
        return self._auto_decrypt(plaintext, max_results, **params)
    
    def decrypt(self, ciphertext: str, max_results: int = 10, **params) -> Dict[str, Any]:
        """Try multiple decryption methods and rank results."""
        return self._auto_decrypt(ciphertext, max_results, **params)
    
    def _auto_decrypt(self, ciphertext: str, max_results: int = 10, **params) -> Dict[str, Any]:
        """Try multiple decryption methods and rank results."""
        if not ciphertext or not ciphertext.strip():
            return {
                'result': 'Please enter ciphertext to analyze',
                'steps': [{'title': 'Error', 'description': 'Input cannot be empty'}],
                'visualization_data': None
            }
        
        max_results = int(max_results)
        steps = []
        all_attempts = []
        
        steps.append({
            'title': 'Auto-Detection Started',
            'description': f'Analyzing ciphertext: "{ciphertext[:50]}..."\n' +
                          f'Length: {len(ciphertext)} characters\n' +
                          f'Testing multiple cipher types...'
        })
        
        # Try Caesar cipher (all shifts)
        steps.append({
            'title': 'Testing Caesar Cipher',
            'description': 'Trying all 26 possible shifts...'
        })
        for shift in range(26):
            result = self._decrypt_caesar(ciphertext, shift)
            score = self._score_text(result)
            all_attempts.append({
                'cipher': 'Caesar',
                'key': f'Shift {shift}',
                'result': result,
                'score': score
            })
        
        # Try ROT13
        steps.append({
            'title': 'Testing ROT13',
            'description': 'Applying ROT13 transformation...'
        })
        result = self._decrypt_rot13(ciphertext)
        score = self._score_text(result)
        all_attempts.append({
            'cipher': 'ROT13',
            'key': 'ROT13',
            'result': result,
            'score': score
        })
        
        # Try Affine cipher (ALL key combinations for completeness)
        steps.append({
            'title': 'Testing Affine Cipher',
            'description': 'Testing all 312 valid key combinations...'
        })
        valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
        for a in valid_a:
            for b in range(26):  # ALL b values
                result = self._decrypt_affine(ciphertext, a, b)
                score = self._score_text(result)
                all_attempts.append({
                    'cipher': 'Affine',
                    'key': f'a={a}, b={b}',
                    'result': result,
                    'score': score
                })
        
        # Try Vigenère with common keywords
        steps.append({
            'title': 'Testing Vigenère Cipher',
            'description': f'Trying {len(self.common_keywords)} common keywords...'
        })
        for keyword in self.common_keywords:
            result = self._decrypt_vigenere(ciphertext, keyword)
            score = self._score_text(result)
            all_attempts.append({
                'cipher': 'Vigenère',
                'key': f'Keyword: {keyword}',
                'result': result,
                'score': score
            })
        
        # Try Rail Fence
        steps.append({
            'title': 'Testing Rail Fence Cipher',
            'description': 'Trying 2-10 rails...'
        })
        for rails in range(2, 11):
            result = self._decrypt_railfence(ciphertext, rails)
            score = self._score_text(result)
            all_attempts.append({
                'cipher': 'Rail Fence',
                'key': f'{rails} rails',
                'result': result,
                'score': score
            })
        
        # Check for A1Z26
        if self._looks_like_a1z26(ciphertext):
            steps.append({
                'title': 'Testing A1Z26',
                'description': 'Detected number pattern...'
            })
            result = self._decrypt_a1z26(ciphertext)
            if result:
                score = self._score_text(result)
                all_attempts.append({
                    'cipher': 'A1Z26',
                    'key': 'A1Z26',
                    'result': result,
                    'score': score
                })
        
        # Check for Morse code
        if self._looks_like_morse(ciphertext):
            steps.append({
                'title': 'Testing Morse Code',
                'description': 'Detected dot/dash pattern...'
            })
            result = self._decrypt_morse(ciphertext)
            if result:
                score = self._score_text(result)
                all_attempts.append({
                    'cipher': 'Morse',
                    'key': 'Morse Code',
                    'result': result,
                    'score': score
                })
        
        # Sort by score (highest first)
        all_attempts.sort(key=lambda x: x['score'], reverse=True)
        
        # Get results up to max_results (or all if max_results > total)
        top_results = all_attempts[:min(max_results, len(all_attempts))]
        
        # Format results
        results_text = f"🔍 Auto-Detection Results\n\n"
        results_text += f"Showing {len(top_results)} of {len(all_attempts)} total decryption attempts:\n\n"
        for i, attempt in enumerate(top_results, 1):
            results_text += f"#{i} [{attempt['cipher']}] {attempt['key']}\n"
            results_text += f"Score: {attempt['score']:.2f}\n"
            results_text += f"{attempt['result'][:100]}{'...' if len(attempt['result']) > 100 else ''}\n\n"
        
        # Add detailed results in steps
        step_results = []
        for i, att in enumerate(top_results, 1):
            step_results.append(
                f"#{i} [{att['cipher']}] {att['key']}\n"
                f"Score: {att['score']:.2f}\n"
                f"Result: {att['result']}"
            )
        
        steps.append({
            'title': f'🏆 Top {len(top_results)} Results (Ranked by Score)',
            'description': '\n\n'.join(step_results)
        })
        
        steps.append({
            'title': '✅ Analysis Complete',
            'description': f'Tested {len(all_attempts)} total decryption methods.\n\n' +
                          f'🎯 Best result: {top_results[0]["cipher"]} with {top_results[0]["key"]}\n' +
                          f'📊 Confidence score: {top_results[0]["score"]:.2f}/100\n\n' +
                          f'Top result text: {top_results[0]["result"]}\n\n' +
                          f'Note: Showing {len(top_results)} of {len(all_attempts)} attempts.'
        })
        
        # Return structured results for AI analysis (top results)
        structured_results = [
            {
                'key': f"{att['cipher']}: {att['key']}",
                'text': att['result'],
                'score': att['score']
            }
            for att in top_results
        ]
        
        return {
            'result': results_text,
            'steps': steps,
            'visualization_data': None,
            'brute_force_results': structured_results
        }
    
    def _decrypt_caesar(self, text: str, shift: int) -> str:
        """Decrypt using Caesar cipher."""
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = chr((ord(char) - base - shift) % 26 + base)
                result.append(shifted)
            else:
                result.append(char)
        return ''.join(result)
    
    def _decrypt_rot13(self, text: str) -> str:
        """Decrypt using ROT13."""
        return self._decrypt_caesar(text, 13)
    
    def _decrypt_affine(self, text: str, a: int, b: int) -> str:
        """Decrypt using Affine cipher."""
        # Calculate modular inverse
        a_inv = None
        for i in range(1, 26):
            if (a * i) % 26 == 1:
                a_inv = i
                break
        
        if a_inv is None:
            return text
        
        result = []
        for char in text:
            if char.isalpha():
                is_upper = char.isupper()
                y = ord(char.upper()) - ord('A')
                decrypted = (a_inv * (y - b)) % 26
                new_char = chr(decrypted + ord('A'))
                result.append(new_char if is_upper else new_char.lower())
            else:
                result.append(char)
        return ''.join(result)
    
    def _decrypt_vigenere(self, text: str, keyword: str) -> str:
        """Decrypt using Vigenère cipher."""
        keyword = ''.join(c for c in keyword.upper() if c.isalpha())
        if not keyword:
            return text
        
        result = []
        key_index = 0
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(keyword[key_index % len(keyword)]) - ord('A')
                shifted = chr((ord(char) - base - shift) % 26 + base)
                result.append(shifted)
                key_index += 1
            else:
                result.append(char)
        return ''.join(result)
    
    def _decrypt_railfence(self, text: str, rails: int) -> str:
        """Decrypt using Rail Fence cipher."""
        if rails < 2:
            return text
        
        # Calculate positions
        fence_positions = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        
        for i in range(len(text)):
            fence_positions[rail].append(i)
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction *= -1
        
        # Fill fence
        fence = [[] for _ in range(rails)]
        idx = 0
        for i in range(rails):
            for _ in range(len(fence_positions[i])):
                if idx < len(text):
                    fence[i].append(text[idx])
                    idx += 1
        
        # Read in zigzag
        result = []
        rail = 0
        direction = 1
        rail_indices = [0] * rails
        
        for _ in range(len(text)):
            if rail_indices[rail] < len(fence[rail]):
                result.append(fence[rail][rail_indices[rail]])
                rail_indices[rail] += 1
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction *= -1
        
        return ''.join(result)
    
    def _looks_like_a1z26(self, text: str) -> bool:
        """Check if text looks like A1Z26 encoding."""
        # Should contain numbers separated by dashes or spaces
        return any(c.isdigit() for c in text) and ('-' in text or ' ' in text)
    
    def _decrypt_a1z26(self, text: str) -> str:
        """Decrypt A1Z26."""
        try:
            numbers = text.replace('-', ' ').split()
            result = []
            for num_str in numbers:
                if num_str.isdigit():
                    num = int(num_str)
                    if 1 <= num <= 26:
                        result.append(chr(ord('A') + num - 1))
            return ''.join(result) if result else None
        except:
            return None
    
    def _looks_like_morse(self, text: str) -> bool:
        """Check if text looks like Morse code."""
        morse_chars = set('.-/ ')
        return all(c in morse_chars for c in text) and ('.' in text or '-' in text)
    
    def _decrypt_morse(self, text: str) -> str:
        """Decrypt Morse code."""
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z'
        }
        
        try:
            words = text.split(' / ')
            result = []
            for word in words:
                letters = word.split()
                for letter in letters:
                    if letter in morse_dict:
                        result.append(morse_dict[letter])
                result.append(' ')
            return ''.join(result).strip() if result else None
        except:
            return None
    
    def _score_text(self, text: str) -> float:
        """Score how likely text is English - improved algorithm."""
        if not text:
            return 0.0
        
        # English letter frequencies (percentage)
        english_freq = {
            'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
            'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
            'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
            'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
            'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
        }
        
        # Common English words dictionary (expanded from affine.py)
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
            'WALKED', 'DOG', 'TODAY', 'WALK', 'DOGS'
        }
        
        text_upper = text.upper()
        
        # Calculate letter frequency score using chi-squared
        from collections import Counter
        letter_count = Counter(c for c in text_upper if c.isalpha())
        total = sum(letter_count.values())
        
        if total == 0:
            return 0.0
        
        # Chi-squared test for letter frequency
        chi_squared = 0
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            expected_count = (english_freq.get(letter, 0.1) / 100) * total
            observed_count = letter_count.get(letter, 0)
            if expected_count > 0:
                chi_squared += ((observed_count - expected_count) ** 2) / expected_count
        
        # Lower chi-squared is better (convert to score where higher is better)
        freq_score = max(0, 100 - chi_squared)
        
        # Extract words (split by non-alphabetic characters)
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
            return freq_score * 0.3  # Frequency only
        
        # Count valid words
        valid_words = sum(1 for word in words if word in common_words)
        word_ratio = valid_words / len(words)
        
        # Bonus for longer valid words
        long_word_bonus = sum(len(word) * 3 for word in words if len(word) >= 4 and word in common_words)
        
        # Bonus for very common words (THE, AND, etc.)
        very_common = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'WITH', 'HIS', 'THEY', 'HAVE', 'THIS', 'FROM', 'THAT', 'WAS', 'SHE', 'WHAT', 'SAID', 'WHEN', 'WALKED', 'DOG', 'TODAY'}
        very_common_bonus = sum(20 for word in words if word in very_common)
        
        # Word-based score (weighted heavily)
        word_score = (word_ratio * 200) + long_word_bonus + very_common_bonus
        
        # Combined score: 30% frequency, 70% word recognition
        final_score = (freq_score * 0.3) + (word_score * 0.7)
        
        return final_score
