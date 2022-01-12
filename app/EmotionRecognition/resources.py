from flask_restful import Resource, reqparse
from flask import jsonify
from flask import request
import os
import datetime

from app.EmotionRecognition.setting import APP_STATIC
from app.EmotionRecognition import process
from app.EmotionRecognition.models import AnalyticsModel
from app.EmotionRecognition import Vokaturi

Vokaturi.load("app/EmotionRecognition/emotion-lib-linux64.so")

class AllAnalytics(Resource):

    def get_analytics_table_data_by_time(self, start_date, end_date, page):
        return AnalyticsModel.get_analytics_table_data_by_time(start_date=start_date, end_date=end_date, page=page)

    def prepare_pie_charts_emotions(self):
        return AnalyticsModel.prepare_pie_charts_emotions()

    def prepare_emotions_page_data(self, start_date=None, end_date=None):
        return AnalyticsModel.prepare_emotions_page_data(start_date=start_date, end_date=end_date)


class TodayAnalytics(Resource):

    def prepare_day_analytics(self):
        return AnalyticsModel.prepare_day_analytics()


class LastWeekAnalytics(Resource):

    def prepare_dashboard_analytics(self):
        return AnalyticsModel.prepare_dashboard_analytics()

    def prepare_week_analytics(self):
        return AnalyticsModel.prepare_week_analytics()


class LastMonthAnalytics(Resource):

    def prepare_month_analytics(self):
        return AnalyticsModel.prepare_month_analytics()


class LastYearAnalytics(Resource):

    def prepare_year_analytics(self):
        return AnalyticsModel.prepare_year_analytics()


class EmotionAnalysis():
    def predict(self, filename, caller=None, callee=None):
        rec_dir = ""

        # Check for file existence
        if not os.path.isfile(os.path.join(rec_dir, filename)):
            # This line added because some files saved with .WAV extension

            if not os.path.isfile(os.path.join(rec_dir, filename)):
                return {'request': 'failed', 'message': 'File {} not found'.format(filename)}, 400

        result = process.model1GetResultForAVA(os.path.join(rec_dir, filename))

        try:
            emotions = result['result'][0]
        except:
            return {'request': 'failed', 'message': 'Unknown problem in emotion recognition'.format(filename)}, 400

        parsed_phone = process.parse_phone_number(caller)

        newAnalytics = AnalyticsModel(
            filename=filename,
            time=datetime.datetime.now(),
            caller=caller,
            callee=callee,
            angry=emotions['angry'],
            happy=emotions['happy'],
            neutral=emotions['neutral'],
            sad=emotions['sad'],
            fear=emotions['fear'],
            emotion=emotions['emotion'],
            type=parsed_phone['type'],
            location=parsed_phone['region'],
            operator=parsed_phone['operator'],
            callcenter=""
        )

        try:
            newAnalytics.save_to_db()
            return {'request': 'success', 'message': 'Added to database'}, 200
        except:
            return {'request': 'failed', 'message': 'Something went wrong'}, 400
