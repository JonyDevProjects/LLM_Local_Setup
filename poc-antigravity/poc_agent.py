"""PoC: Antigravity SDK + Ollama (ornith-1.5:35b) — agente local con tools."""

import asyncio
import sys
from datetime import datetime

from google.antigravity import Agent, LocalOpenAIAgentConfig
from google.antigravity.hooks import policy

MODEL = "ornith-1.5:35b"
BASE_URL = "http://localhost:11434/v1"


def get_current_datetime() -> str:
    """Devuelve la fecha y hora actuales del sistema en formato ISO."""
    return datetime.now().isoformat(timespec="seconds")


def calculate(operation: str, a: float, b: float) -> float:
    """Realiza una operación aritmética básica.

    Args:
        operation: Una de 'add', 'subtract', 'multiply', 'divide'.
        a: Primer número.
        b: Segundo número.
    """
    ops = {
        "add": lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide": lambda: a / b if b != 0 else float("nan"),
    }
    if operation not in ops:
        raise ValueError(f"Operación desconocida: {operation}")
    return ops[operation]()


async def main() -> None:
    config = LocalOpenAIAgentConfig(
        model=MODEL,
        base_url=BASE_URL,
    ).lightweight()

    config.tools = [get_current_datetime, calculate]
    config.policies = [policy.allow_all()]

    print(f"Conectando a Ollama ({MODEL} @ {BASE_URL})...\n")

    async with Agent(config) as agent:
        prompts = [
            "¿Qué hora es ahora? Usa la herramienta, no la adivines.",
            "Usando la herramienta de cálculo: ¿cuánto es 1734 * 29?",
        ]
        for prompt in prompts:
            print(f">>> Prompt: {prompt}")
            response = await agent.chat(prompt)
            print("<<< Respuesta:")
            async for token in response:
                print(token, end="", flush=True)
            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
