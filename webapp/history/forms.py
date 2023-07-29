from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField,\
                    RadioField, DecimalField, FieldList, FormField, IntegerField,\
                    TextField
from wtforms import ValidationError
from wtforms.fields.html5 import DateField, DateTimeField, TimeField
from wtforms.fields import TextField
from wtforms.validators import ValidationError, DataRequired, Optional, Email, EqualTo, Length, Regexp, NumberRange
#from .models import History
from ..main.models import Clinic, ResearchGroup, Reason, DiagnoseItem, Doctor, Event, Prosthesis, IndicatorDef,\
                            Complication


# -- Форма фильтрации историй болезни
class HistoryFilterForm(FlaskForm):
    hist_number_filter = StringField('Номер истории болезни', validators=[Optional()])
    snils_filter = StringField('СНИЛС пациента', validators=[Optional()])
    clinic_filter = SelectField('Клиника', coerce = int, validators=[DataRequired()])
    group_filter = SelectField('Группа исследования', coerce = int, validators=[Optional()])
    submit_filter = SubmitField('Фильтр')


    def __init__(self, *args, **kwargs):
        super(HistoryFilterForm, self).__init__(*args, **kwargs)
        self.clinic_filter.choices=[(clinic.id, clinic.description)
                              for clinic in Clinic.query.order_by(Clinic.id).all()]
        self.group_filter.choices=[(group.id, group.description)
                              for group in ResearchGroup.query.order_by(ResearchGroup.id).all()]
        self.group_filter.choices.append((0, ''))

