from flask import Flask
from apps.charts.routes import charts_blueprint  
from apps.API.routes import api_blueprint

app = Flask(__name__, static_folder = r'apps/static',template_folder=r'/Users/daanishhindustano/Documents/projects/fin/apps/templates')
app.register_blueprint(charts_blueprint)
app.register_blueprint(api_blueprint)

if __name__ == '__main__':
    app.run(debug=True)