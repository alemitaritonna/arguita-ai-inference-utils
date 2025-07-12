# Tamano de prompt:
# RAG contexto (4500) + template/instrucciones (~1000) = Prompt total (~5500) < Límite servidor (6000) < n_ctx del modelo (8192)

from flask import Flask, request, jsonify
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from pypdf import PdfReader
import tempfile
import os
import traceback
from rag_celery_config import celery_app
import celery.exceptions
import time

import redis

# Inicializar cliente Redis (junto con las otras inicializaciones)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

print("Iniciando servidor RAG...")

app = Flask(__name__)

# Configuraciones
# Configuraciones
INFERENCE_SERVER = "http://localhost:5001"
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_TTL = 3600  # Tiempo de vida de las colecciones en segundos (1 hora)
BASE_COLLECTION_NAME = "documentos_procesados"

print(f"CHROMA_PERSIST_DIR: {CHROMA_PERSIST_DIR}")

# Crear directorio de persistencia si no existe
if not os.path.exists(CHROMA_PERSIST_DIR):
    print(f"Creando directorio de persistencia: {CHROMA_PERSIST_DIR}")
    os.makedirs(CHROMA_PERSIST_DIR)

print(f"Permisos del directorio: {oct(os.stat(CHROMA_PERSIST_DIR).st_mode)[-3:]}")



IGNORE_TERMS = [
    # Español
    "AVISO LEGAL",
    "TÉRMINOS Y CONDICIONES",
    "DERECHOS RESERVADOS",
    "CONFIDENCIAL",
    "DESCARGO DE RESPONSABILIDAD",
    "NOTA LEGAL",
    "ADVERTENCIA LEGAL",
    "PROPIEDAD INTELECTUAL",
    "TODOS LOS DERECHOS RESERVADOS",

    # Inglés
    "LEGAL NOTICE",
    "DISCLAIMER",
    "LEGAL DISCLAIMER",
    "TERMS AND CONDITIONS",
    "ALL RIGHTS RESERVED",
    "CONFIDENTIAL",
    "PROPRIETARY NOTICE",
    "LEGAL WARNING",
    "COPYRIGHT NOTICE",
    "INTELLECTUAL PROPERTY",
    "LEGAL INFORMATION",
    "PRIVATE AND CONFIDENTIAL"
]

def process_pdf(pdf_file):
    """Extrae texto de un PDF ignorando secciones legales y disclaimers"""
    text = ""
    reader = PdfReader(pdf_file)
    print(f"Procesando PDF con {len(reader.pages)} páginas")
    
    for i, page in enumerate(reader.pages):
        try:
            print(f"\nProcesando página {i+1}")
            page_text = page.extract_text()
            
            # Ignorar páginas que comienzan con términos legales
            if any(page_text.strip().upper().startswith(term) for term in IGNORE_TERMS):
                print(f"Página {i+1}: Contenido legal detectado - ignorando")
                continue
                
            if page_text.strip():
                lines = page_text.split('\n')
                processed_lines = []
                
                for line in lines:
                    # Ignorar líneas que contienen términos legales
                    if any(term in line.upper() for term in IGNORE_TERMS):
                        break
                    
                    processed_line = ' '.join(word for word in line.split(' ') if word)
                    if '$' in line:  # Línea con valores monetarios
                        processed_line = line.replace('  ', ' <COL> ')
                    processed_lines.append(processed_line)
                
                page_text = '\n'.join(processed_lines)
                
                text += f"\n\n=== Página {i+1} ===\n\n"
                text += page_text
                print(f"Página {i+1}: {len(page_text)} caracteres extraídos")
            else:
                print(f"Página {i+1}: Sin texto extraíble")
                
        except Exception as e:
            print(f"Error al procesar página {i+1}: {str(e)}")
            continue
    
    print(f"\nTotal de texto extraído: {len(text)} caracteres")
    return text