# -- Форма историй болезни
class HistoryMainForm(FlaskForm):
    hist_number = StringField('Номер истории болезни', validators=[DataRequired()])
    date_in = DateField('Дата открытия', validators=[DataRequired()])
    clinic = SelectField('Клиника', coerce = int, validators=[DataRequired()])
    snils = StringField('СНИЛС') #, Regexp('[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}')])
    birthdate = DateField('Дата рождения', validators=[DataRequired()])
    sex = SelectField('Пол', coerce = str, validators=[DataRequired()])
    research_group = SelectField('Группа исследования', coerce = int, validators=[DataRequired()])
    doctor_researcher = SelectField('Врач-исследователь', coerce = int, validators=[DataRequired()])
    date_research_in = DateField('Дата включения в исследование',validators=[Optional()])
    date_research_out = DateField('Дата исключения из исследования',validators=[Optional()])
    reason = SelectField('Причина исключения из исследования', coerce = int, validators=[Optional()])
    # Основной диагноз будет здесь, так как при сохранении истории болезни нужно знать сторону поражения  
    diagnos = SelectField('Диагноз', coerce = int, validators=[DataRequired()])
    side_damage = SelectField('Сторона поражения', coerce = str, validators=[DataRequired()])
    date_created = DateField('Дата установления', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(HistoryMainForm, self).__init__(*args, **kwargs)
        self.clinic.choices=[(clinic.id, clinic.description)
                              for clinic in Clinic.query.order_by(Clinic.id).all()]
        self.research_group.choices=[(rg.id, rg.description)
                              for rg  in ResearchGroup.query.order_by(ResearchGroup.id).all()]
        self.reason.choices=[(r.id, r.description)
                              for r  in Reason.query.order_by(Reason.id).all()]
        self.sex.choices=[('1','Male'),('2','Female')]
        self.doctor_researcher.choices=[(doctor.id, doctor.fio)
                              for doctor in Doctor.query.order_by(Doctor.fio).all()]
        self.diagnos.choices=[(diagnos.id, diagnos.description)
                              for diagnos in DiagnoseItem.query.filter(DiagnoseItem.type=='Основной').order_by(DiagnoseItem.id).all()]
        self.side_damage.choices=[('Левая','Левая'),('Правая','Правая')]

class IndicatorsForm(FlaskForm):
    #hist_number = StringField('Номер истории болезни', validators=[DataRequired())
    date_begin = DateField('Дата')

# -- Основной диагноз
class HistoryMainDiagnosForm(FlaskForm):
    diagnos = SelectField('Диагноз', coerce = int, validators=[DataRequired()])
    side_damage = SelectField('Сторона поражения', coerce = str, validators=[DataRequired()])
    date_created = DateField('Дата установления', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(HistoryMainDiagnosForm, self).__init__(*args, **kwargs)
        self.diagnos.choices=[(diagnos.id, diagnos.description)
                              for diagnos in DiagnoseItem.query.filter(DiagnoseItem.type=='Основной').order_by(DiagnoseItem.id).all()]
        self.side_damage.choices=[('Левая','Левая'),('Правая','Правая')]

# -- Сопутствующий диагноз
class HistoryOtherDiagnosForm(FlaskForm):
    diagnos = SelectField('Диагноз', coerce = int, validators=[DataRequired()])
    date_created = DateField('Дата назначения', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(HistoryOtherDiagnosForm, self).__init__(*args, **kwargs)
        self.diagnos.choices=[(diagnos.id, diagnos.description)
                              for diagnos in DiagnoseItem.query.filter(DiagnoseItem.type=='Сопутствующий').order_by(DiagnoseItem.id).all()]

# -- История болезни: список амбулаторных приемов. Создание нового
class HistioryNewAmbulanceForm(FlaskForm):
    event = SelectField('Вид амбулаторного приема', coerce = int, validators=[DataRequired()])
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(HistioryNewAmbulanceForm, self).__init__(*args, **kwargs)
        self.event.choices=[(event.id, event.description)
                              for event in Event.query.filter(Event.type=='2').order_by(Event.id).all()]


# -- История болезни: список госпитализаций. Создание новой
class NewHospitalForm(FlaskForm):
    submit = SubmitField('Создать')

# -- Амбулаторный прием - заголовок
class AmbulanceMainForm(FlaskForm):
    doctor = SelectField('Доктор', coerce = int, validators=[DataRequired()])
    event = SelectField('Вид амбулаторного приема', coerce = int, validators=[DataRequired()])
    date_begin = DateField('Дата приема', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(AmbulanceMainForm, self).__init__(*args, **kwargs)
        self.doctor.choices=[(doctor.id, doctor.fio)
                              for doctor in Doctor.query.order_by(Doctor.fio).all()]
        self.event.choices=[(event_obj.id, event_obj.description)
                              for event_obj in Event.query.filter(Event.type=='2').order_by(Event.id).all()]

class IndicatorsForm(FlaskForm):
    #hist_number = StringField('Номер истории болезни', validators=[DataRequired())
    date_begin = DateField('Дата')


class ProsthesisForm(FlaskForm):
    prosthesis = SelectField('Протез', coerce = int, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(ProsthesisForm, self).__init__(*args, **kwargs)
        self.prosthesis.choices=[(prosthesis_obj.id, prosthesis_obj.description)
                              for prosthesis_obj in Prosthesis.query.all()]

class PreoperativeForm(FlaskForm):
    #hist_number = StringField('Номер истории болезни', validators=[DataRequired())
    date_begin = DateField('Дата')

class TelerentgenographyForm(FlaskForm):
    #hist_number = StringField('Номер истории болезни', validators=[DataRequired())
    date_begin = DateField('Дата')

class Ambulance3SubForm1(FlaskForm):
    # Опросники
    #hist_number = StringField('Номер истории болезни', validators=[DataRequired())
    date_begin = DateField('Дата')

class Ambulance3SubForm2(FlaskForm):
    # Осложнения
    complication = SelectField('Осложнение', coerce = int, validators=[DataRequired()])
    date_created = DateField('Дата возникновения', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(Ambulance3SubForm2, self).__init__(*args, **kwargs)
        self.complication.choices=[(value.id, value.description) for value in Complication.query.filter_by(type='Поздние').all()]

class Ambulance3SubForm3(FlaskForm):
    # Заключение
    date_begin = DateField('Дата', validators=[DataRequired()])
    prostesis = SelectField('Протез функционирует', coerce = int, validators=[DataRequired()])
    conclusions = SelectField('Заключение', coerce = int, validators=[DataRequired()])
    recomendations = SelectField('Рекомендации', coerce = int, validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(Ambulance3SubForm3, self).__init__(*args, **kwargs)
        self.prostesis.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=97).all()]
        self.conclusions.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=104).all()]
        self.recomendations.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=105).all()]

class Ambulance3SubForm4(FlaskForm):
    # Заключение
    date_begin = DateField('Дата', validators=[DataRequired()])
    patient_is_live = SelectField('Пациент жив', coerce = int, validators=[DataRequired()])
    date_died = DateField('Дата смерти', validators=[DataRequired()])
    reason_died = SelectField('Причина смерти', coerce = int, validators=[DataRequired()])
    prostesis = SelectField('Протез функционирует', coerce = int, validators=[DataRequired()])
    date_delete = DateField('Дата удаления', validators=[DataRequired()])
    reason_delete = SelectField('Причина удаления', coerce = int, validators=[DataRequired()])
    conclusions = SelectField('Заключение', coerce = int, validators=[DataRequired()])
    recomendations = SelectField('Рекомендации', coerce = int, validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(Ambulance3SubForm4, self).__init__(*args, **kwargs)
        self.prostesis.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=97).all()]
        self.conclusions.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=104).all()]
        self.recomendations.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=105).all()]
        self.reason_delete.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=99).all()]
        self.reason_died.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=102).all()]
        self.patient_is_live.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=100).all()]


