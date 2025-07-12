Arguita AI Inference & RAG Utils
📄 Descripción General
Este repositorio contiene una suite de scripts en Python y utilidades de shell diseñadas para el despliegue y la gestión de sistemas de Inferencia de Modelos de IA y Recuperación Aumentada por Generación (RAG). Nuestro objetivo es proporcionar herramientas eficientes para la orquestación de tareas asíncronas y el servicio de modelos de IA en diversos entornos.

El proyecto se enfoca en:

Eficiencia: Optimización de la carga y ejecución de modelos.

Escalabilidad: Uso de Celery para procesamiento asíncrono y distribuido.

Automatización: Scripts de shell para la gestión simplificada de servicios.

🚀 Características Destacadas
Inferencia de Modelos: Scripts base para cargar y ejecutar modelos de inteligencia artificial de manera optimizada.

Recuperación Aumentada por Generación (RAG): Componentes dedicados a la integración de sistemas de recuperación de información con modelos generativos para respuestas contextuales.

Servidores Gunicorn: Configuraciones robustas para la publicación de APIs de inferencia y RAG.

Workers de Celery: Implementación de tareas asíncronas para el procesamiento en segundo plano y la escalabilidad de las operaciones.

Scripts de Monitoreo: Utilidades de shell para iniciar, detener y monitorear el estado de los servicios clave.

Bases de Datos Vectoriales: Integración con sistemas de bases de datos vectoriales (como ChromaDB) para la gestión y búsqueda eficiente de embeddings.

Gestión de Modelos: Funcionalidades para la carga dinámica y la gestión de diferentes modelos de IA.

📁 Estructura del Proyecto
A continuación, se detalla la organización de los archivos y directorios principales dentro de este repositorio:

.
├── __pycache__/             # Directorio de caché de Python (ignorado por .gitignore)
├── chroma_db/               # Base de datos vectorial (ChromaDB - Ignorado por .gitignore)
├── env/                     # Entorno virtual de Python (Ignorado por .gitignore)
├── env_models/              # Otro entorno virtual (Ignorado por .gitignore)
├── models/                  # Directorio para almacenar modelos de IA (Ignorado por .gitignore)
│
├── gunicorn.inference.py    # Configuración de Gunicorn para el servicio de inferencia.
├── gunicorn.inference_models.py # Configuración de Gunicorn para el servicio de gestión de modelos.
├── gunicorn.rag.py          # Configuración de Gunicorn para el servicio RAG.
│
├── inference.py             # Lógica principal para la ejecución de inferencias con modelos.
├── inference_models.py      # Lógica para la carga, descarga y gestión de modelos.
│
├── kill_services.sh         # Script de shell para detener todos los servicios Gunicorn y Celery.
├── models_celery_config.py  # Archivo de configuración para los workers de Celery de modelos.
├── models_celery_worker.py  # Implementación del worker de Celery para tareas relacionadas con modelos.
│
├── monit_celery_models_worker.sh # Script de monitoreo para el worker de Celery de modelos.
├── monit_celery_rag_worker.sh    # Script de monitoreo para el worker de Celery de RAG.
├── monit_gunicorn_inference.sh   # Script de monitoreo para la instancia de Gunicorn de inferencia.
├── monit_gunicorn_models.sh      # Script de monitoreo para la instancia de Gunicorn de modelos.
├── monit_gunicorn_rag.sh         # Script de monitoreo para la instancia de Gunicorn de RAG.
│
├── rag.py                   # Lógica principal para el sistema de Recuperación Aumentada por Generación (RAG).
├── rag_celery_config.py     # Archivo de configuración para los workers de Celery de RAG.
├── rag_celery_worker.py     # Implementación del worker de Celery para tareas relacionadas con RAG.
│
├── restart_services.sh      # Script de shell para reiniciar todos los servicios.
├── start_services.sh        # Script de shell para iniciar todos los servicios.
├── suggest_monit_matching.sh # Script de shell para sugerir configuraciones de monitoreo basadas en los servicios.
├── test.sh                  # Script de shell para pruebas generales del entorno.
├── test_celery.py           # Script de Python para probar la funcionalidad de Celery.
├── test_ollama.py           # Script de Python para probar la integración con Ollama (si aplica).
│
└── .gitignore               # Archivo de configuración de Git para ignorar archivos y directorios.

⚙️ Requisitos del Sistema
Para poder ejecutar y desarrollar con estos scripts, necesitarás tener instalados los siguientes componentes en tu sistema:

