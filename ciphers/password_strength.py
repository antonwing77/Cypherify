from .base_cipher import BaseCipher
from typing import Dict, List, Any
import string

class PasswordStrengthCipher(BaseCipher):
    # Most common 4-digit PINs based on research
    COMMON_4_DIGIT_PINS = [
        '1234', '1111', '0000', '1212', '7777', '1004', '2000', '4444', '2222', '6969',
        '9999', '3333', '5555', '6666', '1122', '1313', '8888', '4321', '2001', '1010',
        '0909', '2580', '1818', '0808', '1230', '1984', '1986', '0070', '1985', '0666',
        '8520', '1987', '1231', '1000', '1998', '2468', '1357', '7410', '9876', '5678',
        '1314', '1980', '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997'
    ]
    
    # Common 6-digit PINs
    COMMON_6_DIGIT_PINS = [
        '123456', '654321', '111111', '000000', '123123', '666666', '121212', '112233',
        '789456', '159753', '123321', '100000', '777777', '555555', '888888', '222222'
    ]
    
    def get_name(self) -> str:
        return "Password & PIN Strength"
    
    def get_description(self) -> str:
        return """
        Demonstrates the security strength of passwords and PINs through brute force attack simulations.
        
        **What This Shows**:
        - How long it takes to crack passwords of different complexities
        - Why common PINs are extremely vulnerable
        - The importance of password length, special characters, and numbers
        - Real-world attack patterns used by hackers
        
        **PIN Security**:
        - 4-digit PIN: Only 10,000 possibilities (can be cracked in seconds)
        - 6-digit PIN: 1,000,000 possibilities (still weak)
        - Optimized attacks try common patterns first (1234, 0000, etc.)
        
        **Password Security**:
        - Length matters more than complexity
        - Each character type multiplies the keyspace exponentially
        - Modern GPUs can test billions of passwords per second
        
        **How to Use**: Enter a PIN or password in the input field and click "Analyze" to see how secure it is.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'mode',
                'type': 'select',
                'label': 'Analysis Mode',
                'default': '4pin_optimized',
                'options': [
                    {'label': '4-Digit PIN (Optimized Attack)', 'value': '4pin_optimized'},
                    {'label': '4-Digit PIN (Sequential Attack)', 'value': '4pin_sequential'},
                    {'label': '6-Digit PIN (Optimized Attack)', 'value': '6pin_optimized'},
                    {'label': '6-Digit PIN (Sequential Attack)', 'value': '6pin_sequential'},
                    {'label': 'Password Strength Analysis', 'value': 'password_analysis'}
                ]
            }
        ]
    
    def encrypt(self, plaintext: str, mode: str = '4pin_optimized', **params) -> Dict[str, Any]:
        """Analyze the PIN/password strength."""
        return self._analyze(plaintext, mode)
    
    def decrypt(self, ciphertext: str, mode: str = '4pin_optimized', **params) -> Dict[str, Any]:
        """Analyze the PIN/password strength."""
        return self._analyze(ciphertext, mode)
    
    def _analyze(self, target: str, mode: str) -> Dict[str, Any]:
        """Main analysis function."""
        if mode == '4pin_optimized':
            return self._brute_force_4pin_optimized(target)
        elif mode == '4pin_sequential':
            return self._brute_force_4pin_sequential(target)
        elif mode == '6pin_optimized':
            return self._brute_force_6pin_optimized(target)
        elif mode == '6pin_sequential':
            return self._brute_force_6pin_sequential(target)
        elif mode == 'password_analysis':
            return self._analyze_password_strength(target)
        
        return {
            'result': 'Invalid mode selected',
            'steps': [],
            'visualization_data': None
        }

    # By Anton Wingeier
    
    def _brute_force_4pin_optimized(self, target: str) -> Dict[str, Any]:
        """Brute force 4-digit PIN trying common patterns first."""
        steps = []
        
        if not target or not target.isdigit() or len(target) != 4:
            return {
                'result': 'Please enter a valid 4-digit PIN (e.g., 1234)',
                'steps': [{'title': 'Error', 'description': 'Target must be exactly 4 digits (0-9)'}],
                'visualization_data': None
            }
        
        steps.append({
            'title': 'Optimized Brute Force Attack Simulation',
            'description': f'Analyzing PIN: {target}\n' +
                          f'Strategy: Try most common PINs first\n' +
                          f'Total possibilities: 10,000 (0000-9999)\n' +
                          f'Common PINs database: {len(self.COMMON_4_DIGIT_PINS)} entries'
        })
        
        attempts = 0
        found = False
        
        # Try common PINs first
        for i, pin in enumerate(self.COMMON_4_DIGIT_PINS):
            attempts += 1
            if pin == target:
                found = True
                steps.append({
                    'title': '⚠️ CRITICAL SECURITY RISK!',
                    'description': f'PIN CRACKED in just {attempts} attempts!\n' +
                                  f'Found in position #{i+1} of common PINs list.\n\n' +
                                  f'Your PIN "{target}" is EXTREMELY INSECURE!\n' +
                                  f'Time to crack: <0.01 seconds\n\n' +
                                  f'Why this is bad:\n' +
                                  f'• Attackers try common PINs first\n' +
                                  f'• This PIN is in the top {i+1} most common\n' +
                                  f'• Can be guessed in seconds'
                })
                break
        
        if not found:
            # Would need to continue with sequential search
            target_num = int(target)
            attempts = len(self.COMMON_4_DIGIT_PINS) + target_num + 1
            
            steps.append({
                'title': 'PIN Security Analysis',
                'description': f'PIN not found in common patterns.\n' +
                              f'Estimated attempts needed: {attempts:,}\n' +
                              f'Time to crack (at 1,000 tries/sec): {attempts/1000:.2f} seconds\n' +
                              f'Time to crack (at 10,000 tries/sec): {attempts/10000:.2f} seconds\n\n' +
                              f'Security rating: WEAK\n' +
                              f'4-digit PINs can still be cracked in under 10 seconds.'
            })
        
        steps.append({
            'title': 'Top 20 Common PINs (Attackers Try These First)',
            'description': ', '.join(self.COMMON_4_DIGIT_PINS[:20]) + '\n\n' +
                          'These account for 27% of all PINs used!'
        })
        
        steps.append({
            'title': 'Recommendations',
            'description': '• Never use sequential numbers (1234, 4321)\n' +
                          '• Avoid repeated digits (1111, 2222)\n' +
                          '• Don\'t use dates (birth years, etc.)\n' +
                          '• Consider using 6+ digit PINs\n' +
                          '• Use alphanumeric passwords when possible'
        })
        
        security_rating = 'CRITICAL' if found and attempts < 20 else 'VERY WEAK' if found else 'WEAK'
        
        result_text = f"PIN: {target}\n" +\
                     f"Security Rating: {security_rating}\n" +\
                     f"Attempts to crack: {attempts:,} / 10,000\n" +\
                     f"Time: {attempts/1000:.2f} seconds\n\n" +\
                     f"{'🚨 This PIN is in the most common list!' if found else '⚠️ Still weak - only 10,000 possibilities'}"
        
        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None
        }
    
    def _brute_force_4pin_sequential(self, target: str) -> Dict[str, Any]:
        """Brute force 4-digit PIN sequentially."""
        if not target or not target.isdigit() or len(target) != 4:
            return {
                'result': 'Please enter a valid 4-digit PIN',
                'steps': [{'title': 'Error', 'description': 'Target must be exactly 4 digits'}],
                'visualization_data': None
            }
        
        target_num = int(target)
        attempts = target_num + 1
        
        steps = [{
            'title': 'Sequential Brute Force Analysis',
            'description': f'PIN: {target}\n' +
                          f'Strategy: Try every PIN from 0000 to 9999 in order\n\n' +
                          f'Results:\n' +
                          f'Attempts needed: {attempts:,}\n' +
                          f'Percentage of keyspace: {(attempts/10000)*100:.1f}%\n\n' +
                          f'Time estimates:\n' +
                          f'• At 100 tries/sec: {attempts/100:.1f} seconds\n' +
                          f'• At 1,000 tries/sec: {attempts/1000:.2f} seconds\n' +
                          f'• At 10,000 tries/sec: {attempts/10000:.3f} seconds\n\n' +
                          f'Security Rating: WEAK\n' +
                          f'All 4-digit PINs can be cracked in < 100 seconds'
        }]
        
        result_text = f"PIN: {target}\n" +\
                     f"Attempts: {attempts:,} / 10,000\n" +\
                     f"Time: ~{attempts/1000:.2f} sec"
        
        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None
        }
    
    def _brute_force_6pin_optimized(self, target: str) -> Dict[str, Any]:
        """Brute force 6-digit PIN analysis."""
        if not target or not target.isdigit() or len(target) != 6:
            return {
                'result': 'Please enter a valid 6-digit PIN',
                'steps': [{'title': 'Error', 'description': 'Target must be exactly 6 digits'}],
                'visualization_data': None
            }
        
        attempts = 0
        found = False
        
        # Check common patterns
        for pin in self.COMMON_6_DIGIT_PINS:
            attempts += 1
            if pin == target:
                found = True
                break
        
        if not found:
            target_num = int(target)
            attempts = len(self.COMMON_6_DIGIT_PINS) + target_num + 1
        
        steps = [{
            'title': '6-Digit PIN Security Analysis',
            'description': f'PIN: {target}\n' +
                          f'Total possibilities: 1,000,000\n\n' +
                          f'Optimized Attack Results:\n' +
                          f'Attempts needed: {attempts:,}\n' +
                          f'{"⚠️ Found in common patterns!" if found else "Not in common patterns"}\n\n' +
                          f'Time estimates:\n' +
                          f'• At 1,000 tries/sec: {attempts/1000:.1f} seconds\n' +
                          f'• At 10,000 tries/sec: {attempts/10000:.1f} seconds\n' +
                          f'• At 100,000 tries/sec: {attempts/100000:.1f} seconds\n\n' +
                          f'Security Rating: {"WEAK" if found else "MODERATE"}\n' +
                          f'6-digit PINs are better but still crackable in minutes'
        }]
        
        security_status = "WEAK (common pattern)" if found else "MODERATE"
        result_text = f"6-Digit PIN: {target}\n" +\
                     f"Attempts: {attempts:,} / 1,000,000\n" +\
                     f"Security: {security_status}"
        
        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None
        }
    
    def _brute_force_6pin_sequential(self, target: str) -> Dict[str, Any]:
        """Sequential 6-digit PIN analysis."""
        if not target or not target.isdigit() or len(target) != 6:
            return {
                'result': 'Please enter a valid 6-digit PIN',
                'steps': [{'title': 'Error', 'description': 'Target must be exactly 6 digits'}],
                'visualization_data': None
            }
        
        target_num = int(target)
        attempts = target_num + 1
        
        steps = [{
            'title': 'Sequential 6-Digit Attack',
            'description': f'PIN: {target}\n' +
                          f'Attempts: {attempts:,} / 1,000,000\n' +
                          f'Percentage: {(attempts/1000000)*100:.2f}%\n\n' +
                          f'Time estimates:\n' +
                          f'• At 1,000/sec: {attempts/1000:.1f} seconds\n' +
                          f'• At 10,000/sec: {attempts/10000:.1f} seconds\n' +
                          f'• At 100,000/sec: {attempts/100000:.1f} seconds'
        }]
        
        return {
            'result': f"6-Digit PIN: {target}\nAttempts: {attempts:,}\nTime: ~{attempts/10000:.1f} sec",
            'steps': steps,
            'visualization_data': None
        }
    
    def _analyze_password_strength(self, password: str) -> Dict[str, Any]:
        """Comprehensive password strength analysis."""
        if not password:
            return {
                'result': 'Please enter a password to analyze',
                'steps': [{'title': 'Error', 'description': 'Password cannot be empty'}],
                'visualization_data': None
            }
        
        steps = []
        
        # Analyze components
        length = len(password)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)
        
        # Calculate character set size
        charset_size = 0
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_digit:
            charset_size += 10
        if has_special:
            charset_size += 32
        
        if charset_size == 0:
            charset_size = 10  # fallback for unusual characters
        
        # Calculate keyspace
        keyspace = charset_size ** length
        
        steps.append({
            'title': 'Password Composition Analysis',
            'description': f'Length: {length} characters\n' +
                          f'Lowercase letters: {"✓" if has_lower else "✗"}\n' +
                          f'Uppercase letters: {"✓" if has_upper else "✗"}\n' +
                          f'Numbers: {"✓" if has_digit else "✗"}\n' +
                          f'Special characters: {"✓" if has_special else "✗"}\n\n' +
                          f'Character set size: {charset_size}\n' +
                          f'Total combinations: {keyspace:,.0f}'
        })
        
        # Time to crack (at 10 billion attempts/sec)
        rate = 10_000_000_000
        seconds = keyspace / rate
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        years = days / 365
        
        if years > 1000000:
            time_str = f'{years/1000000:.1f} million years'
        elif years > 1000:
            time_str = f'{years/1000:.1f} thousand years'
        elif years >= 1:
            time_str = f'{years:.1f} years'
        elif days >= 1:
            time_str = f'{days:.1f} days'
        elif hours >= 1:
            time_str = f'{hours:.1f} hours'
        elif minutes >= 1:
            time_str = f'{minutes:.1f} minutes'
        else:
            time_str = f'{seconds:.2f} seconds'
        
        # Security rating
        if years > 1000:
            rating = '🟢 EXCELLENT'
        elif years > 10:
            rating = '🟢 STRONG'
        elif years > 1:
            rating = '🟡 GOOD'
        elif days > 30:
            rating = '🟡 MODERATE'
        elif days > 1:
            rating = '🟠 WEAK'
        else:
            rating = '🔴 VERY WEAK'
        
        steps.append({
            'title': 'Brute Force Time Estimate',
            'description': f'At 10 billion attempts/second (modern GPU):\n' +
                          f'Time to crack: {time_str}\n\n' +
                          f'Security Rating: {rating}'
        })
        
        # Recommendations
        recommendations = []
        if length < 12:
            recommendations.append(f'• Increase length to 12+ characters (currently {length})')
        if not has_upper:
            recommendations.append('• Add uppercase letters (A-Z)')
        if not has_lower:
            recommendations.append('• Add lowercase letters (a-z)')
        if not has_digit:
            recommendations.append('• Add numbers (0-9)')
        if not has_special:
            recommendations.append('• Add special characters (!@#$%^&*)')
        
        if recommendations:
            steps.append({
                'title': 'Security Recommendations',
                'description': '\n'.join(recommendations)
            })
        else:
            steps.append({
                'title': 'Good Practices',
                'description': '✓ Your password has good character diversity!\n' +
                              '• Use different passwords for different accounts\n' +
                              '• Consider using a password manager\n' +
                              '• Change passwords periodically\n' +
                              '• Enable two-factor authentication when possible'
            })
        
        result_text = f"Password Strength: {rating}\n\n" +\
                     f"Length: {length} characters\n" +\
                     f"Character types: {sum([has_lower, has_upper, has_digit, has_special])}/4\n" +\
                     f"Time to crack: {time_str}\n" +\
                     f"Combinations: {keyspace:,.0f}"
        
        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None
        }
