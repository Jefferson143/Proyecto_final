from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "¡KeyFeedback está en marcha!"

if __name__ == "__main__":
    app.run(debug=True)
