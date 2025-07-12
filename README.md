# Arguita AI Inference & RAG Utils

## 📄 Descripción General

Este repositorio contiene una suite de scripts en Python y utilidades de shell diseñadas para el despliegue y la gestión de sistemas de Inferencia de Modelos de IA y Recuperación Aumentada por Generación (RAG). Nuestro objetivo es proporcionar herramientas eficientes para la orquestación de tareas asíncronas y el servicio de modelos de IA en diversos entornos.

El proyecto se enfoca en:

- **Eficiencia**: Optimización de la carga y ejecución de modelos.
- **Escalabilidad**: Uso de Celery para procesamiento asíncrono y distribuido.
- **Automatización**: Scripts de shell para la gestión simplificada de servicios.

## 🚀 Características Destacadas

- **Inferencia de Modelos**: Scripts base para cargar y ejecutar modelos de inteligencia artificial de manera optimizada.
- **Recuperación Aumentada por Generación (RAG)**: Componentes dedicados a la integración de sistemas de recuperación de información con modelos generativos para respuestas contextuales.
- **Servidores Gunicorn**: Configuraciones robustas para la publicación de APIs de inferencia y RAG.
- **Workers de Celery**: Implementación de tareas asíncronas para el procesamiento en segundo plano y la escalabilidad de las operaciones.
- **Scripts de Monitoreo**: Utilidades de shell para iniciar, detener y monitorear el estado de los servicios clave.
- **Bases de Datos Vectoriales**: Integración con sistemas de bases de datos vectoriales (como ChromaDB) para la gestión y búsqueda eficiente de embeddings.
- **Gestión de Modelos**: Funcionalidades para la carga dinámica y la gestión de diferentes modelos de IA.

## 📁 Estructura del Proyecto

```bash
.
├── __pycache__/             
├── chroma_db/               
├── env/                     
├── env_models/              
├── models/                  
│
├── gunicorn.inference.py
├── gunicorn.inference_models.py
├── gunicorn.rag.py
│
├── inference.py
├── inference_models.py
│
├── kill_services.sh
├── models_celery_config.py
├── models_celery_worker.py
│
├── monit_celery_models_worker.sh
├── monit_celery_rag_worker.sh
├── monit_gunicorn_inference.sh
├── monit_gunicorn_models.sh
├── monit_gunicorn_rag.sh
│
├── rag.py
├── rag_celery_config.py
├── rag_celery_worker.py
│
├── restart_services.sh
├── start_services.sh
├── suggest_monit_matching.sh
├── test.sh
├── test_celery.py
├── test_ollama.py
│
└── .gitignore
````

## ⚙️ Requisitos del Sistema

* Python 3.x (versión recomendada: 3.8 o superior)
* pip
* Git
* Gunicorn
* Celery
* **Broker de Mensajes**: Redis
* \[Opcional] Ollama

## 💻 Instalación de Dependencias de Python

```bash
# 1. Crea un entorno virtual (si no existe)
python3 -m venv env

# 2. Activa el entorno virtual
source env/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt
```

> Asegúrate de que el archivo `requirements.txt` esté actualizado:
>
> ```bash
> pip freeze > requirements.txt
> ```

## 🚀 Uso

### Configuración Inicial

```bash
git clone https://github.com/alemitaritonna/arguita-ai-inference-utils.git
cd arguita-ai-inference-utils
```

### Ejecución de Servicios

```bash
# Iniciar todos los servicios
./start_services.sh

# Reiniciar todos los servicios
./restart_services.sh

# Detener todos los servicios
./kill_services.sh
```

### Monitoreo de Servicios

Los scripts con prefijo `monit_` están pensados para integrarse con `monit` o `systemd`.

### Uso de Scripts Específicos

* **`inference.py`**: Carga modelos de IA y realiza inferencias.

```bash
python inference.py --model_path /ruta/a/tu/modelo
```

* **`rag.py`**: Sistema RAG: recuperación de documentos + generación.

```bash
python rag.py --query "Pregunta sobre el documento"
```

* **`test_celery.py`**: Verifica la configuración de Celery.

```bash
python test_celery.py
```

* **`test_ollama.py`**: Prueba la integración con Ollama.

```bash
python test_ollama.py
```


## 📜 Licencia

Este proyecto está bajo la licencia **\[Nombre de la Licencia, ej. MIT License]**. Revisa el archivo `LICENSE`.

## 📞 Contacto

* GitHub: [alemitaritonna](https://github.com/alemitaritonna)
* Email: \[[tu.email@ejemplo.com](mailto:tu.email@ejemplo.com)]


