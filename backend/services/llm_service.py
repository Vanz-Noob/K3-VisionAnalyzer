import os
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "openai is not installed. "
        "Install it with: pip install openai"
    )


class LLMService:
    """BytePlus Seed LLM Service for image analysis."""
    
    def __init__(self):
        """Initialize OpenAI client with BytePlus Ark API."""
        self.api_key = os.environ.get("ARK_API_KEY")
        self.base_url = os.environ.get(
            "ARK_BASE_URL",
            "https://ark.ap-southeast.bytepluses.com/api/v3"
        )
        self.model = os.environ.get("ARK_MODEL", "seed-2-0-code-preview-260328")
        
        if not self.api_key:
            raise ValueError(
                "Missing required ARK_API_KEY environment variable"
            )
        
        # Initialize OpenAI client for BytePlus Ark
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
    
    def analyze_image(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze an image using BytePlus Seed LLM.
        
        Args:
            image_url: URL of the image to analyze
            prompt: User prompt for analysis (optional, defaults to fixed K3 prompt if None)
            system_prompt: Optional system prompt (optional, defaults to fixed K3 system prompt if None)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary containing content, model, and usage
        """
        # Default K3 system prompt
        default_system_prompt = (
            "Anda adalah ahli Kesehatan dan Keselamatan Kerja (K3). "
            "Tugas Anda adalah menganalisis gambar orang yang bekerja untuk mengecek kelengkapan Alat Pelindung Diri (APD).\n\n"
            "ATURAN PENTING:\n"
            "Jika di dalam gambar TIDAK ditemukan orang (subjek manusia) atau hanya berisi barang/pemandangan saja, "
            "Anda WAJIB memberikan jawaban dalam format JSON berikut:\n"
            '{\n'
            '  "hasSubject": false,\n'
            '  "individuals": [],\n'
            '  "overallCompliance": "N/A",\n'
            '  "summary": "tidak ada subject yang dapat di analisa"\n'
            '}\n\n'
            "Jika ditemukan orang, Anda WAJIB memberikan jawaban dalam format JSON berikut:\n"
            '{\n'
            '  "hasSubject": true,\n'
            '  "individuals": [\n'
            '    {\n'
            '      "id": 1,\n'
            '      "ppeItems": [\n'
            '        {"name": "Helm Proyek", "worn": true},\n'
            '        {"name": "Rompi Reflektif", "worn": true},\n'
            '        {"name": "Sepatu Safety", "worn": false},\n'
            '        {"name": "Sarung Tangan", "worn": false},\n'
            '        {"name": "Kacamata Safety", "worn": false}\n'
            '      ],\n'
            '      "compliance": "Non-Compliant",\n'
            '      "missingItems": ["Sepatu Safety", "Sarung Tangan", "Kacamata Safety"],\n'
            '      "recommendation": "Gunakan sepatu safety, sarung tangan, dan kacamata safety"\n'
            '    }\n'
            '  ],\n'
            '  "overallCompliance": "Non-Compliant",\n'
            '  "summary": "Dari 1 orang yang teridentifikasi, 1 orang tidak mematuhi standar APD K3."\n'
            '}\n\n'
            "PENTING: Selalu gunakan nilai \"Compliant\" atau \"Non-Compliant\" untuk field compliance. "
            "Berikan jawaban dalam Bahasa Indonesia yang profesional dan jelas. "
            "Hanya berikan output JSON saja, tanpa teks tambahan apapun seperti markdown code blocks."
        )
        
        # Default user prompt
        default_user_prompt = (
            "Tolong lakukan audit K3 visual pada gambar ini. "
            "Identifikasi setiap individu yang terlihat dan periksa apakah mereka menggunakan APD standar "
            "(seperti helm proyek, rompi visibilitas tinggi, sepatu pelindung, masker, atau kacamata safety). "
            "Sebutkan apa yang mereka pakai, apa yang kurang, dan berikan penilaian akhir apakah mereka "
            "sudah patuh (Compliant) atau tidak patuh (Non-Compliant) terhadap standar keselamatan kerja."
        )
        
        current_system_prompt = system_prompt if system_prompt else default_system_prompt
        current_user_prompt = prompt if prompt else default_user_prompt
        
        # Build messages array
        messages = [
            {
                "role": "system",
                "content": current_system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    },
                    {
                        "type": "text",
                        "text": current_user_prompt
                    }
                ]
            }
        ]
        
        try:
            # Call the LLM API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
            )
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content
            
            # Extract usage information if available
            usage = None
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "inputTokens": response.usage.prompt_tokens,
                    "outputTokens": response.usage.completion_tokens,
                    "totalTokens": response.usage.total_tokens,
                }
            
            return {
                "content": content,
                "analysis": self._parse_json_response(content),
                "model": self.model,
                "usage": usage,
            }
            
        except Exception as e:
            raise Exception(f"Failed to analyze image: {str(e)}")

    def _parse_json_response(self, content: str) -> dict:
        import json
        import re
        try:
            # Try to find JSON in markdown code blocks first
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # If not in a code block, try to find anything that looks like a JSON object
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                # Clean potential whitespace/newlines before/after
                json_str = json_match.group(1).strip()
                return json.loads(json_str)
            
            # Last resort: try to parse the whole thing
            return json.loads(content.strip())
        except (json.JSONDecodeError, AttributeError, Exception) as e:
            logger.error(f"JSON Parsing Error: {str(e)} | Content: {content[:100]}...")
            return {
                "hasSubject": None, 
                "individuals": [], 
                "overallCompliance": "N/A", 
                "summary": content,
                "error": "Failed to parse structured data"
            }

    def chat(
        self,
        messages: list,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        General chat completion method.
        
        Args:
            messages: Array of message objects
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary containing content, model, and usage
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
            )
            
            choice = response.choices[0]
            content = choice.message.content
            
            usage = None
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "inputTokens": response.usage.prompt_tokens,
                    "outputTokens": response.usage.completion_tokens,
                    "totalTokens": response.usage.total_tokens,
                }
            
            return {
                "content": content,
                "model": self.model,
                "usage": usage,
            }
            
        except Exception as e:
            raise Exception(f"Failed to complete chat: {str(e)}")


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service