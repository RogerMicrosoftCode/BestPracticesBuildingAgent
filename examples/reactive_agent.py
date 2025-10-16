"""
Reactive Agent Pattern Example

A reactive agent responds directly to environmental stimuli without maintaining
internal state or planning. This pattern is best for:
- Simple, fast responses
- Fully observable environments
- Situations where immediate reaction is more important than planning
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Enumeration of possible agent actions"""
    GREET = "greet"
    HELP = "help"
    SEARCH = "search"
    ERROR = "error"
    DEFAULT = "default"


@dataclass
class Perception:
    """Represents agent's perception of the environment"""
    input_text: str
    context: Dict[str, Any]
    timestamp: float


@dataclass
class Action:
    """Represents an action the agent can take"""
    action_type: ActionType
    response: str
    metadata: Dict[str, Any]


class ConditionActionRule(ABC):
    """Base class for condition-action rules"""
    
    @abstractmethod
    def matches(self, perception: Perception) -> bool:
        """Check if this rule matches the current perception"""
        pass
    
    @abstractmethod
    def execute(self, perception: Perception) -> Action:
        """Execute the action for this rule"""
        pass


class GreetingRule(ConditionActionRule):
    """Rule for handling greetings"""
    
    GREETING_KEYWORDS = ['hello', 'hi', 'hey', 'greetings']
    
    def matches(self, perception: Perception) -> bool:
        text_lower = perception.input_text.lower()
        return any(keyword in text_lower for keyword in self.GREETING_KEYWORDS)
    
    def execute(self, perception: Perception) -> Action:
        return Action(
            action_type=ActionType.GREET,
            response="Hello! How can I help you today?",
            metadata={'rule': 'greeting'}
        )


class HelpRule(ConditionActionRule):
    """Rule for handling help requests"""
    
    HELP_KEYWORDS = ['help', 'assist', 'support', 'how to']
    
    def matches(self, perception: Perception) -> bool:
        text_lower = perception.input_text.lower()
        return any(keyword in text_lower for keyword in self.HELP_KEYWORDS)
    
    def execute(self, perception: Perception) -> Action:
        help_text = """
        I can help you with:
        - Answering questions
        - Providing information
        - Searching for resources
        
        Just ask me anything!
        """
        return Action(
            action_type=ActionType.HELP,
            response=help_text.strip(),
            metadata={'rule': 'help'}
        )


class SearchRule(ConditionActionRule):
    """Rule for handling search requests"""
    
    SEARCH_KEYWORDS = ['search', 'find', 'look for', 'lookup']
    
    def matches(self, perception: Perception) -> bool:
        text_lower = perception.input_text.lower()
        return any(keyword in text_lower for keyword in self.SEARCH_KEYWORDS)
    
    def execute(self, perception: Perception) -> Action:
        # Extract search query (simplified)
        query = perception.input_text
        for keyword in self.SEARCH_KEYWORDS:
            query = query.lower().replace(keyword, '').strip()
        
        return Action(
            action_type=ActionType.SEARCH,
            response=f"Searching for: {query}",
            metadata={'rule': 'search', 'query': query}
        )


class DefaultRule(ConditionActionRule):
    """Fallback rule when no other rules match"""
    
    def matches(self, perception: Perception) -> bool:
        return True  # Always matches as fallback
    
    def execute(self, perception: Perception) -> Action:
        return Action(
            action_type=ActionType.DEFAULT,
            response="I understand you said: " + perception.input_text,
            metadata={'rule': 'default'}
        )


class ReactiveAgent:
    """
    A reactive agent that responds to inputs using condition-action rules.
    
    Best Practices Demonstrated:
    1. Clear separation of rules (modularity)
    2. Simple, fast decision making (no state, no planning)
    3. Ordered rule evaluation (priority handling)
    4. Fallback behavior (robustness)
    """
    
    def __init__(self):
        # Rules are evaluated in order - more specific rules first
        self.rules: List[ConditionActionRule] = [
            GreetingRule(),
            HelpRule(),
            SearchRule(),
            DefaultRule(),  # Always last as fallback
        ]
    
    def perceive(self, input_text: str, context: Dict[str, Any] = None) -> Perception:
        """Convert input into perception"""
        import time
        return Perception(
            input_text=input_text,
            context=context or {},
            timestamp=time.time()
        )
    
    def decide(self, perception: Perception) -> Action:
        """
        Select and execute the first matching rule.
        
        This implements the reactive agent's decision process:
        - Evaluate rules in order
        - Execute first matching rule
        - Guaranteed to return an action (DefaultRule always matches)
        """
        for rule in self.rules:
            if rule.matches(perception):
                return rule.execute(perception)
        
        # This should never be reached due to DefaultRule
        # but included for defensive programming
        return Action(
            action_type=ActionType.ERROR,
            response="Error: No matching rule found",
            metadata={'error': 'no_match'}
        )
    
    def act(self, action: Action) -> str:
        """Execute the selected action and return response"""
        # In a real agent, this might:
        # - Send messages
        # - Make API calls
        # - Update external systems
        # For this example, we just return the response
        return action.response
    
    def run(self, input_text: str, context: Dict[str, Any] = None) -> str:
        """
        Main agent loop: perceive -> decide -> act
        
        This is the classic reactive agent cycle.
        """
        # Perceive
        perception = self.perceive(input_text, context)
        
        # Decide
        action = self.decide(perception)
        
        # Act
        response = self.act(action)
        
        return response


def main():
    """Example usage of the reactive agent"""
    agent = ReactiveAgent()
    
    # Test cases demonstrating different rules
    test_inputs = [
        "Hello there!",
        "I need help",
        "Search for Python tutorials",
        "What is the weather like?",
    ]
    
    print("Reactive Agent Demo")
    print("=" * 50)
    
    for user_input in test_inputs:
        print(f"\nUser: {user_input}")
        response = agent.run(user_input)
        print(f"Agent: {response}")
    
    print("\n" + "=" * 50)
    print("\nBest Practices Demonstrated:")
    print("1. ✓ Modular rule-based architecture")
    print("2. ✓ Clear separation of perception, decision, and action")
    print("3. ✓ Ordered rule evaluation with fallback")
    print("4. ✓ Type safety with dataclasses and enums")
    print("5. ✓ Simple, fast responses (no state or planning)")


if __name__ == "__main__":
    main()
