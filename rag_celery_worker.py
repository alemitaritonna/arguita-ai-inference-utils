from rag_celery_config import celery_app
from celery import Task
from llama_index.llms.ollama import Ollama
import threading

# Singleton para instancia del modelo LLM usando LlamaIndex y Ollama
class SingletonModel:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("Inicializando modelo Ollama via LlamaIndex (singleton)...")
                    cls._instance = Ollama(
                        #model="qwen2.5-optimo:latest",
                        model="qwen2.5:latest",
                        #model="qwen2.5:3b",
                        #model="llama3.2:3b",
                        base_url="http://localhost:11434",  # Ollama local
                        temperature=0.5,
                        request_timeout=600
                    )
                    print("Modelo inicializado correctamente")
        return cls._instance

# Clase base de tareas que accede al modelo
class ModelTask(Task):
    _model = None
    _lock = threading.Lock()

    @property
    def model(self):
        if self._model is None:
            self._model = SingletonModel.get_instance()
        return self._model

# Tarea Celery para procesar inferencias
@celery_app.task(base=ModelTask, bind=True)
def process_inference(self, prompt, max_tokens=512, temperature=0.5, user_id=None):
    try:
        print(f"\nProcesando prompt de {len(prompt)} caracteres para usuario {user_id}...")

        # Lock específico por usuario para evitar condiciones de carrera
        if not hasattr(self, '_user_locks'):
            self._user_locks = {}

        if user_id not in self._user_locks:
            self._user_locks[user_id] = threading.Lock()

        user_lock = self._user_locks[user_id]

        with user_lock:
            llm = self.model
            response = llm.complete(prompt=prompt, max_tokens=max_tokens)
            result = response.text.strip()

            print(f"Inferencia completada para usuario {user_id}: {len(result)} caracteres generados")
            return result

    except Exception as e:
        print(f"Error en inferencia para usuario {user_id}: {str(e)}")
        return {'error': str(e)}




# from rag_celery_config import celery_app
# from celery import Task
# from llama_cpp import Llama
# import threading

# class SingletonModel:
#     _instance = None
#     _lock = threading.Lock()

#     @classmethod
#     def get_instance(cls):
#         if cls._instance is None:
#             with cls._lock:
#                 if cls._instance is None:
#                     print("Inicializando modelo (singleton)...")
#                     cls._instance = Llama.from_pretrained(
#                         repo_id="BafS/gemma-2-2b-it-Q4_K_M-GGUF",
#                         filename="gemma-2-2b-it-q4_k_m.gguf",
#                         n_ctx=8192,
#                         n_gpu_layers=-1,
#                         n_batch=512,
#                         n_threads=12
#                     )
#                     print("Modelo inicializado correctamente")
#         return cls._instance


# class ModelTask(Task):
#     _model = None
#     _lock = threading.Lock()

#     @property
#     def model(self):
#         if self._model is None:
#             self._model = SingletonModel.get_instance()
#         return self._model


# @celery_app.task(base=ModelTask, bind=True)
# def process_inference(self, prompt, max_tokens=1024, temperature=0.6, user_id=None):
#     try:
#         print(f"\nProcesando prompt de {len(prompt)} caracteres para usuario {user_id}...")
        
#         # Creamos un lock específico por usuario si no existe
#         if not hasattr(self, '_user_locks'):
#             self._user_locks = {}
        
#         # Obtenemos o creamos un lock específico para este usuario
#         if user_id not in self._user_locks:
#             self._user_locks[user_id] = threading.Lock()
        
#         user_lock = self._user_locks[user_id]
        
#         with user_lock:  # Usar el lock específico del usuario
#             output = self.model.create_chat_completion(
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                 ],
#                 max_tokens=max_tokens,
#                 temperature=temperature
#             )
#             result = output['choices'][0]['message']['content'].strip()
            
#             print(f"Inferencia completada para usuario {user_id}: {len(result)} caracteres generados")

#             return result
        
#     except Exception as e:
#         print(f"Error en inferencia para usuario {user_id}: {str(e)}")
#         return {'error': str(e)}