# Рентгенография
class Ambulance3SubForm5(FlaskForm):
    indicators_date_begin = DateField('Дата заполнения', validators=[DataRequired()])
    zone_light1 = SelectField('Наличие зоны просветления вокруг', coerce = int, validators=[DataRequired()])
    zone_light2 = SelectField('Наличие зоны просветления вокруг', coerce = int, validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(Ambulance3SubForm5, self).__init__(*args, **kwargs)
        self.zone_light1.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=113).all()]
        self.zone_light2.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=114).all()]


# Телерентгенография нижних конечностей
class Ambulance3SubForm6(FlaskForm):
    indicators_date_begin = DateField('Дата заполнения', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# КТ коленного сустава
class Ambulance3SubForm7(FlaskForm):
    indicators_date_begin = DateField('Дата заполнения', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# Общие сведения о госпитализации
class HospitalSubForm1(FlaskForm):
    date_begin = DateField('Дата госпитализации', validators=[DataRequired()])
    date_end = DateField('Дата выписки')
    doctor = SelectField('Лечащий врач', coerce = int, validators=[DataRequired()])
    doctor_chief = SelectField('Заведующий отделением', coerce = int, validators=[DataRequired()])
    days1 = IntegerField('Койко-день')
    days2 = IntegerField('Предоперационный койко-день ')
    days3 = IntegerField('Послеоперационный койко-день ')
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(HospitalSubForm1, self).__init__(*args, **kwargs)
        self.doctor.choices=[(doctor_obj.id, doctor_obj.fio)
                              for doctor_obj in Doctor.query.order_by(Doctor.fio).all()]
        self.doctor_chief.choices=[(doctor_obj.id, doctor_obj.fio)
                              for doctor_obj in Doctor.query.order_by(Doctor.fio).all()]

# -- История болезни: список госпитализаций. Создание новой
class NewHospitalForm(FlaskForm):
    submit = SubmitField('Создать')

# -- Госпитализация: общие сведения о пациенте
class HospitalSubForm2(FlaskForm):
    date_begin = DateField('Дата', validators=[DataRequired()])
    claims = SelectField('Жалобы', coerce = str, validators=[DataRequired()])
    claims_time = SelectField('Анамнез заболевания: жалобы в течение ', coerce = str, validators=[DataRequired()])
    diseases = SelectField('Перенесенные заболевания', coerce = str, validators=[DataRequired()])
    traumas = SelectField('Операции, травмы', coerce = str, validators=[DataRequired()])
    smoking = SelectField('Курение', coerce = str, validators=[DataRequired()])
    alcohol = SelectField('Алкоголь', coerce = str, validators=[DataRequired()])
    allergy = SelectField('Аллергологический анамнез', coerce = str, validators=[DataRequired()])
    genetic = SelectField('Наследственные заболевания', coerce = str, validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(HospitalSubForm2, self).__init__(*args, **kwargs)
        self.claims.choices=[('Да','Да'),('Нет','Нет')]
        self.claims_time.choices=[('до 1 года','до 1 года'),('от 1 до 3 лет','от 1 до 3 лет'),\
                                  ('от 3 до 5 лет','от 3 до 5 лет'),\
                                  ('более 5 лет','более 5 лет')]
        self.traumas.choices=[('Да','Да'),('Нет','Нет')]
        self.diseases.choices=[('Да','Да'),('Нет','Нет')]
        self.smoking.choices=[('Да','Да'),('Нет','Нет')]
        self.alcohol.choices=[('Часто','Часто'),('Редко','Редко')]
        self.allergy.choices=[('Да','Да'),('Нет','Нет')]
        self.genetic.choices=[('Да','Да'),('Нет','Нет')]

# -- Госпитализация: Данные объективного осмотра
class HospitalSubForm3(FlaskForm):
    indicators_date_begin = DateField('Дата осмотра', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Госпитализация: Рентгенография коленного сустава в двух проекциях
class HospitalSubForm4(FlaskForm):
    prosthesis = SelectField('Протез', coerce = int, validators=[DataRequired()])
    indicators_date_begin = DateField('Дата планирования', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(HospitalSubForm4, self).__init__(*args, **kwargs)
        self.prosthesis.choices=[(prosthesis_obj.id, prosthesis_obj.description)
                              for prosthesis_obj in Prosthesis.query.all()]

# -- Телерентгенография
class HospitalSubForm5(FlaskForm):
    indicators_date_begin = DateField('Дата планирования', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Госпитализация: Опросники
class HospitalSubForm6(FlaskForm):
    save = SubmitField('Сохранить')

# -- Госпитализация: Результаты лабораторных исследований
class HospitalSubForm7(FlaskForm):
    indicators_date_begin = DateField('Дата', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Госпитализация: Операции
class HospitalSubForm8(FlaskForm):
    create = SubmitField('Создать')

# -- Операция: заголовок
class OperationsSubForm1(FlaskForm):
    doctor_surgeon = SelectField(" Хирург", coerce = int, validators=[DataRequired()])
    doctor_assistant = SelectField("Ассистент хирурга", coerce = int, validators=[DataRequired()])
    operation_order = IntegerField("Очередность", validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(OperationsSubForm1, self).__init__(*args, **kwargs)        
        self.doctor_surgeon.choices=[(doctor_surgeon.id, doctor_surgeon.fio)
                              for doctor_surgeon in Doctor.query.all()]
        self.doctor_assistant.choices=[(doctor_assistant.id, doctor_assistant.fio)
                              for doctor_assistant in Doctor.query.all()]

# -- Операции: Показатели операции
class OperationsSubForm2(FlaskForm):
    operation_date_begin = DateField('Дата начала операции', validators=[DataRequired()])
    anesthesia = SelectField('Анастезия', coerce = int, validators=[DataRequired()])
    anesthesia_begin = TimeField('Начало анестезии', validators=[DataRequired()])
    anesthesia_end = TimeField('Окончание анестезии', validators=[DataRequired()])
    anesthesia_duration = IntegerField('Длительность анастезии (мин)', validators=[DataRequired()])
    surgical_access = SelectField('Хирургический доступ', coerce = int, validators=[DataRequired()])
    operation_specificity = SelectField('Особенности операции', coerce = int, validators=[DataRequired()])
    technical_difficulty = SelectField('Технические трудности', coerce = int, validators=[DataRequired()])
    intraoperative_blood_loss = IntegerField('Интраоперационная кровопотеря (мл)', validators=[DataRequired()])
    wound_drainage = SelectField('Дренирование раны', coerce = int, validators=[DataRequired()])
    amount_of_water = IntegerField('Количество отделяемого по дренажу (мл)', validators=[DataRequired()])
    duration_drainage = IntegerField('Длительность дренирования (ч)', validators=[DataRequired()])
    intra_complications = SelectField('Интраоперационные осложнения', coerce = int, validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(OperationsSubForm2, self).__init__(*args, **kwargs)
        self.anesthesia.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=77).all()]
        self.surgical_access.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=81).all()]
        self.operation_specificity.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=82).all()]
        self.technical_difficulty.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=83).all()]
        self.wound_drainage.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=85).all()]
        self.intra_complications.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=96).all()]