Python 3.x (versión recomendada: 3.8 o superior)

pip (el gestor de paquetes de Python)

Git (para clonar y gestionar el repositorio)

Gunicorn (servidor WSGI para aplicaciones Python)

Celery (sistema de cola de tareas distribuidas)

Broker de Mensajes: Un broker como RabbitMQ o Redis es necesario para que Celery funcione.

[Opcional] Ollama: Si planeas utilizar los scripts de prueba o funcionalidades que interactúan con Ollama, asegúrate de tenerlo instalado y configurado.

Instalación de Dependencias de Python
Se recomienda encarecidamente crear y activar un entorno virtual para gestionar las dependencias de Python de forma aislada:

# 1. Crea un entorno virtual (si no existe)
python3 -m venv env

# 2. Activa el entorno virtual
source env/bin/activate

# 3. Instala las dependencias listadas en requirements.txt
pip install -r requirements.txt

Nota: Asegúrate de que el archivo requirements.txt esté actualizado con todas las bibliotecas de Python que tus scripts necesitan. Puedes generarlo ejecutando pip freeze > requirements.txt en tu entorno virtual después de instalar todas las dependencias.

🚀 Uso
Configuración Inicial
Clonar el Repositorio:

git clone https://github.com/alemitaritonna/arguita-ai-inference-utils.git
cd arguita-ai-inference-utils

Instalar Dependencias:
Sigue los pasos de la sección "Instalación de Dependencias de Python" para configurar tu entorno.

Configurar Variables de Entorno:
Algunos scripts (especialmente los de Gunicorn y Celery) pueden depender de variables de entorno para configurar puertos, URLs de brokers, rutas a modelos o claves API. Asegúrate de que estas variables estén definidas en tu entorno de ejecución.

Si utilizas un archivo .env o similar para cargar variables de entorno, menciónalo aquí y explica cómo cargarlo (ej. source .env).

Ejecución de Servicios
Los scripts de shell en la raíz del proyecto facilitan la gestión de los servicios principales:

Iniciar todos los servicios (Gunicorn y Celery workers):

./start_services.sh

Reiniciar todos los servicios:

./restart_services.sh

Detener todos los servicios:

./kill_services.sh

Monitoreo de Servicios
Los scripts con prefijo monit_ están diseñados para ser integrados con un sistema de monitoreo como monit o systemd para asegurar la alta disponibilidad de los servicios críticos.

Si tienes configuraciones específicas para monit o instrucciones detalladas sobre cómo usar estos scripts de monitoreo, agrégalas aquí.

Uso de Scripts Específicos
inference.py: Este script contiene la lógica para cargar modelos de IA y realizar inferencias. Puedes interactuar con él a través de la API expuesta por Gunicorn.

Ejemplo de uso: python inference.py --model_path /ruta/a/tu/modelo (ajusta según la implementación).

rag.py: Implementa el sistema RAG, combinando la recuperación de documentos con la generación de texto.

Ejemplo de uso: python rag.py --query "Pregunta sobre el documento" (ajusta según la implementación).

test_celery.py: Utilízalo para verificar que la configuración de Celery es correcta y que los workers están procesando tareas.

Ejemplo de uso: python test_celery.py

test_ollama.py: Si estás usando Ollama, este script te ayudará a probar la conexión y las funcionalidades básicas.

Ejemplo de uso: python test_ollama.py

🤝 Contribuciones
¡Las contribuciones son bienvenidas y muy apreciadas! Si deseas contribuir a este proyecto, por favor sigue estos pasos:

Haz un "fork" de este repositorio.

Crea una nueva rama para tu funcionalidad o corrección (git checkout -b feature/nombre-de-tu-funcionalidad o fix/correccion-de-bug).

Realiza tus cambios y commitea con un mensaje claro y descriptivo (git commit -m 'feat: Añadir soporte para nuevo modelo X').

Sube tus cambios a tu repositorio forkeado (git push origin feature/nombre-de-tu-funcionalidad).

Abre un Pull Request desde tu rama hacia la rama main de este repositorio.

📜 Licencia
Este proyecto está bajo la licencia [Nombre de la Licencia, ej. MIT License]. Consulta el archivo LICENSE en la raíz del repositorio para más detalles sobre los términos y condiciones de uso.

📞 Contacto
Para cualquier pregunta, comentario o sugerencia, no dudes en contactarme:

GitHub: @alemitaritonna

Email (Opcional): [tu.email@ejemplo.com]
