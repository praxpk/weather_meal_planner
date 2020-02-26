from flask import Flask
import application

app = Flask(__name__)
app.add_url_rule('/', view_func=application.index)
app.add_url_rule('/temperature', methods=['POST'], view_func=application.temperature)
if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(debug=True)