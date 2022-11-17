from flask import Flask
app = Flask(__name__)

import os

@app.route("/")
def home():
    return "Hello!"
    
if __name__=="__main__":
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)