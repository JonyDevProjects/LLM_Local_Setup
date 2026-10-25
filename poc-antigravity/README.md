# PoC: Agentes Autónomos con LiteRT/Llama

**⚠️ NOTA:** Este directorio contiene prototipos de agentes autónomos usando la 
[Google Antigravity SDK](https://github.com/google-gemini/antigravity). 

El código requiere instalación manual del SDK y no está incluido en la distribución pública.

## Componentes

| Archivo | Propósito |
|---------|-----------|
| `poc_agent.py` | Agente local conectado a Ollama (`ornith-1.5:35b`) |
| `poc_litert_agent.py` | Agente local conectado a LiteRT-LM (`gemma4-26b`) |
| `config-experiments.json` | Config LiteRT para experimentos |

## Requisitos para ejecutar

```bash
cd poc-antigravity
python3 -m venv .venv
source .venv/bin/activate
pip install google-antigravity litert-lm-cli  # paquetes externos
python poc_agent.py    # o poc_litert_agent.py
```

> Los modelos de LLM subyacentes (Ollama, LiteRT) deben instalarse por separado.
