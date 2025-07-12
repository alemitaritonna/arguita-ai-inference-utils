from llama_index.llms.ollama import Ollama

llm = Ollama(
    model="qwen2.5:latest",
    base_url="http://localhost:11434",
    temperature=0.6,
    request_timeout=120  # ⏱️ aumentamos a 2 minutos
)

response = llm.complete(prompt="¿Qué es un modelo de lenguaje?")
print(response.text)
