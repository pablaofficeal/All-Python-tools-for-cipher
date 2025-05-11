from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = '(-7d9]_-84H0]W+#t\^mW3}]?wn@0L/}'   

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    