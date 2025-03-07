from flask import Flask, render_template

app = Flask(__name__,
            static_folder='../Presentacion/static',
            template_folder='../Presentacion/templates')

@app.route('/')
def home():
    # Renderiza el template Prueba1.html desde la carpeta "templates"
    return render_template('Prueba1.html')

if __name__ == '__main__':
    # Escucha en todas las IPs (0.0.0.0) y puerto 5000
    app.run(host='0.0.0.0', port=5000)
