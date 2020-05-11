from .models import Clinic, Complication, DiagnoseItem, Doctor, Event, Indicator,\
                IndicatorDef, IndicatorGroup, IndicatorNorm, \
                OperationStep, Profile, ProfileAnswer, ProfileItem, Prosthesis, \
                ProsthesisComponent, Reason, ResearchGroup, ProfileSection, ProfileSectionAnswer
from Tools.filetools import FileEngine
from .. import db


def create_module(app, **kwargs):
    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)

def LoadAllDictionary():
    """
        Первоначальная загрузка всех справочников из файла /Tools/Dictionaries.xlsx

    """
    # Получить спсисок справочников
    dict_list = FileEngine.GetDictList()
    # Клиники
    dict_values = FileEngine.GetListData('Clinic')
    for i in dict_values:
        new_c = Clinic.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = Clinic(id=i['id'], description=i['description'])
        db.session.add(new_c)

    # Причины исключения
    dict_values = FileEngine.GetListData('Reason')
    for i in dict_values:
        new_c = Reason.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = Reason(id=i['id'], description=i['description'])
        db.session.add(new_c)

    # Диагнозы
    dict_values = FileEngine.GetListData('DiagnoseItem')
    for i in dict_values:
        new_c = DiagnoseItem.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = DiagnoseItem(id=i['id'],
                         description=i['description'],
                         mkb10=i['mkb10'],
                         type=i['type'])
        db.session.add(new_c)

    # Протезы
    dict_values = FileEngine.GetListData('Prosthesis')
    for i in dict_values:
        new_c = Prosthesis.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = Prosthesis(id=i['id'],
                         description=i['description'],
                         firm=i['firm'],
                         type=i['type'],
                         model=i['model'])
        db.session.add(new_c)

    # Осложнения
    dict_values = FileEngine.GetListData('Complication')
    for i in dict_values:
        new_c = Complication.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = Complication(id=i['id'],
                         description=i['description'],
                         type=i['type'])
        db.session.add(new_c)

    # Группы исследования
    dict_values = FileEngine.GetListData('ResearchGroup')
    for i in dict_values:
        new_c = ResearchGroup.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = ResearchGroup(id=i['id'],
                         description=i['description'],
                         clinic_id=i['clinic_id'])
        db.session.add(new_c)

    # Врачи
    dict_values = FileEngine.GetListData('Doctor')
    for i in dict_values:
        new_c = Doctor.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = Doctor(id=i['id'],
                        first_name=i['first_name'],
                        second_name=i['second_name'],
                        fio=i['fio']
                        )
        db.session.add(new_c)

    # Группы показателей
    dict_values = FileEngine.GetListData('IndicatorGroup')
    for i in dict_values:
        new_c = IndicatorGroup.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue

        item = IndicatorGroup(id=i['id'])
        item.description = i['description']
        db.session.add(item)

    # Показатели
    dict_values = FileEngine.GetListData('Indicator')
    for i in dict_values:
        new_c = Indicator.query.get(i['id'])
        if new_c is None:
            # Новый элемент
            item = Indicator()
            item.id=i['id']
        else:
            item = new_c

        item.description=i['description']
        item.is_calculated=i['is_calculated']
        item.group_id=i['group_id']
        if i['unit'] is None:
            item.unit=''
        else:
            item.unit=i['unit']
        if i['type'] is None:
            item.type=''
        else:
            item.type=i['type']
        db.session.add(item)

    # Значения по умолчанию
    dict_values = FileEngine.GetListData('IndicatorDef')
    for i in dict_values:
        new_c = IndicatorDef.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = IndicatorDef(id=i['id'],
                               indicator_id=i['indicator_id'],
                               text_value=i['text_value'],
                               num_value=i['num_value'],
                               id_value=i['id_value']
                               )
        db.session.add(new_c)

    # Нормативы показателей
    dict_values = FileEngine.GetListData('IndicatorNorm')
    for i in dict_values:
        new_c = IndicatorNorm.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = IndicatorNorm(id=i['id'],
                               indicator_id=i['indicator_id'],
                               nvalue_from=i['nvalue_from'],
                               nvalue_to=i['nvalue_to']
                               )
        db.session.add(new_c)

    # События
    dict_values = FileEngine.GetListData('Event')
    for i in dict_values:
        new_c = Event.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = Event(
                       id=i['id'],
                       description=i['description'],
                       type=i['type']
                       )
        db.session.add(new_c)

    # Шаги операций
    dict_values = FileEngine.GetListData('OperationStep')
    for i in dict_values:
        new_c = OperationStep.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = OperationStep(
                       id=i['id'],
                       description=i['description'],
                       order=i['order']
                       )
        db.session.add(new_c)

    # Анткеты
    dict_values = FileEngine.GetListData('Profile')
    for i in dict_values:
        new_c = Profile.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            new_c.description=i['description']
            db.session.add(new_c)
            continue
        new_c = Profile(
                       id=i['id'],
                       description=i['description']
                       )
        db.session.add(new_c)

    # Вопросы анкет
    dict_values = FileEngine.GetListData('ProfileItem')
    for i in dict_values:
        new_c = ProfileItem.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = ProfileItem(
                       id=i['id'],
                       profile_id=i['profile_id'],
                       description=i['description'],
                       item_group=i['item_group']
                       )
        db.session.add(new_c)

    # Компоненты протезов
    dict_values = FileEngine.GetListData('ProsthesisComponent')
    for i in dict_values:
        new_c = ProsthesisComponent.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = ProsthesisComponent(
                       id=i['id'],
                       model = i['model'],
                       component=i['component'],
                       value=i['value']
                       )

        db.session.add(new_c)

    # Разделы анкет
    dict_values = FileEngine.GetListData('ProfileSection')
    for i in dict_values:
        new_c = ProfileSection.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = ProfileSection(
                       id=i['id'],
                       profile_id=i['profile_id'],
                       description=i['description'],
                       profile_section=i['profile_section']
                       )
        db.session.add(new_c)

    # Возможные ответы разделов
    dict_values = FileEngine.GetListData('ProfileSectionAnswer')
    for i in dict_values:
        new_c = ProfileSectionAnswer.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = ProfileSectionAnswer(
                       id=i['id'],
                       profile_id=i['profile_id'],
                       profile_section_id=i['profile_section_id'],
                       response_str=i['response_str'],
                       response_num_value_from=i['response_num_value_from'],
                       response_num_value_to=i['response_num_value_to']
                       )
        db.session.add(new_c)

    db.session.commit()

"""
    # Возможные ответы
    dict_values = FileEngine.GetListData('ProfileAnswer')
    for i in dict_values:
        new_c = ProfileAnswer.query.get(i['id'])
        if new_c:
            # Такой элемент уже есть
            continue
        new_c = ProfileAnswer(
                       id=i['id'],
                       profile_id = i['profile_id'],
                       profile_item_id=i['profile_item_id'],
                       response=i['response']
                       )
        db.session.add(new_c)
"""
