from flask import Flask, request, jsonify
from models_celery_config import celery_app

app = Flask(__name__)
PORT = 5003

@app.route('/predict', methods=['GET'])
def predict():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker no proporcionado"}), 400

    try:
        # Enviar tarea a Celery
        task = celery_app.send_task(
            'models_celery_worker.process_prediction',
            args=[ticker]
        )
        
        # Esperar resultado
        result = task.get(timeout=300)  # 5 minutos timeout
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 400
            
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=PORT, debug=True)