from .. import db
from datetime import datetime, date
#from ..history.models import ProfileSectionResponse
#from .models import Profile, ProfileSection

# Клиники
class Clinic(db.Model):
    __tablename__ = 'Clinic'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100))

    #def __init__(self, description):
    #    self.description = description

    def __repr__(self):
        return f'Клиника {self.description}'

    @staticmethod
    def insert_clinic():
        clinic = Clinic.query.get(1)
        if clinic is None:
            clinic = Clinic('Клинический центр Первого МГМУ им. И.М. Сеченова')
            db.session.add(clinic)
            db.session.commit()

# Группы исследования
class ResearchGroup(db.Model):
    __tablename__ = 'ResearchGroup'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'))

# Причины исключения из исследования
class Reason(db.Model):
    __tablename__ = 'Reason'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(300), unique=True)

# Диагнозы
class DiagnoseItem(db.Model):
    __tablename__ = 'DiagnoseItem'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=True)
    mkb10 = db.Column(db.String(20), unique=False)
    type = db.Column(db.String(30), unique=False, index = True)


# Врачи
class Doctor(db.Model):
    __tablename__ = 'Doctor'
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(100), unique=False)
    second_name = db.Column(db.String(100), unique=False)
    fio = db.Column(db.String(100), unique=False)

# Протезы
class Prosthesis(db.Model):
    __tablename__ = 'Prosthesis'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    firm = db.Column(db.String(100), unique=False)
    type = db.Column(db.String(100), unique=False)
    model = db.Column(db.String(20), unique=False)

# Компоненты протезов
class ProsthesisComponent(db.Model):
    __tablename__ = 'ProsthesisComponent'
    id = db.Column(db.Integer(), primary_key=True)
    model = db.Column(db.String(20))
    component = db.Column(db.String(100))
    value = db.Column(db.String(10))

# Осложнения
class Complication(db.Model):
    __tablename__ = 'Complication'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    type = db.Column(db.String(100), unique=False, index = True)

# Этапы операций
class OperationStep(db.Model):
    __tablename__ = 'OperationStep'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    order = db.Column(db.Integer(), unique=True)

# Наблюдения
class Event(db.Model):
    __tablename__ = 'Event'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    type = db.Column(db.String(100), unique=False, index = True)

# Группы Показателей
class IndicatorGroup(db.Model):
    __tablename__ = 'IndicatorGroup'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    indicators = db.relationship('Indicator', backref='group', lazy='dynamic')

# Показатели
class Indicator(db.Model):
    __tablename__ = 'Indicator'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(300), unique=False)
    is_calculated = db.Column(db.Boolean)
    group_id = db.Column(db.Integer(), db.ForeignKey('IndicatorGroup.id'), index = True)
    unit = db.Column(db.String(20), unique=False)
    type = db.Column(db.String(20), unique=False)
    def_values = db.relationship('IndicatorDef', backref='indicator')
    norm_values = db.relationship('IndicatorNorm', backref='indicator')


# Допустимые значения показателей
class IndicatorDef(db.Model):
    __tablename__='IndicatorDef'
    id=db.Column(db.Integer(), primary_key=True)
    indicator_id = db.Column(db.Integer(), db.ForeignKey('Indicator.id'), index = True)
    text_value = db.Column(db.String(100), unique=False)
    num_value = db.Column(db.Numeric())
    id_value =db.Column(db.Integer(), unique=False)

# Нормативные значения показателей
class IndicatorNorm(db.Model):
    __tablename__='IndicatorNorm'
    id=db.Column(db.Integer(), primary_key=True)
    indicator_id = db.Column(db.Integer(), db.ForeignKey('Indicator.id'), index = True)
    nvalue_from = db.Column(db.Numeric())
    nvalue_to = db.Column(db.Numeric())

# Анкеты
class Profile(db.Model):
    __tablename__ = 'Profile'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=False)
    items = db.relationship('ProfileItem', backref='profile', lazy='dynamic')

