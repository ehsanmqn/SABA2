from run import db
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from app.EmotionRecognition.process import softmax, parse_phone_number

class AnalyticsModel(db.Model):
    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(250), unique = True, nullable = False)
    time = db.Column(db.DateTime(250), nullable = False)
    caller = db.Column(db.String(20))
    callee = db.Column(db.String(20))
    location = db.Column(db.String(120), nullable = False)
    operator = db.Column(db.String(10), nullable = True)
    angry = db.Column(db.Float, nullable = False)
    happy = db.Column(db.Float, nullable = False)
    neutral = db.Column(db.Float, nullable = False)
    sad = db.Column(db.Float, nullable = False)
    fear = db.Column(db.Float, nullable = False)
    emotion = db.Column(db.String(1), nullable=True)
    type = db.Column(db.String(10), nullable=True)
    callcenter = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    can_create = False
    can_edit = False
    can_delete = False

    def save_to_db(self):
        db.session.add(self)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            print(str(e.__dict__['orig']))


    @classmethod
    def update_row_by_filename(cls, filename, angry, happy, neutral, sad, fear):
        row = cls.query.filter_by(filename = filename).first()
        row.angry = angry
        row.happy = happy
        row.neutral = neutral
        row.fear = fear
        row.sad = sad
        db.session.commit()

    @classmethod
    def find_by_caller_id(cls, extension):
        return cls.query.filter_by(caller = extension).first()

    @classmethod
    def find_by_callee_id(cls, extension):
        return cls.query.filter_by(callee = extension).first()

    @classmethod
    def find_by_filename(cls, filename):
        return cls.query.filter_by(filename = filename).first()

    @classmethod
    def alter_table(cls):
        max = AnalyticsModel.query.count()
        for row in range(2, max):

            query = cls.query.filter_by(id=row).first()
            print(query.id)

            parsed_data = parse_phone_number(query.caller)
            query.type = parsed_data['type']
            query.location = parsed_data['region']
            query.operator = parsed_data['operator']

            # query.emotion = softmax([query.angry, query.happy, query.neutral, query.sad, query.fear])
            db.session.commit()

        return

    @classmethod
    def count_all(cls):
        return AnalyticsModel.query.count()

    @classmethod
    def get_analytics_table_data_by_time(cls, start_date, end_date, page):
        def to_json(x):
            return {
                'filename': x.filename,
                'caller': x.caller,
                'callee': x.callee,
                'time': x.time,
                'angry': x.angry,
                'happy': x.happy,
                'neutral': x.neutral,
                'sad': x.sad,
                'fear': x.fear,
                'emotion': x.emotion,
                'location': x.location,
                'type': x.type,
                'operator': x.operator
            }

        return list(map(lambda x: to_json(x),
                        AnalyticsModel.query.filter(AnalyticsModel.time > start_date)
                        .filter(AnalyticsModel.time < end_date)[(100 * (page - 1) + 1):(100 * page)]))


    @classmethod
    def prepare_dashboard_analytics(cls):

        # AnalyticsModel.alter_table()

        regions = ['البرز', 'قم', 'مرکزی', 'زنجان',
                         'سمنان', 'همدان', 'قزوین', 'اصفهان',
                         'آذربایجان غربی', 'مازندران', 'کهگیلویه و بویراحمد',
                         'کرمانشاه', 'خراسان رضوی', 'اردبیل', 'گلستان',
                         'آذربایجان شرقی', 'سیستان و بلوچستان', 'کردستان',
                         'فارس', 'لرستان', 'کرمان', 'خراسان جنوبی', 'گیلان',
                         'بوشهر', 'هرمزگان', 'خوزستان', 'چهار محال و بختیاری',
                         'خراسان شمالی', 'یزد', 'ایلام', 'تهران']

        total_calls = AnalyticsModel.query.count()

        start = datetime.now()
        end = start - timedelta(7)

        Q_week = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)
        week_calls_number = Q_week.count()
        if week_calls_number == 0:
            week_calls_number = 1
        avg_calls_per_minute = round(week_calls_number / 10080) # 7 * 24 * 60 = 10080

        Q_angry = Q_week.filter_by(emotion='A')
        Q_happy = Q_week.filter_by(emotion='H')
        Q_neutral = Q_week.filter_by(emotion='N')
        Q_sad = Q_week.filter_by(emotion='S')
        Q_fear = Q_week.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        calls = []
        intervals = []

        for i in range(0, 7):
            end = start - timedelta(days=1)
            intervals.append(start.day)
            calls.append(Q_week.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        irancell = Q_week.filter_by(operator='Irancell').count()
        tci = Q_week.filter_by(operator='TCI')
        mci = Q_week.filter_by(operator='MCI').count()
        rightel = Q_week.filter_by(operator='RighTel').count()
        other = Q_week.count() - irancell - tci.count() - mci - rightel

        Q_fixed = tci
        states = {}
        for state in regions:
            states.update({state: Q_fixed.filter_by(location=state).count()})

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'calls': calls[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.count(),
            'happy': Q_happy.count(),
            'neutral': Q_neutral.count(),
            'sad': Q_sad.count(),
            'fear': Q_fear.count(),
            'week_calls_number': week_calls_number,
            'total_calls': total_calls,
            'avg_calls_per_minute': avg_calls_per_minute,
            'irancell': round(irancell / week_calls_number * 100, 2),
            'tci': round(tci.count() / week_calls_number * 100, 2),
            'mci': round(mci / week_calls_number * 100, 2),
            'rightel': round(rightel / week_calls_number * 100, 2),
            'other': round(other / week_calls_number * 100, 2),
            'states': states
        }

    @classmethod
    def prepare_pie_charts_emotions(cls):

        start = datetime.now()

        # Day analytics
        end = start - timedelta(1)
        Q_day = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)

        day_calls_number = Q_day.count()

        if day_calls_number == 0:
            day_calls_number = 1

        day_angry = Q_day.filter_by(emotion='A').count() / day_calls_number * 100
        day_happy = Q_day.filter_by(emotion='H').count() / day_calls_number * 100
        day_neutral = Q_day.filter_by(emotion='N').count() / day_calls_number * 100
        day_sad = Q_day.filter_by(emotion='S').count() / day_calls_number * 100
        day_fear = Q_day.filter_by(emotion='F').count() / day_calls_number * 100

        # Week analytics
        end = start - timedelta(7)
        Q_week = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)

        week_calls_number = Q_week.count()

        if week_calls_number == 0:
            week_calls_number = 1

        week_angry = Q_week.filter_by(emotion='A').count() / week_calls_number * 100
        week_happy = Q_week.filter_by(emotion='H').count() / week_calls_number * 100
        week_neutral = Q_week.filter_by(emotion='N').count() / week_calls_number * 100
        week_sad = Q_week.filter_by(emotion='S').count() / week_calls_number * 100
        week_fear = Q_week.filter_by(emotion='F').count() / week_calls_number * 100

        # Month analytics
        end = start - timedelta(30)
        Q_month = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)

        month_calls_number = Q_month.count()

        if month_calls_number == 0:
            month_calls_number = 1

        month_angry = Q_month.filter_by(emotion='A').count() / month_calls_number * 100
        month_happy = Q_month.filter_by(emotion='H').count() / month_calls_number * 100
        month_neutral = Q_month.filter_by(emotion='N').count() / month_calls_number * 100
        month_sad = Q_month.filter_by(emotion='S').count() / month_calls_number * 100
        month_fear = Q_month.filter_by(emotion='F').count() / month_calls_number * 100

        # Year analytics
        end = start - timedelta(364)
        Q_year = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)

        year_calls_number = Q_year.count()

        if year_calls_number == 0:
            year_calls_number = 1

        year_angry = Q_year.filter_by(emotion='A').count() / year_calls_number * 100
        year_happy = Q_year.filter_by(emotion='H').count() / year_calls_number * 100
        year_neutral = Q_year.filter_by(emotion='N').count() / year_calls_number * 100
        year_sad = Q_year.filter_by(emotion='S').count() / year_calls_number * 100
        year_fear = Q_year.filter_by(emotion='F').count() / year_calls_number * 100

        return {
            'day': {
                'angry': day_angry,
                'happy': day_happy,
                'neutral': day_neutral,
                'fear': day_fear,
                'sad': day_sad
            },
            'week': {
                'angry': week_angry,
                'happy': week_happy,
                'neutral': week_neutral,
                'fear': week_fear,
                'sad': week_sad
            },
            'month': {
                'angry': month_angry,
                'happy': month_happy,
                'neutral': month_neutral,
                'fear': month_fear,
                'sad': month_sad
            },
            'year': {
                'angry': year_angry,
                'happy': year_happy,
                'neutral': year_neutral,
                'fear': year_fear,
                'sad': year_sad
            },
        }

    @classmethod
    def prepare_day_analytics(cls):

        now = datetime.now()
        start = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour)
        end = start - timedelta(1)

        Q_day = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)

        day_calls_number = Q_day.count()

        if day_calls_number == 0:
            day_calls_number = 1

        Q_angry = Q_day.filter_by(emotion='A')
        Q_happy = Q_day.filter_by(emotion='H')
        Q_neutral = Q_day.filter_by(emotion='N')
        Q_sad = Q_day.filter_by(emotion='S')
        Q_fear = Q_day.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []

        for i in range(0, 24):
            end = start - timedelta(hours=1)
            intervals.append(start)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.count() / day_calls_number * 100,
            'happy': Q_happy.count() / day_calls_number * 100,
            'neutral': Q_neutral.count() / day_calls_number * 100,
            'sad': Q_sad.count() / day_calls_number * 100,
            'fear': Q_fear.count() / day_calls_number * 100,
            'day_calls_number': day_calls_number,
        }

    @classmethod
    def prepare_week_analytics(cls):

        now = datetime.now()
        start = datetime(year=now.year, month=now.month, day=now.day)
        end = start - timedelta(7)

        query = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)

        calls_number = query.count()

        if calls_number == 0:
            calls_number = 1

        Q_angry = query.filter_by(emotion='A')
        Q_happy = query.filter_by(emotion='H')
        Q_neutral = query.filter_by(emotion='N')
        Q_sad = query.filter_by(emotion='S')
        Q_fear = query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []

        for i in range(0, 7):
            end = start - timedelta(days=1)
            intervals.append(start)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.count() / calls_number * 100,
            'happy': Q_happy.count() / calls_number * 100,
            'neutral': Q_neutral.count() / calls_number * 100,
            'sad': Q_sad.count() / calls_number * 100,
            'fear': Q_fear.count() / calls_number * 100,
            'calls_number': calls_number,
        }

    @classmethod
    def prepare_month_analytics(cls):

        now = datetime.now()
        start = datetime(year=now.year, month=now.month, day=now.day)
        end = start - timedelta(30)

        query = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)

        calls_number = query.count()

        if calls_number == 0:
            calls_number = 1

        Q_angry = query.filter_by(emotion='A')
        Q_happy = query.filter_by(emotion='H')
        Q_neutral = query.filter_by(emotion='N')
        Q_sad = query.filter_by(emotion='S')
        Q_fear = query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []

        for i in range(0, 30):
            end = start - timedelta(days=1)
            intervals.append(start)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.count() / calls_number * 100,
            'happy': Q_happy.count() / calls_number * 100,
            'neutral': Q_neutral.count() / calls_number * 100,
            'sad': Q_sad.count() / calls_number * 100,
            'fear': Q_fear.count() / calls_number * 100,
            'calls_number': calls_number,
        }

    @classmethod
    def prepare_year_analytics(cls):

        now = datetime.now()
        start = datetime(year=now.year, month=now.month, day=now.day)
        end = start - timedelta(364)

        query = AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end)
        calls_number = query.count()

        Q_angry = query.filter_by(emotion='A')
        Q_happy = query.filter_by(emotion='H')
        Q_neutral = query.filter_by(emotion='N')
        Q_sad = query.filter_by(emotion='S')
        Q_fear = query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []

        for i in range(0, 12):
            end = start - timedelta(days=31)
            intervals.append(start)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.count() / calls_number * 100,
            'happy': Q_happy.count() / calls_number * 100,
            'neutral': Q_neutral.count() / calls_number * 100,
            'sad': Q_sad.count() / calls_number * 100,
            'fear': Q_fear.count() / calls_number * 100,
            'calls_number': calls_number,
        }

    @classmethod
    def prepare_emotions_page_data(cls, start_date=None, end_date=None):

        start = start_date
        end = end_date

        time_diff = end_date - start_date
        if (time_diff.days <= 1):
            range_max = end_date.hour + 1
            range_min = 0
            step = 'h'
            delta = timedelta(hours=1)
        elif (time_diff.days <= 7):
            range_max = 7
            range_min = 0
            step = 'd'
            delta = timedelta(days=1)
        elif (time_diff.days <= 30):
            range_max = 30
            range_min = 0
            step = 'd'
            delta = timedelta(days=1)
        elif (time_diff.days <= 254):
            range_max = 12
            range_min = 0
            step = 'm'
            delta = timedelta(days=31)


        query = AnalyticsModel.query.filter(AnalyticsModel.time > start).filter(AnalyticsModel.time < end)
        calls_number = query.count()
        if(calls_number == 0):
            calls_number = 1

        Q_angry = query.filter_by(emotion='A')
        Q_happy = query.filter_by(emotion='H')
        Q_neutral = query.filter_by(emotion='N')
        Q_sad = query.filter_by(emotion='S')
        Q_fear = query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []

        for i in range(range_min, range_max):
            end = start + delta
            # intervals.append(i)
            if(step == 'h'):
                intervals.append(start.hour)
            elif(step == 'd'):
                intervals.append(start.day)
            elif(step == 'm'):
                intervals.append(start.month)

            angries.append(Q_angry.filter(AnalyticsModel.time > start).filter(AnalyticsModel.time < end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time > start).filter(AnalyticsModel.time < end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time > start).filter(AnalyticsModel.time < end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time > start).filter(AnalyticsModel.time < end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time > start).filter(AnalyticsModel.time < end).count())

            start = end

        return {
            'angries': angries,
            'happies': happies,
            'sads': sads,
            'fears': fears,
            'neutrals': neutrals,
            'intervals': intervals,
            'angry': round(Q_angry.count() / calls_number * 100, 2),
            'happy': round(Q_happy.count() / calls_number * 100, 2),
            'neutral': round(Q_neutral.count() / calls_number * 100, 2),
            'sad': round(Q_sad.count() / calls_number * 100, 2),
            'fear': round(Q_fear.count() / calls_number * 100, 2),
            'angry_number': Q_angry.count(),
            'happy_number': Q_happy.count(),
            'neutral_number': Q_neutral.count(),
            'sad_number': Q_sad.count(),
            'fear_number': Q_fear.count(),
            'calls_number': calls_number,
        }

    @classmethod
    def get_day_emotions(cls):

        start = datetime.now()
        end = start - timedelta(1)

        Q_angry = AnalyticsModel.query.filter_by(emotion='A')
        Q_happy = AnalyticsModel.query.filter_by(emotion='H')
        Q_neutral = AnalyticsModel.query.filter_by(emotion='N')
        Q_sad = AnalyticsModel.query.filter_by(emotion='S')
        Q_fear = AnalyticsModel.query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []
        start = datetime.now()
        for i in range(0, 24):
            end = start - timedelta(hours=1)
            intervals.append(start.hour)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        start = datetime.now()
        end = start - timedelta(1)

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'happy': Q_happy.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'neutral': Q_neutral.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'sad': Q_sad.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'fear': Q_fear.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'count': AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
        }

    @classmethod
    def get_week_emotions(cls):


        Q_angry = AnalyticsModel.query.filter_by(emotion='A')
        Q_happy = AnalyticsModel.query.filter_by(emotion='H')
        Q_neutral = AnalyticsModel.query.filter_by(emotion='N')
        Q_sad = AnalyticsModel.query.filter_by(emotion='S')
        Q_fear = AnalyticsModel.query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []
        start = datetime.now()
        for i in range(0, 7):
            end = start - timedelta(days=1)
            intervals.append(start.day)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        start = datetime.now()
        end = start - timedelta(7)

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count(),
            'happy': Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count(),
            'neutral': Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count(),
            'sad': Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count(),
            'fear': Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count(),
            'count': AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
        }

    @classmethod
    def get_month_emotions(cls):
        Q_angry = AnalyticsModel.query.filter_by(emotion='A')
        Q_happy = AnalyticsModel.query.filter_by(emotion='H')
        Q_neutral = AnalyticsModel.query.filter_by(emotion='N')
        Q_sad = AnalyticsModel.query.filter_by(emotion='S')
        Q_fear = AnalyticsModel.query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []
        start = datetime.now()
        for i in range(0, 30):
            end = start - timedelta(days=1)
            intervals.append(start.day)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        start = datetime.now()
        end = start - timedelta(30)

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'happy': Q_happy.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'neutral': Q_neutral.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'sad': Q_sad.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'fear': Q_fear.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'count': AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
        }

    @classmethod
    def get_year_emotions(cls):
        Q_angry = AnalyticsModel.query.filter_by(emotion='A')
        Q_happy = AnalyticsModel.query.filter_by(emotion='H')
        Q_neutral = AnalyticsModel.query.filter_by(emotion='N')
        Q_sad = AnalyticsModel.query.filter_by(emotion='S')
        Q_fear = AnalyticsModel.query.filter_by(emotion='F')

        angries = []
        happies = []
        fears = []
        sads = []
        neutrals = []
        intervals = []
        start = datetime.now()
        for i in range(0, 12):
            end = start - timedelta(days=30)
            intervals.append(start.month)
            angries.append(Q_angry.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            happies.append(Q_happy.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            neutrals.append(Q_neutral.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            fears.append(Q_fear.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())
            sads.append(Q_sad.filter(AnalyticsModel.time < start).filter(AnalyticsModel.time > end).count())

            start = end

        start = datetime.now()
        end = start - timedelta(364)

        return {
            'angries': angries[::-1],
            'happies': happies[::-1],
            'sads': sads[::-1],
            'fears': fears[::-1],
            'neutrals': neutrals[::-1],
            'intervals': intervals[::-1],
            'angry': Q_angry.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'happy': Q_happy.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'neutral': Q_neutral.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'sad': Q_sad.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'fear': Q_fear.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
            'count': AnalyticsModel.query.filter(AnalyticsModel.time < start).filter(
                AnalyticsModel.time > end).count(),
        }

    @classmethod
    def get_last_week_calls_number(cls,):
        def to_jason(x, y):
            return {
                'day': str(x),
                'calls': y
            }

        day1 = datetime.now()
        day2 = day1 - timedelta(1)
        day3 = day2 - timedelta(1)
        day4 = day3 - timedelta(1)
        day5 = day4 - timedelta(1)
        day6 = day5 - timedelta(1)
        day7 = day6 - timedelta(1)
        day8 = day7 - timedelta(1)

        days = [day7.day, day6.day, day5.day, day4.day, day3.day, day2.day, day1.day]
        calls = []

        calls.append(AnalyticsModel.query.filter(AnalyticsModel.time < day7).filter(AnalyticsModel.time > day8).count())
        calls.append(AnalyticsModel.query.filter(AnalyticsModel.time < day6).filter(AnalyticsModel.time > day7).count())
        calls.append(AnalyticsModel.query.filter(AnalyticsModel.time < day5).filter(AnalyticsModel.time > day6).count())
        calls.append(AnalyticsModel.query.filter(AnalyticsModel.time < day4).filter(AnalyticsModel.time > day5).count())
        calls.append(AnalyticsModel.query.filter(AnalyticsModel.time < day3).filter(AnalyticsModel.time > day4).count())
        calls.append(AnalyticsModel.query.filter(AnalyticsModel.time < day2).filter(AnalyticsModel.time > day3).count())
        calls.append(AnalyticsModel.query.filter(AnalyticsModel.time < day1).filter(AnalyticsModel.time > day2).count())

        return {
            'days': days,
            'calls': calls,
        }

    @classmethod
    def get_last_week_callers_operators(cls, ):

        day1 = datetime.now()
        day7 = day1 - timedelta(7)

        last_week_query = AnalyticsModel.query.filter(AnalyticsModel.time < day1).filter(AnalyticsModel.time > day7)

        total = last_week_query.count()
        irancell = last_week_query.filter_by(operator = 'Irancell').count()
        tci = last_week_query.filter_by(operator='TCI').count()
        mci = last_week_query.filter_by(operator='MCI').count()
        rightel = last_week_query.filter_by(operator='RighTel').count()
        other = last_week_query.count() - irancell - tci - mci - rightel


        return {
            'irancell': round(irancell / total * 100, 2),
            'tci': round(tci / total * 100, 2),
            'mci': round(mci / total * 100, 2),
            'rightel': round(rightel / total * 100, 2),
            'other': round(other / total * 100, 2),
        }

    @classmethod
    def getAverageEmotions(cls, day=None, month=None, year=None):
        q1 = AnalyticsModel.query.with_entities(func.avg(AnalyticsModel.angry).label('angry'),
                                                func.avg(AnalyticsModel.happy).label('happy'),
                                                func.avg(AnalyticsModel.neutral).label('neutral'),
                                                func.avg(AnalyticsModel.sad).label('sad'),
                                                func.avg(AnalyticsModel.fear).label('fear'))

        return {'request': 'ok', 'result': list(map(lambda x: to_json(x), q1))}

    @classmethod
    def AverageEmotions(cls):
        def to_json(x):
            return {
                'angry': x.angry,
                'happy': x.happy,
                'neutral': x.neutral,
                'sad': x.sad,
                'fear': x.fear,
            }

        q1 = AnalyticsModel.query.with_entities(func.avg(AnalyticsModel.angry).label('angry'),
                                                func.avg(AnalyticsModel.happy).label('happy'),
                                                func.avg(AnalyticsModel.neutral).label('neutral'),
                                                func.avg(AnalyticsModel.sad).label('sad'),
                                                func.avg(AnalyticsModel.fear).label('fear'))

        return list(map(lambda x: to_json(x), q1))

    @classmethod
    def AverageEmotionsRounded(cls):
        def to_json(x):
            return {
                'angry': round(x.angry * 100),
                'happy': round(x.happy * 100),
                'neutral': round(x.neutral * 100),
                'sad': round(x.sad * 100),
                'fear': round(x.fear * 100),
            }

        q1 = AnalyticsModel.query.with_entities(func.avg(AnalyticsModel.angry).label('angry'),
                                                func.avg(AnalyticsModel.happy).label('happy'),
                                                func.avg(AnalyticsModel.neutral).label('neutral'),
                                                func.avg(AnalyticsModel.sad).label('sad'),
                                                func.avg(AnalyticsModel.fear).label('fear'))

        return list(map(lambda x: to_json(x), q1))

    @classmethod
    def AverageEmotions(cls):
        def to_json(x):
            return {
                'angry': x.angry,
                'happy': x.happy,
                'neutral': x.neutral,
                'sad': x.sad,
                'fear': x.fear,
            }

        q1 = AnalyticsModel.query.with_entities(func.avg(AnalyticsModel.angry).label('angry'),
                                                func.avg(AnalyticsModel.happy).label('happy'),
                                                func.avg(AnalyticsModel.neutral).label('neutral'),
                                                func.avg(AnalyticsModel.sad).label('sad'),
                                                func.avg(AnalyticsModel.fear).label('fear'))

        return list(map(lambda x: to_json(x), q1))


    @classmethod
    def DeleteAll(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'request': 'ok', 'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'request': 'failed', 'message': 'Something went wrong'}

    @classmethod
    def AnalyticsByCount(cls, count):
        def to_json(x):
            return {
                'filename': x.filename,
                'caller': x.caller,
                'callee': x.callee,
                # 'time': x.time,
                'uid': x.location,
                'angry': x.angry,
                'happy': x.happy,
                'neutral': x.neutral,
                'sad': x.sad,
                'fear': x.fear
            }

        return {'request': 'ok', 'result': list(map(lambda x: to_json(x), AnalyticsModel.query.order_by(AnalyticsModel.id.desc()).limit(count)))}

    @classmethod
    def AnalyticsByFilename(cls, filename):
        def to_json(x):
            return {
                'filename': x.filename,
                'caller': x.caller,
                'callee': x.callee,
                'time': x.time,
                'uid': x.location,
                'angry': x.angry,
                'happy': x.happy,
                'neutral': x.neutral,
                'sad': x.sad,
                'fear': x.fear
            }

        return {'request': 'ok', 'result': list(map(lambda x: to_json(x), AnalyticsModel.query.filter_by(filename = filename).all()))}