def create_chunks(text):
    """Divide el texto en chunks respetando la estructura de tablas"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=200,
        length_function=len,
        # Separadores modificados para respetar estructura tabular
        separators=["\n\n=== Página", "\n\n", "\n", "<COL>", " ", ""]
    )
    
    # Pre-procesar el texto para identificar secciones de tablas
    sections = []
    current_section = []
    lines = text.split('\n')
    
    for line in lines:
        if line.startswith('===') or not line.strip():  # Nueva sección o línea vacía
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
        current_section.append(line)
    
    if current_section:
        sections.append('\n'.join(current_section))
    
    # Procesar cada sección por separado
    all_chunks = []
    for section in sections:
        if '<COL>' in section:  # Es una tabla
            # Mantener la tabla completa en un solo chunk
            all_chunks.append(section)
        else:
            # Dividir texto normal
            chunks = text_splitter.split_text(section)
            all_chunks.extend(chunks)
    
    print(f"Texto dividido en {len(all_chunks)} chunks")
    return all_chunks


# Inicializar embeddings
embeddings = HuggingFaceEmbeddings(
    #model_name="sentence-transformers/all-MiniLM-L6-v2",
    #model_name="sentence-transformers/all-mpnet-base-v2",
    model_name="sentence-transformers/LaBSE", #Embeddings en espanol
    #model_name="jinaai/jina-embeddings-v2-base-es", #Embeddings en espanol 
    model_kwargs={'device': 'cpu'}
)


# Inicializar cliente Chroma
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'RAG Server'
    })




@app.route('/process_documents', methods=['POST'])
def process_documents():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    # Obtener session_id de los headers
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        return jsonify({'error': 'No session ID provided'}), 400
    
    # Crear nombre de colección único para esta sesión y carga
    timestamp = int(time.time())
    collection_name = f"{BASE_COLLECTION_NAME}_{session_id}_{timestamp}"
    
    print(f"\nProcesando documentos para sesión {session_id}")
    print(f"Colección: {collection_name}")
    
    try:
        files = request.files.getlist('files')
        all_chunks = []
        processed_files = []
        
        for file in files:
            if file.filename.endswith('.pdf'):
                processed_files.append(file.filename)
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    file.save(tmp_file.name)
                    
                    # Pre-procesar para detectar si es un documento financiero
                    sample_text = process_pdf(tmp_file.name)
                    is_financial = any(term in sample_text.lower() for term in [
                        'balance sheet', 'income statement', 'cash flow',
                        'consolidated', 'financial statements'
                    ])
                    
                    if is_financial:
                        print("Detectado documento financiero - aplicando procesamiento especial")
                        text = process_financial_pdf(tmp_file.name)
                    else:
                        text = process_pdf(tmp_file.name)
                    
                    chunks = create_chunks(text)
                    all_chunks.extend(chunks)
                    
                os.unlink(tmp_file.name)
        
        if not all_chunks:
            return jsonify({'error': 'No valid text extracted from PDFs'}), 400
        
        print(f"\nCreando vector store con {len(all_chunks)} chunks...")
        
        # Crear nuevo vector store con metadata
        vector_store = Chroma.from_texts(
            texts=all_chunks,
            embedding=embeddings,
            client=chroma_client,
            collection_name=collection_name,
            collection_metadata={
                'created_at': timestamp,
                'session_id': session_id,
                'document_count': len(processed_files)
            }
        )

        # Guardar referencia de la colección actual para este usuario
        redis_client.set(f"current_collection_{session_id}", collection_name)
        
        print(f"Vector store creado exitosamente para sesión {session_id}")
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(processed_files)} documents with {len(all_chunks)} chunks',
            'processed_files': processed_files,
            'chunks_created': len(all_chunks),
            'session_id': session_id,
            'collection_name': collection_name
        })

    except Exception as e:
        print(f"Error en el procesamiento: {str(e)}")
        return jsonify({'error': str(e)}), 500



def process_financial_pdf(pdf_file):
    """Procesamiento especializado para documentos financieros"""
    text = ""
    reader = PdfReader(pdf_file)
    
    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text()
            if page_text.strip():
                # Detectar y preservar estructura de tabla
                lines = page_text.split('\n')
                table_lines = []
                
                for line in lines:
                    # Detectar líneas de tabla financiera
                    if any(char in line for char in ['$', '(', ')', '%']) or \
                       any(word.replace(',', '').replace('.', '').isdigit() for word in line.split()):
                        # Preservar espaciado y alineación
                        line = f"<TABLE>{line}</TABLE>"
                    table_lines.append(line)
                
                processed_text = '\n'.join(table_lines)
                text += f"\n\n=== Página {i+1} ===\n\n"
                text += processed_text
                
        except Exception as e:
            print(f"Error en página {i+1}: {str(e)}")
            
    return text


@app.route('/ask', methods=['POST'])
def ask():
    try:
        # Obtener session_id
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
        
        # Obtener la colección actual del usuario
        collection_name = redis_client.get(f"current_collection_{session_id}")
        if not collection_name:
            return jsonify({'error': 'No documents have been processed for this session'}), 400
            
        collection_name = collection_name.decode('utf-8')

        # Verificar si existe la colección
        if collection_name not in [col.name for col in chroma_client.list_collections()]:
            return jsonify({'error': 'No documents have been processed for this session'}), 400

        vector_store = Chroma(
                            client=chroma_client,
                            embedding_function=embeddings,
                            collection_name=collection_name
                            )
        
    except Exception as e:
        print(f"Error al cargar vector store: {str(e)}")
        return jsonify({'error': 'No documents have been processed yet'}), 400
    
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400
    
    question = data['question']
    print(f"\nProcesando pregunta: {question}")
    
    try:
        # Recuperar contexto relevante
        docs = vector_store.similarity_search(question, k=40)
        print(f"Documentos recuperados: {len(docs)}")
        
        # Filtrar contenido no relevante
        filtered_docs = []
        for doc in docs:
            content = doc.page_content
            if not any(term in content.lower() for term in [
                "aviso legal", "disclaimer", "derechos reservados"
            ]):
                filtered_docs.append(content)
                print(f"\nContexto recuperado ({len(content)} caracteres):")
                print(content[:200] + "...")
        
        if not filtered_docs:
            return jsonify({
                'response': 'No se encontró información relevante para responder la pregunta.',
                'context_used': False
            })
        
        # Unir contexto
        context = "\n\n".join(filtered_docs)
        if len(context) > 4500:
            context = context[:4500] + "..."
        
        print(f"\nLongitud del contexto final: {len(context)} caracteres")
        
        # Crear prompt
        prompt = f"""Actúa como un analista financiero experto analizando documentos corporativos y de mercado.

        CONTEXTO:
        {context}

        PREGUNTA: {question}

        INSTRUCCIONES:
        1. Usa solo la información del contexto
        2. Si falta información, indícalo
        3. Proporciona una respuesta estructurada, concisa y profesional
        4. Cita el contexto cuando sea relevante
        5. Mantén un tono objetivo y claro, evitando inferencias no soportadas por el contexto.

        RESPUESTA:"""

        print("\nEnviando tarea a Celery...")
        
        try:
            # Enviar tarea a Celery
            task = celery_app.send_task(
                'rag_celery_worker.process_inference',
                args=[
                    prompt,
                    512,  # max_tokens
                    0.2,   # temperature
                    session_id  # Agregamos el session_id como user_id
                ]
            )
            
            # Esperar resultado con timeout
            result = task.get(timeout=600)
            
            print(f"\nRespuesta recibida de Celery: {result[:200]}...")
            
            # Verificar si el resultado es un diccionario con error
            if isinstance(result, dict) and 'error' in result:
                raise Exception(result['error'])
            
            # Asegurarse de que result sea string
            if not isinstance(result, str):
                raise Exception(f"Tipo de respuesta inesperado: {type(result)}")
            
            return jsonify({
                'response': result,
                'context_used': True
            })

        except celery.exceptions.TimeoutError:
            print("Timeout en el procesamiento de la tarea")
            return jsonify({
                'error': 'El procesamiento de la tarea tardó demasiado',
                'detail': 'Timeout después de 600 segundos'
            }), 504
            
        except Exception as e:
            print(f"Error en el procesamiento de la tarea: {str(e)}")
            return jsonify({
                'error': f'Error en el procesamiento: {str(e)}',
                'detail': traceback.format_exc()
            }), 500

    except Exception as e:
        print(f"Error general en ask: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'detail': traceback.format_exc()
        }), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)