# Результаты заполнения анкет
    @staticmethod
    def get_profiles_results(history_event, **kwargs):
        # Если передан список с номерами анкет, то выбираем только их
        profile_list = kwargs.get('profile_list',None)

        items = []
        item = {}
        if profile_list is None:
            # Выбор всех анкет
            profile_sections = ProfileSection.query.order_by(ProfileSection.profile_id, ProfileSection.id).all()
        else:
            # Выбор только анкет из списка
            profile_sections = ProfileSection.query.filter(ProfileSection.profile_id.in_(profile_list)).order_by(ProfileSection.profile_id, ProfileSection.id).all()
            print(profile_sections)

        if profile_sections is None:
            # Справочник разделов анкет пустой
            return(items)

        # первая анкета
        current_profile = Profile.query.get(profile_sections[0].profile_id)
        prev_res = ''
        item = {}
        for section in profile_sections:

            if current_profile.id == 999:
                # это пустая анкета
                continue

            if section.profile_id != current_profile.id:
                item['result'] = prev_res
                items.append(item)
                current_profile = Profile.query.get(section.profile_id)
                prev_res = ''
                item = {}

            # Собрать резултаты анкеты
            item['profile_id'] = current_profile.id
            item['profile_section_id'] = section.id
            item['description'] = current_profile.description
            # Получить ответы по разделам анкет
            section_response = ProfileSectionResponse.query.filter_by(profile_id=current_profile.id, profile_section_id=section.id, history_event_id=history_event.id).first()
            if section_response:
                # Есть ответ
                if section_response.response_value == 0:
                    prev_res = prev_res + ' ' + section.profile_section + ': ' + str(section_response.response_str)
                else:
                    prev_res = prev_res + ' ' + section.profile_section + ': ' + str(section_response.response_value)

                item['date'] = section_response.date_value
            else:
                # Ответа нет
                prev_res = prev_res + ' ' + section.profile_section + ': '
                item['date'] = date(1999,1,1)
                item['empty'] = 1

        item['result'] = prev_res
        items.append(item)


        return(items)


# Вопросы анкет
class ProfileItem(db.Model):
    __tablename__ = 'ProfileItem'
    id = db.Column(db.Integer(), primary_key=True)
    profile_id= db.Column(db.Integer(), db.ForeignKey('Profile.id'), index = True)
    description = db.Column(db.String(100), unique=False)
    item_group = db.Column(db.String(100))
    answers = db.relationship('ProfileAnswer', backref='item', lazy='dynamic')

# Возможные Ответы на вопросы анкет
class ProfileAnswer(db.Model):
    __tablename__ = 'ProfileAnswer'
    id = db.Column(db.Integer(), primary_key=True)
    profile_id= db.Column(db.Integer(), db.ForeignKey('Profile.id'), index = True)
    profile_item_id= db.Column(db.Integer(), db.ForeignKey('ProfileItem.id'))
    response = db.Column(db.String(100), unique=False)
    response_value = db.Column(db.Numeric())

# Разделы анкет
class ProfileSection(db.Model):
    __tablename__ = 'ProfileSection'
    id = db.Column(db.Integer(), primary_key=True)
    profile_id= db.Column(db.Integer(), db.ForeignKey('Profile.id'), index = True)
    profile_section= db.Column(db.String(100), unique=False)
    description = db.Column(db.String(100), unique=False)

# Возможные итоги разделов анкет
class ProfileSectionAnswer(db.Model):
    __tablename__ = 'ProfileSectionAnswer'
    id = db.Column(db.Integer(), primary_key=True)
    profile_id= db.Column(db.Integer(), db.ForeignKey('Profile.id'), index = True)
    profile_section_id= db.Column(db.Integer(), db.ForeignKey('ProfileSection.id'))
    response_str = db.Column(db.String(100), unique=False)
    response_num_value_from = db.Column(db.Numeric())
    response_num_value_to = db.Column(db.Numeric())


# Фактические результаты разделов анкет (агрегированно по всем вопросам)
class ProfileSectionResponse(db.Model):
    __tablename__='ProfileSectionResponse'
    id = db.Column(db.Integer(), primary_key=True)
    date_value = db.Column(db.Date())
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    history_event_id = db.Column(db.Integer(), db.ForeignKey('HistoryEvent.id'))
    profile_id = db.Column(db.Integer(), db.ForeignKey('Profile.id'), index = True)
    profile_section_id= db.Column(db.Integer(), db.ForeignKey('ProfileSection.id'))
    response_str = db.Column(db.String(100), unique=False)
    response_value = db.Column(db.Numeric())
