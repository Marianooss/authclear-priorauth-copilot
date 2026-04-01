"""
a2a_agent/prompts — Agent prompt templates

Exports system prompt and prior auth letter template.
"""

from a2a_agent.prompts.system import build_system_prompt
from a2a_agent.prompts.prior_auth import PRIOR_AUTH_LETTER_TEMPLATE

__all__ = [
    "build_system_prompt",
    "PRIOR_AUTH_LETTER_TEMPLATE",
]
