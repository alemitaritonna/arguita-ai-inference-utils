#!/bin/bash

# Prompt de ejemplo
PROMPT="Explicame brevemente qué es el aprendizaje profundo"

# Llamada al endpoint Flask que corre en el puerto 5001
curl -X POST http://179.43.113.46:5001/ticker_analysis \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "'"$PROMPT"'",
        "max_tokens": 512,
        "temperature": 0.4,
        "user_id": 12
    }' | jq
