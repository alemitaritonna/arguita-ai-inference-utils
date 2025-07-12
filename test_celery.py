from rag_celery_worker import process_inference

r = process_inference.apply(args=[
    "Explicame qué es el aprendizaje profundo.",
    512, 0.4, 12
])
print(r.get(timeout=180))
