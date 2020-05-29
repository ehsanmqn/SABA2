# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present Avin Technologies
"""
import dateparser
from flask import jsonify
from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
from datetime import datetime, timedelta

from app.EmotionRecognition.resources import AllAnalytics, LastWeekAnalytics, TodayAnalytics, \
    LastMonthAnalytics, LastYearAnalytics

@blueprint.route('/index')
@login_required
def index():
    
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    dashboard_data = LastWeekAnalytics().prepare_dashboard_analytics()

    return render_template('index.html',
                           dashboard_data=dashboard_data,
                           start_time = datetime.date(datetime.now() - timedelta(6)),
                           end_time = datetime.date(datetime.now()))


@blueprint.route('/emotions', methods=['GET', 'POST'])
@login_required
def emotions():
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    if 'start-date' in request.form:
        start_date = dateparser.parse(request.form['start-date'][0:24])
        end_date = dateparser.parse(request.form['end-date'][0:24])

        start_js = request.form['start-date']
        end_js = request.form['end-date']
    else:
        now = datetime.now()
        start_date = datetime(year=now.year, month=now.month, day=now.day)
        end_date = now

        start_js = '-'
        end_js = '_'

    analytic_data = AllAnalytics().prepare_emotions_page_data(start_date=start_date, end_date=end_date)

    return render_template('emotions.html',
                           analytic_data=analytic_data,
                           start_date=start_js,
                           end_date=end_js)

@blueprint.route('/emotions/all/piechart')
def picharts():

    pie_chart_data = AllAnalytics().prepare_pie_charts_emotions()

    return jsonify(pie_chart_data)

    return render_template('all-piechart.html',
                           pie_chart_data=pie_chart_data)

@blueprint.route('/emotions/day/linechart')
def day_linechart():

    day_data = TodayAnalytics().prepare_day_analytics()

    return jsonify(day_data)

    return render_template('day-linechart.html',
                           day_data=day_data)

@blueprint.route('/emotions/week/linechart')
def week_linechart():

    week_data = LastWeekAnalytics().prepare_week_analytics()

    return jsonify(week_data)

    return render_template('week-linechart.html',
                           week_data=week_data)

@blueprint.route('/emotions/month/linechart')
def month_linechart():

    month_data = LastMonthAnalytics().prepare_month_analytics()

    return jsonify(month_data)

    return render_template('month-linechart.html',
                           month_data=month_data)

@blueprint.route('/emotions/year/linechart')
def year_linechart():

    year_data = LastYearAnalytics().prepare_year_analytics()

    return jsonify(year_data)

    return render_template('year-linechart.html',
                           year_data=year_data)


@blueprint.route('/tables-data', methods=['GET', 'POST'])
@login_required
def data():
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    page = request.args.get('page')

    if 'start-date' in request.form:
        start_date = dateparser.parse(request.form['start-date'][0:24])
        end_date = dateparser.parse(request.form['end-date'][0:24])

        start_js = request.form['start-date']
        end_js = request.form['end-date']
    else:
        now = datetime.now()
        start_date = datetime(year=now.year, month=now.month, day=now.day)
        end_date = now

        start_js = '-'
        end_js = '_'

    call_data = AllAnalytics().get_analytics_table_data_by_time(start_date=start_date, end_date=end_date, page=1)

    return render_template('tables-data.html', call_data=call_data)


@blueprint.route('/<template>')
def route_template(template):

    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    try:

        return render_template(template + '.html')

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500
