from .base_cipher import BaseCipher
from typing import Dict, List, Any

class RailFenceCipher(BaseCipher):
    def get_name(self) -> str:
        return "Rail Fence Cipher"
    
    def get_description(self) -> str:
        return """
        The Rail Fence cipher is a transposition cipher that writes the message in a zigzag 
        pattern across multiple "rails" (rows), then reads off each rail sequentially.
        
        **Example** (3 rails):
        ```
        H . . . O . . . L . . .
        . E . L . W . R . D . !
        . . L . . . O . . . .
        ```
        Encrypted: "HOLLELWRD!"
        
        **Weakness**: Relatively easy to break with known rail count or pattern analysis.
        """
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'rails',
                'type': 'number',
                'label': 'Number of Rails',
                'default': 3,
                'min': 2,
                'max': 10
            },
            {
                'name': 'brute_force',
                'type': 'checkbox',
                'label': 'Brute Force Mode (try 2-10 rails)',
                'default': False
            }
        ]
    
    def encrypt(self, plaintext: str, rails: int = 3, **params) -> Dict[str, Any]:
        steps = []
        rails = int(rails)
        
        if rails < 2:
            return {
                'result': 'Error: Need at least 2 rails',
                'steps': [{'title': 'Error', 'description': 'Invalid rail count'}],
                'visualization_data': None
            }
        
        steps.append({
            'title': 'Step 1: Initialize',
            'description': f'Using {rails} rails. Text will be written in zigzag pattern.'
        })
        
        # Create rail fence
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1  # 1 for down, -1 for up
        
        for char in plaintext:
            fence[rail].append(char)
            rail += direction
            
            if rail == 0 or rail == rails - 1:
                direction *= -1
        
        # Create visualization
        visualization = []
        for i, rail_chars in enumerate(fence):
            rail_str = ''.join(rail_chars) if rail_chars else '(empty)'
            visualization.append(f'Rail {i+1}: {rail_str}')
        
        steps.append({
            'title': 'Step 2: Write in Zigzag Pattern',
            'description': 'Rail distribution:\n' + '\n'.join(visualization)
        })
        
        # Read off rails
        ciphertext = ''.join([''.join(rail) for rail in fence])
        
        steps.append({
            'title': 'Step 3: Read Rails Sequentially',
            'description': f'Result: {ciphertext}'
        })
        
        return {
            'result': ciphertext,
            'steps': steps,
            'visualization_data': None
        }
    
    def decrypt(self, ciphertext: str, rails: int = 3, brute_force: bool = False, **params) -> Dict[str, Any]:
        if brute_force:
            return self._brute_force_decrypt(ciphertext)
        
        steps = []
        rails = int(rails)
        
        if rails < 2:
            return {
                'result': 'Error: Need at least 2 rails',
                'steps': [{'title': 'Error', 'description': 'Invalid rail count'}],
                'visualization_data': None
            }
        
        steps.append({
            'title': 'Step 1: Calculate Rail Positions',
            'description': f'Determining character distribution across {rails} rails'
        })
        
        # Calculate positions
        fence_positions = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        
        for i in range(len(ciphertext)):
            fence_positions[rail].append(i)
            rail += direction
            
            if rail == 0 or rail == rails - 1:
                direction *= -1
        
        # Fill fence with characters
        fence = [[] for _ in range(rails)]
        idx = 0
        for i in range(rails):
            for _ in range(len(fence_positions[i])):
                if idx < len(ciphertext):
                    fence[i].append(ciphertext[idx])
                    idx += 1
        
        steps.append({
            'title': 'Step 2: Distribute Characters',
            'description': f'Characters distributed across {rails} rails based on zigzag pattern'
        })
        
        # Read in zigzag
        result = []
        rail = 0
        direction = 1
        rail_indices = [0] * rails
        
        for _ in range(len(ciphertext)):
            if rail_indices[rail] < len(fence[rail]):
                result.append(fence[rail][rail_indices[rail]])
                rail_indices[rail] += 1
            
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction *= -1
        
        plaintext = ''.join(result)
        
        steps.append({
            'title': 'Step 3: Read in Zigzag Order',
            'description': f'Result: {plaintext}'
        })
        
        return {
            'result': plaintext,
            'steps': steps,
            'visualization_data': None
        }
    
    def _brute_force_decrypt(self, ciphertext: str) -> Dict[str, Any]:
        """Try different rail counts to find the correct decryption."""
        steps = []
        
        steps.append({
            'title': 'Brute Force Attack',
            'description': 'Trying rail counts from 2 to 10. AI will analyze to find readable text!'
        })
        
        all_results = []
        structured_results = []  # For AI analysis
        
        for rails in range(2, 11):
            # Calculate positions
            fence_positions = [[] for _ in range(rails)]
            rail = 0
            direction = 1
            
            for i in range(len(ciphertext)):
                fence_positions[rail].append(i)
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1
            
            # Fill fence
            fence = [[] for _ in range(rails)]
            idx = 0
            for i in range(rails):
                for _ in range(len(fence_positions[i])):
                    if idx < len(ciphertext):
                        fence[i].append(ciphertext[idx])
                        idx += 1
            
            # Read in zigzag
            result = []
            rail = 0
            direction = 1
            rail_indices = [0] * rails
            
            for _ in range(len(ciphertext)):
                if rail_indices[rail] < len(fence[rail]):
                    result.append(fence[rail][rail_indices[rail]])
                    rail_indices[rail] += 1
                
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1
            
            decrypted = ''.join(result)
            all_results.append(f"{rails} rails: {decrypted}")
            structured_results.append((f"{rails} rails", decrypted))
        
        steps.append({
            'title': 'All Rail Counts Tried',
            'description': 'Results:\n\n' + '\n'.join(all_results)
        })
        
        steps.append({
            'title': 'How to Find the Answer',
            'description': 'Look for the result that makes sense. Rail Fence is weak against brute force with only 9 possibilities (2-10 rails).\n\n' +
                          'AI Teacher will analyze these results to identify the correct decryption!'
        })
        
        result_text = '\n'.join(all_results)
        
        return {
            'result': result_text,
            'steps': steps,
            'visualization_data': None,
            'brute_force_results': structured_results
        }
