"""
Mock ML Server - Simula un ML service que retorna HTML en vez de JSON.
Ejecutar ANTES de correr el test 502 en Postman.

Uso:
    pip install flask
    python mock_ml_server.py

El servidor escucha en http://localhost:8000 (mismo puerto que el ML real).
Detener con Ctrl+C y luego reiniciar el ML real: docker start ml-service
"""

from flask import Flask, Response

app = Flask(__name__)

@app.route('/analisis-energetico', methods=['POST'])
def analisis_energetico():
    """Retorna HTML en vez de JSON → el backend no puede parsear → retorna 502"""
    html_response = """
    <!DOCTYPE html>
    <html>
    <head><title>502 Bad Gateway</title></head>
    <body>
    <h1>502 Bad Gateway</h1>
    <p>nginx/1.18.0</p>
    </body>
    </html>
    """
    return Response(html_response, status=200, content_type='text/html')

@app.route('/health', methods=['GET'])
def health():
    """Retorna HTML en vez de JSON"""
    return Response('<html><body><h1>Service Unavailable</h1></body></html>',
                    status=200, content_type='text/html')

@app.route('/', methods=['GET'])
def root():
    """Retorna HTML en vez de JSON"""
    return Response('<html><body><h1>ML Service Mock</h1></body></html>',
                    status=200, content_type='text/html')

if __name__ == '__main__':
    print("=" * 60)
    print("MOCK ML SERVER - Simula respuesta no-JSON para test 502")
    print("=" * 60)
    print("Escuchando en http://localhost:8000")
    print("DETENER EL ML REAL PRIMERO: docker stop ml-service")
    print("Detener este mock: Ctrl+C")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000, debug=False)
