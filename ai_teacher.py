import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AITeacher:
    def __init__(self):
        """Initialize the AI Teacher with OpenAI API."""
        # Check for API key in environment
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.enabled = bool(self.api_key)
        self.client = None
        
        # Only initialize if API key exists and is valid
        if self.api_key and self.api_key.strip() and not self.api_key.startswith('your_'):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
                print("✓ AI Teacher initialized successfully")
            except Exception as e:
                print(f"⚠ AI Teacher initialization failed: {e}")
                self.enabled = False
        else:
            print("⚠ AI Teacher disabled: No valid API key found")
        
        self.system_prompt = """You are an expert cryptography teacher helping students learn about encryption and ciphers. 
You are part of an educational web application called Cypherify that teaches various encryption methods.

Your role is to:
- Explain cryptographic concepts clearly and simply
- Answer questions about specific ciphers (Caesar, Vigenère, RSA, AES, etc.)
- Help students understand the mathematics behind encryption
- Explain the history and real-world applications of cryptography
- Discuss security strengths and weaknesses of different methods
- Always emphasize that the implementations shown are for EDUCATIONAL purposes only

Keep your responses concise (2-4 paragraphs) but informative. Use examples when helpful.
If asked about implementing real security, always recommend using established libraries and consulting security professionals."""
    
    def ask(self, question: str, cipher_context: str = None, conversation_history: list = None) -> dict:
        """
        Ask the AI teacher a question.
        
        Args:
            question: The student's question
            cipher_context: Optional context about which cipher they're viewing
            conversation_history: Previous messages in the conversation
            
        Returns:
            dict with 'success', 'response', and optional 'error' keys
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI Teacher is not configured. Please add your OpenAI API key to the .env file.'
            }
        
        try:
            # Build the message with context
            user_message = question
            if cipher_context:
                user_message = f"[Context: Student is learning about {cipher_context}]\n\n{question}"
            
            # Build messages array with history
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current question
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                'success': True,
                'response': answer
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error communicating with AI: {str(e)}'
            }
    
    def get_cipher_hint(self, cipher_name: str, operation: str) -> dict:
        """
        Get a helpful hint about using a specific cipher.
        
        Args:
            cipher_name: Name of the cipher
            operation: 'encrypt' or 'decrypt'
            
        Returns:
            dict with 'success', 'response', and optional 'error' keys
        """
        question = f"Give me a helpful tip for {operation}ing with the {cipher_name}. Keep it brief and practical."
        return self.ask(question, cipher_name)
    
    def analyze_brute_force_results(self, results: list, cipher_name: str) -> dict:
        """
        Analyze brute force results to find the most likely correct decryption.
        
        Args:
            results: List of dicts with 'key' and 'text' for each attempt
            cipher_name: Name of the cipher being analyzed
            
        Returns:
            dict with 'success', 'best_match', 'confidence', 'explanation'
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI Teacher is not configured.'
            }
        
        if not results or len(results) == 0:
            return {
                'success': False,
                'error': 'No results to analyze'
            }
        
        try:
            # Prepare summary of results for AI
            summary = f"Cipher: {cipher_name}\n\n"
            summary += "Top 10 decryption attempts:\n\n"
            
            for i, result in enumerate(results[:10], 1):
                summary += f"{i}. {result['key']}: {result['text'][:100]}...\n"
            
            prompt = f"""Analyze these brute force decryption results and identify which one is most likely correct English text.

{summary}

Provide your analysis in this format:
BEST_MATCH: [number 1-10]
CONFIDENCE: [high/medium/low]
REASONING: [brief explanation why this is most likely correct]

Consider:
- Proper English words and grammar
- Coherent meaning
- Natural letter patterns
- Sentence structure"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying English text from cipher decryptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            # Parse the response
            best_match_num = 1
            confidence = "medium"
            reasoning = "Analysis complete"
            
            for line in answer.split('\n'):
                if 'BEST_MATCH:' in line:
                    try:
                        best_match_num = int(''.join(filter(str.isdigit, line)))
                    except:
                        pass
                elif 'CONFIDENCE:' in line:
                    if 'high' in line.lower():
                        confidence = 'high'
                    elif 'low' in line.lower():
                        confidence = 'low'
                elif 'REASONING:' in line:
                    reasoning = line.split('REASONING:', 1)[1].strip()
            
            # Ensure index is valid
            best_match_num = max(1, min(best_match_num, len(results)))
            
            return {
                'success': True,
                'best_match': results[best_match_num - 1],
                'confidence': confidence,
                'explanation': reasoning
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analyzing results: {str(e)}'
            }
