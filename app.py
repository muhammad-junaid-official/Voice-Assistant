from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Voice Assistant API</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>Voice Assistant Web API</h1>
            <p>Created by <strong>Muhammad Junaid FullStack Developer</strong></p>
            <p>This is the web endpoint for the Voice Assistant project.</p>
        </body>
    </html>
    """

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "active", "owner": "Muhammad Junaid FullStack Developer"})

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
