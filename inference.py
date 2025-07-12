from flask import Flask, request, jsonify
from rag_celery_worker import process_inference  # Import directo a la tarea
import traceback

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model': "qwen2.5:latest"  # actualizado si ya usás Qwen2.5
    })


@app.route('/ticker_analysis', methods=['POST'])
def ticker_analysis():
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({'error': 'No prompt provided'}), 400

        prompt = data['prompt']
        max_tokens = data.get('max_tokens', 512)
        temperature = data.get('temperature', 0.5)
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'No user_id provided'}), 400

        print(f"📥 Recibido prompt de {len(prompt)} caracteres para usuario {user_id}")

        task = process_inference.delay(prompt, max_tokens, temperature, user_id)

        # Esperamos la respuesta del modelo con un timeout extendido (10 minutos)
        result = task.wait(timeout=600, propagate=False)

        if task.failed():
            print(f"❌ Tarea fallida para usuario {user_id}")
            return jsonify({
                'error': 'Tarea fallida en Celery',
                'detail': str(task.result)
            }), 500

        if isinstance(result, dict) and 'error' in result:
            print(f"⚠️ Error en resultado para usuario {user_id}: {result['error']}")
            return jsonify({'error': result['error']}), 500

        print(f"✅ Respuesta generada para usuario {user_id}: {len(result)} caracteres")
        return jsonify({'response': result})

    except Exception as e:
        print(f"💥 Error general para usuario {user_id}: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Error interno del servidor',
            'detail': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)



# from flask import Flask, request, jsonify
# from rag_celery_config import celery_app
# import traceback

# app = Flask(__name__)



# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({
#         'status': 'healthy',
#         'model': "BafS/gemma-2-2b-it-Q4_K_M-GGUF"
#     })


# @app.route('/ticker_analysis', methods=['POST'])
# def ticker_analysis():
#     try:
#         data = request.json
#         if not data or 'prompt' not in data:
#             return jsonify({'error': 'No prompt provided'}), 400

#         prompt = data['prompt']
#         max_tokens = data.get('max_tokens', 512)
#         temperature = data.get('temperature', 0.2)
#         user_id = data.get('user_id')  # Obtenemos el user_id del request

#         if not user_id:
#             return jsonify({'error': 'No user_id provided'}), 400

#         print(f"Recibido prompt de {len(prompt)} caracteres para usuario {user_id}")

#         try:
#             task = celery_app.send_task(
#                 'rag_celery_worker.process_inference',
#                 args=[prompt, max_tokens, temperature, user_id]  # Agregamos user_id a los argumentos
#             )
            
#             result = task.get(timeout=600)
            
#             if isinstance(result, dict) and 'error' in result:
#                 raise Exception(result['error'])
                
#             print(f"Respuesta generada: {len(result)} caracteres para usuario {user_id}")
#             return jsonify({'response': result})

#         except Exception as e:
#             print(f"Error en la generación para usuario {user_id}: {str(e)}")
#             print(f"Traceback: {traceback.format_exc()}")
#             return jsonify({
#                 'error': 'Error en la generación de texto',
#                 'detail': str(e)
#             }), 500

#     except Exception as e:
#         print(f"Error general: {str(e)}")
#         print(f"Traceback: {traceback.format_exc()}")
#         return jsonify({
#             'error': 'Error interno del servidor',
#             'detail': str(e)
#         }), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, debug=True)