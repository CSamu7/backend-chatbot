
from flask import Flask, request, jsonify
import pickle
import numpy as np
from pathlib import Path

app = Flask(__name__)

MODEL_PATH = Path("/app/models/chatbot_model.pkl")
model = None

try:
    if MODEL_PATH.exists():
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("✅ Modelo cargado exitosamente")
except Exception as e:
    print(f"⚠️  Error cargando modelo: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Predecir intención del usuario"""
    try:
        data = request.get_json()
        user_input = data.get('text', '')
        
        if not model:
            return jsonify({"error": "Modelo no cargado"}), 503
        
        prediction = model.predict([user_input])
        confidence = model.predict_proba([user_input]).max()
        
        return jsonify({
            "intent": prediction[0],
            "confidence": float(confidence),
            "text": user_input
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/train', methods=['POST'])
def train():
    """Endpoint para reentrenar el modelo"""
    try:
        data = request.get_json()
        
        return jsonify({"status": "training_started"}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)