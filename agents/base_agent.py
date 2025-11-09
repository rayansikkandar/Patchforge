from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NEMOTRON_MODEL
from utils.logger import setup_logger
from typing import List, Dict, Optional

class NemotronAgent:
    def __init__(self, name: str, system_prompt: str, tools: Optional[List[Dict]] = None):
        self.name = name
        self.logger = setup_logger(f"Agent-{name}")
        self.client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY
        )
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.conversation_history = []
    
    def call_nemotron(self, user_message: str, temperature: float = 0.7) -> str:
        """Make a call to Nemotron"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history,
                {"role": "user", "content": user_message}
            ]
            
            kwargs = {
                "model": NEMOTRON_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2000
            }
            
            if self.tools:
                kwargs["tools"] = self.tools
                kwargs["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**kwargs)
            
            assistant_message = response.choices[0].message
            
            # Handle tool calls
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                self.logger.info(f"Tool calls requested: {len(assistant_message.tool_calls)}")
                return assistant_message
            
            content = assistant_message.content
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": content})
            
            return content
            
        except Exception as e:
            self.logger.error(f"Nemotron API error: {e}")
            raise
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []

