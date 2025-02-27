from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return "Hello from Python Flask on Vercel"

if __name__ == "__main__":
    # Apenas para teste local, se quiser
    app.run(debug=True, port=3000)