# -- Операции: Тестирование операционной бригады
class OperationsSubForm3(FlaskForm):
    indicators_date = DateField('Дата', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Операции: Этапы операции
class OperationsSubForm4(FlaskForm):
    save = SubmitField('Сохранить')

# -- Операции: Наблюдения после операции
class OperationsSubForm5(FlaskForm):
    event = SelectField('Дата после операции', coerce = int, validators=[DataRequired()])
    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(OperationsSubForm5, self).__init__(*args, **kwargs)
        self.event.choices=[(value.id, value.description) for value in Event.query.filter(Event.type=='5').order_by(Event.id).all()]

# -- Операции: Ранние послеоперационные осложнения
class OperationsSubForm6(FlaskForm):
    complication = SelectField('Осложнение', coerce = int, validators=[DataRequired()])
    date_created = DateField('Дата возникновения', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self, *args, **kwargs):
        super(OperationsSubForm6, self).__init__(*args, **kwargs)
        self.complication.choices=[(value.id, value.description) for value in Complication.query.filter_by(type='Послеоперационные').all()]


# -- Операции: Заключение
class OperationsSubForm7(FlaskForm):
    # Заключение
    date_begin = DateField('Дата', validators=[DataRequired()])
    conclusions = SelectField('Заключение', coerce = int, validators=[DataRequired()])
    recomendations = SelectField('Рекомендации', coerce = int, validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(OperationsSubForm7, self).__init__(*args, **kwargs)
        self.conclusions.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=104).all()]
        self.recomendations.choices=[(value.id_value, value.text_value) for value in IndicatorDef.query.filter_by(indicator_id=105).all()]

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- VAS
class ProfileSubForm1(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    num_value = IntegerField('Значение показателя VAS (от 0 до 10):') #validators=[DataRequired()])
    submit = SubmitField('Сохранить')


    #def validate_num_value(self, field):

    #    if field.data < 0 or field.data > 10:
    #        print(type(self.num_value.errors))
    #        print(self.num_value.errors)
    #        self.num_value.errors.append('Значение должно быть от 0 до 10')
    #        raise ValidationError('Значение от 0 до 10')

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- ASA
class ProfileSubForm2(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value = SelectField('Класс по ASA:', coerce = str, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(ProfileSubForm2, self).__init__(*args, **kwargs)
        self.value.choices=[('ASA1','ASA1'),('ASA2','ASA2'),('ASA3','ASA3')]

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- KSS
class ProfileSubForm3(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value_kss_k = IntegerField('Шкала колена (Knee Score) от 0 до 100:')#, validators=[DataRequired()])
    value_kss_f = IntegerField('Шкала функции (Function Score) от 0 до 100:')#, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- OKS
class ProfileSubForm4(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value_oks = IntegerField('OKS от 0 до 48:')#, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- WOMAC
class ProfileSubForm5(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value_a = IntegerField('A - боль в коленном суставе (от 0 до 20):')#, validators=[DataRequired()])
    value_b = IntegerField('B - скованность коленного сустава (от 0 до 8):')#, validators=[DataRequired()])
    value_c = IntegerField('C - степень затруднения - функция коленного сустава (от 0 до 68):')#, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- SF-36
class ProfileSubForm6(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value_pf = IntegerField('PF - Физическое функционирование (от 10 до 30):', validators=[DataRequired()])
    value_rp = IntegerField('RP - Ролевое (физическое) функционирование (от 4 до 8):', validators=[DataRequired()])
    value_p = IntegerField('P - Боль (от 2 до 12):', validators=[DataRequired()])
    value_gh = IntegerField('GH - Общее здоровье (от 5 до 25):', validators=[DataRequired()])
    value_vt = IntegerField('VT - Общее здоровье (от 4 до 24):', validators=[DataRequired()])
    value_sf = IntegerField('SF - Социальное функционирование (от 2 до 10):', validators=[DataRequired()])
    value_re = IntegerField('RE - Эмоциональное функционирование (от 3 до 6):', validators=[DataRequired()])
    value_mh = IntegerField('MH - Психологическое здоровье (от 5 до 30):', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- Спилберг
class ProfileSubForm7(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value_ra = IntegerField('STAI-RA - РЕАКТИВНАЯ ТРЕВОЖНОСТЬ (от 20 до 80):', validators=[DataRequired()])
    value_pa = IntegerField('STAI-PA - ЛИЧНОСТНАЯ ТРЕВОЖНОСТЬ (от 20 до 80):', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- fjs-12
class ProfileSubForm8(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value_fjs = IntegerField('FJS-12 - Шкала «забытого сустава» (от 0 до 100):')#, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# -- Анкеты: модальные формы для заполнения результатов разделов
# ---- SLR
class ProfileSubForm9(FlaskForm):
    date_created = DateField('Дата заполнения', validators=[DataRequired()])
    value_slr = IntegerField('SLR - Шкала SLR (от 0 до 5):')#, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# -- Послеоперационное наблюдение: Данные объективного осмотра
class PostOperationsSubForm1(FlaskForm):
    indicators_date_begin = DateField('Дата заполнения', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Послеоперационное наблюдение: Результаты лабораторных исследований
class PostOperationsSubForm2(FlaskForm):
    indicators_date_begin = DateField('Дата заполнения', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Послеоперационное наблюдение: Телерентгенография нижних конечностей
class PostOperationsSubForm3(FlaskForm):
    indicators_date_begin = DateField('Дата заполнения', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Послеоперационное наблюдение: КТ коленного сустава
class PostOperationsSubForm4(FlaskForm):
    indicators_date_begin = DateField('Дата заполнения', validators=[DataRequired()])
    save_indicators = SubmitField('Сохранить')

# -- Послеоперационное наблюдение: Опросники
class PostOperationsSubForm5(FlaskForm):
    save = SubmitField('Сохранить')
