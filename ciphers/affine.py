from .base_cipher import BaseCipher
from typing import Dict, List, Any
from collections import Counter

class AffineCipher(BaseCipher):
    def get_name(self) -> str:
        return "Affine Cipher"
    
    def get_description(self) -> str:
        return """
        The Affine cipher is a monoalphabetic substitution cipher where each letter is mapped 
        to its numeric equivalent, encrypted using a mathematical function: E(x) = (ax + b) mod 26
        
        **Parameters**:
        - a: Multiplicative key (must be coprime with 26)
        - b: Additive key (shift value)
        
        **Valid 'a' values**: 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25
        
        **Weakness**: Only 312 possible keys, vulnerable to brute force and frequency analysis.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'a',
                'type': 'number',
                'label': 'Multiplicative key (a) - must be coprime with 26',
                'default': 5,
                'min': 1,
                'max': 25
            },
            {
                'name': 'b',
                'type': 'number',
                'label': 'Additive key (b)',
                'default': 8,
                'min': 0,
                'max': 25
            },
            {
                'name': 'brute_force',
                'type': 'checkbox',
                'label': 'Brute Force Mode (try all valid keys)',
                'default': False
            }
        ]
    
    def _gcd(self, a, b):
        while b:
            a, b = b, a % b
        return a
    
    def _mod_inverse(self, a, m):
        for i in range(1, m):
            if (a * i) % m == 1:
                return i
        return None
    
    def encrypt(self, plaintext: str, a: int = 5, b: int = 8, **params) -> Dict[str, Any]:
        steps = []
        a, b = int(a), int(b)
        
        if self._gcd(a, 26) != 1:
            return {
                'result': f'Error: a={a} is not coprime with 26. Valid values: 1,3,5,7,9,11,15,17,19,21,23,25',
                'steps': [{'title': 'Error', 'description': 'Invalid multiplicative key'}],
                'visualization_data': None
            }
        
        steps.append({
            'title': 'Step 1: Initialize',
            'description': f'Encryption formula: E(x) = (ax + b) mod 26\na = {a}, b = {b}\nValid because gcd({a}, 26) = 1'
        })
        
        result = []
        transformations = []
        
        for char in plaintext:
            if char.isalpha():
                is_upper = char.isupper()
                x = ord(char.upper()) - ord('A')
                encrypted = (a * x + b) % 26
                new_char = chr(encrypted + ord('A'))
                
                if len(transformations) < 5:
                    transformations.append(f'{char}({x}) → ({a}×{x}+{b})mod26 = {encrypted} → {new_char}')
                
                result.append(new_char if is_upper else new_char.lower())
            else:
                result.append(char)
        
        steps.append({
            'title': 'Step 2: Apply Affine Function',
            'description': 'Transformations:\n' + '\n'.join(transformations) +
                          ('\n...' if len(transformations) >= 5 else '')
        })
        
        ciphertext = ''.join(result)
        steps.append({
            'title': 'Step 3: Complete',
            'description': f'Result: {ciphertext}'
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
    
    def decrypt(self, ciphertext: str, a: int = 5, b: int = 8, brute_force: bool = False, **params) -> Dict[str, Any]:
        if brute_force:
            return self._brute_force_decrypt(ciphertext)
        
        steps = []
        a, b = int(a), int(b)
        
        if self._gcd(a, 26) != 1:
            return {
                'result': f'Error: a={a} is not coprime with 26',
                'steps': [{'title': 'Error', 'description': 'Invalid multiplicative key'}],
                'visualization_data': None
            }
        
        a_inv = self._mod_inverse(a, 26)
        
        steps.append({
            'title': 'Step 1: Calculate Inverse',
            'description': f'Decryption formula: D(y) = a^(-1)(y - b) mod 26\na^(-1) = {a_inv} (modular inverse of {a})'
        })
        
        result = []
        transformations = []
        
        for char in ciphertext:
            if char.isalpha():
                is_upper = char.isupper()
                y = ord(char.upper()) - ord('A')
                decrypted = (a_inv * (y - b)) % 26
                new_char = chr(decrypted + ord('A'))
                
                if len(transformations) < 5:
                    transformations.append(f'{char}({y}) → {a_inv}×({y}-{b})mod26 = {decrypted} → {new_char}')
                
                result.append(new_char if is_upper else new_char.lower())
            else:
                result.append(char)
        
        steps.append({
            'title': 'Step 2: Apply Decryption',
            'description': 'Transformations:\n' + '\n'.join(transformations) +
                          ('\n...' if len(transformations) >= 5 else '')
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
    
    def _brute_force_decrypt(self, ciphertext: str) -> Dict[str, Any]:
        """Try all valid key combinations (312 possibilities)."""
        steps = []

        # Valid values for 'a' (coprime with 26)
        valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]

        steps.append({
            'title': 'Brute Force Attack',
            'description': f'Trying all {len(valid_a) * 26} = {len(valid_a) * 26} possible key combinations.'
        })

        all_results = []
        scored_results = []
        structured_results = []  # For AI analysis

        for a in valid_a:
            a_inv = self._mod_inverse(a, 26)
            for b in range(26):
                result = []

                for char in ciphertext:
                    if char.isalpha():
                        is_upper = char.isupper()
                        y = ord(char.upper()) - ord('A')
                        decrypted = (a_inv * (y - b)) % 26
                        new_char = chr(decrypted + ord('A'))
                        result.append(new_char if is_upper else new_char.lower())
                    else:
                        result.append(char)

                decrypted = ''.join(result)
                
                # Calculate readability score
                score = self._calculate_english_score(decrypted)
                scored_results.append((score, a, b, decrypted))
                all_results.append(f"a={a:2d}, b={b:2d}: {decrypted}")

        # Sort by score (highest first)
        scored_results.sort(reverse=True)
        
        # Build structured results for AI
        for score, a, b, text in scored_results[:20]:  # Top 20 for AI
            structured_results.append({
                'key': f'a={a}, b={b}',
                'text': text,
                'score': score
            })
        
        # Get top 10 most likely results
        top_results = []
        for i, (score, a, b, decrypted) in enumerate(scored_results[:10], 1):
            top_results.append(f"#{i} [Score: {score:.3f}] a={a:2d}, b={b:2d}: {decrypted}")

        steps.append({
            'title': 'Top 10 Most Likely Results (AI-Scored)',
            'description': 'Ranked by English language probability:\n\n' + '\n'.join(top_results)
        })

        steps.append({
            'title': 'All Key Combinations (312 total)',
            'description': 'Complete results:\n\n' + '\n'.join(all_results)
        })

        steps.append({
            'title': 'How Scoring Works',
            'description': 'The AI scoring uses English letter frequency analysis and common word patterns. ' +
                          'Higher scores indicate text that looks more like English. ' +
                          'The top result is usually (but not always) correct!'
        })

        # Return top result as main output, with all results in steps
        result_text = f"Most Likely Result:\n{scored_results[0][3]}\n\n" + \
                     f"Keys: a={scored_results[0][1]}, b={scored_results[0][2]}\n\n" + \
                     "See 'Step-by-Step Explanation' for all 312 possibilities."

        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None,
            'brute_force_results': structured_results
        }
    
    def _calculate_english_score(self, text: str) -> float:
        """Calculate how likely text is English based on letter frequency and valid words."""
        # Expected English letter frequencies
        english_freq = {
            'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
            'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
            'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
            'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
            'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
        }
        
        # Common English words dictionary (expanded)
        common_words = {
            'THE', 'OF', 'TO', 'AND', 'A', 'IN', 'IS', 'IT', 'YOU', 'THAT',
            'HE', 'WAS', 'FOR', 'ON', 'ARE', 'WITH', 'AS', 'I', 'HIS', 'THEY',
            'BE', 'AT', 'ONE', 'HAVE', 'THIS', 'FROM', 'OR', 'HAD', 'BY', 'HOT',
            'BUT', 'SOME', 'WHAT', 'THERE', 'WE', 'CAN', 'OUT', 'OTHER', 'WERE', 'ALL',
            'YOUR', 'WHEN', 'UP', 'USE', 'WORD', 'HOW', 'SAID', 'AN', 'EACH', 'SHE',
            'WHICH', 'DO', 'THEIR', 'TIME', 'IF', 'WILL', 'WAY', 'ABOUT', 'MANY', 'THEN',
            'THEM', 'WOULD', 'WRITE', 'LIKE', 'SO', 'THESE', 'HER', 'LONG', 'MAKE', 'THING',
            'SEE', 'HIM', 'TWO', 'HAS', 'LOOK', 'MORE', 'DAY', 'COULD', 'GO', 'COME',
            'DID', 'MY', 'SOUND', 'NO', 'MOST', 'NUMBER', 'WHO', 'OVER', 'KNOW', 'WATER',
            'THAN', 'CALL', 'FIRST', 'PEOPLE', 'MAY', 'DOWN', 'SIDE', 'BEEN', 'NOW', 'FIND',
            'ANY', 'NEW', 'WORK', 'PART', 'TAKE', 'GET', 'PLACE', 'MADE', 'LIVE', 'WHERE',
            'AFTER', 'BACK', 'LITTLE', 'ONLY', 'ROUND', 'MAN', 'YEAR', 'CAME', 'SHOW', 'EVERY',
            'GOOD', 'ME', 'GIVE', 'OUR', 'UNDER', 'NAME', 'VERY', 'THROUGH', 'FORM', 'MUCH',
            'GREAT', 'THINK', 'HELP', 'LOW', 'LINE', 'BEFORE', 'TURN', 'CAUSE', 'SAME', 'MEAN',
            'DIFFER', 'MOVE', 'RIGHT', 'BOY', 'OLD', 'TOO', 'DOES', 'TELL', 'SENTENCE', 'SET',
            'THREE', 'WANT', 'AIR', 'WELL', 'ALSO', 'PLAY', 'SMALL', 'END', 'PUT', 'HOME',
            'READ', 'HAND', 'PORT', 'LARGE', 'SPELL', 'ADD', 'EVEN', 'LAND', 'HERE', 'MUST',
            'BIG', 'HIGH', 'SUCH', 'FOLLOW', 'ACT', 'WHY', 'ASK', 'MEN', 'CHANGE', 'WENT',
            'LIGHT', 'KIND', 'OFF', 'NEED', 'HOUSE', 'PICTURE', 'TRY', 'US', 'AGAIN', 'ANIMAL',
            'POINT', 'MOTHER', 'WORLD', 'NEAR', 'BUILD', 'SELF', 'EARTH', 'FATHER', 'HEAD', 'STAND',
            'OWN', 'PAGE', 'SHOULD', 'COUNTRY', 'FOUND', 'ANSWER', 'SCHOOL', 'GROW', 'STUDY', 'STILL',
            'LEARN', 'PLANT', 'COVER', 'FOOD', 'SUN', 'FOUR', 'THOUGHT', 'LET', 'KEEP', 'EYE',
            'NEVER', 'LAST', 'DOOR', 'BETWEEN', 'CITY', 'TREE', 'CROSS', 'SINCE', 'HARD', 'START',
            'MIGHT', 'STORY', 'SAW', 'FAR', 'SEA', 'DRAW', 'LEFT', 'LATE', 'RUN', 'DON\'T',
            'WHILE', 'PRESS', 'CLOSE', 'NIGHT', 'REAL', 'LIFE', 'FEW', 'STOP', 'OPEN', 'SEEM',
            'TOGETHER', 'NEXT', 'WHITE', 'CHILDREN', 'BEGIN', 'GOT', 'WALK', 'EXAMPLE', 'EASE', 'PAPER',
            'OFTEN', 'ALWAYS', 'MUSIC', 'THOSE', 'BOTH', 'MARK', 'BOOK', 'LETTER', 'UNTIL', 'MILE',
            'RIVER', 'CAR', 'FEET', 'CARE', 'SECOND', 'GROUP', 'CARRY', 'TOOK', 'RAIN', 'EAT',
            'ROOM', 'FRIEND', 'BEGAN', 'IDEA', 'FISH', 'MOUNTAIN', 'NORTH', 'ONCE', 'BASE', 'HEAR',
            'HORSE', 'CUT', 'SURE', 'WATCH', 'COLOR', 'FACE', 'WOOD', 'MAIN'
        }

        
        # Count letters in text
        text_upper = text.upper()
        letter_count = Counter(c for c in text_upper if c.isalpha())
        total = sum(letter_count.values())
        
        if total == 0:
            return 0.0
        
        # Calculate chi-squared statistic for letter frequency
        chi_squared = 0.0
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            expected = english_freq[letter] * total / 100
            observed = letter_count.get(letter, 0)
            if expected > 0:
                chi_squared += (observed - expected) ** 2 / expected
        
        # Base score from frequency (lower chi-squared is better)
        frequency_score = max(0, 100 - chi_squared)
        
        # Extract words from text (split by non-letters)
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
        
        # Score based on valid words
        if not words:
            return frequency_score
        
        # Count valid common words
        valid_word_count = sum(1 for word in words if word in common_words)
        valid_word_ratio = valid_word_count / len(words) if words else 0
        
        # Bonus for longer valid words
        long_word_bonus = sum(len(word) for word in words if len(word) >= 4 and word in common_words)
        
        # Count words that are at least 2 letters and all letters are valid
        reasonable_words = sum(1 for word in words if len(word) >= 2)
        
        # Penalty for very short "words" (single letters that aren't 'A' or 'I')
        single_letter_penalty = sum(1 for word in words if len(word) == 1 and word not in ['A', 'I'])
        
        # Calculate word score
        word_score = (
            (valid_word_ratio * 100) +           # 0-100 based on % of recognized words
            (long_word_bonus * 2) +              # Bonus for longer valid words
            (reasonable_words * 2) -             # Small bonus for reasonable word lengths
            (single_letter_penalty * 5)          # Penalty for suspicious single letters
        )
        
        # Combined score (weighted towards word validity)
        final_score = (frequency_score * 0.3) + (word_score * 0.7)
        
        return final_score

    # By Anton Wingeier
