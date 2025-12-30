from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class ConversationTurn:
    question: str
    code: str
    result_summary: str
    timestamp: datetime

class ConversationManager:
    def __init__(self, max_history: int = 5):
        self.history: List[ConversationTurn] = []
        self.max_history = max_history

    def add_turn(self, question: str, code: str, result_summary: str):
        """Adds a turn to the history."""
        turn = ConversationTurn(
            question=question,
            code=code,
            result_summary=result_summary,
            timestamp=datetime.now()
        )
        self.history.append(turn)
        
        # Keep only last N turns
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context_for_llm(self) -> str:
        """
        Formats history for LLM context. 
        Returns a string of previous Q&A.
        """
        if not self.history:
            return ""
            
        context = ["Historial de conversación reciente:"]
        for turn in self.history:
            context.append(f"Usuario: {turn.question}")
            context.append(f"Tú (código generado): {turn.code}")
            context.append(f"Sistema (resultado): {turn.result_summary}")
            context.append("---")
            
        return "\n".join(context)

    def clear(self):
        self.history = []
