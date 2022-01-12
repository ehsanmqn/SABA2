
from flask_migrate import Migrate
from os import environ
from sys import exit
from flask_restful import Api
from config import config_dict
from app import create_app, create_celery, db
from app.EmotionRecognition import resources
from flask import render_template, redirect, url_for, request


get_config_mode = environ.get('APPSEED_CONFIG_MODE', 'Debug')

try:
    config_mode = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid APPSEED_CONFIG_MODE environment variable entry.')


app = create_app(config_mode)
celery = create_celery(app)
api = Api(app)
Migrate(app, db)

@app.route('/api/predict/model3', methods=['GET'])
def predict_api():
    filename = request.args.get('file')
    callcenter = request.args.get('cal')

    predict.delay(filename=filename, callcenter=callcenter)

    return {'request': 'success', 'message': 'File inserted into process queue'}

# 
# Analysis function
# Given filename and path, this functions processes the audio file to determine which emotion class
# it blonged to
# filename: filename
# callcenter: file path
# 
@celery.task(name='run.predict')
def predict(filename=None, callcenter=None):
    return resources.EmotionAnalysis().predict(filename=filename)

# Set up api
# api.add_resource(resources.PredictWithModel1ForShafatel, '/api/predict/model3')

if __name__ == "__main__":
    app.run()
