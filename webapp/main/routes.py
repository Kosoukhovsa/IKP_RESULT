from flask import render_template, url_for, Blueprint, redirect, flash, request, session, jsonify
from webapp.auth import permission_required
from flask_login import login_required
from Tools.filetools import FileEngine
from Tools.sqltools import SqlEngine
from webapp import db
from . import LoadAllDictionary

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)

@main_blueprint.route('/')
def index():
    return render_template('home.html')

# Список справочников
@main_blueprint.route('/main/dict_list')
@login_required
@permission_required('ADMIN')
def dict_list():
    # Получить список таблиц с количеством записей
    # { table: rows }
    tables_dict = SqlEngine.GetTablesInfo(db)
    print(tables_dict)
    # Получить спсисок настраиваемых справочников и ограничить выводимый список только ими
    dict_list = FileEngine.GetDictList()
    only_dict = {}
    for (k,v) in tables_dict.items():
        if k in dict_list:
            only_dict[k]=v
    return render_template('main/dict_dashboard.html', tables_dict=only_dict)

# Загрузка всех справочников
@main_blueprint.route('/admin/dict_load_all/', methods= ['GET','POST'])
@login_required
@permission_required('ADMIN')
def dict_load_all():
    # Загрузить список справочников  из файла
    LoadAllDictionary()
    return redirect(url_for('.dict_list'))

# Загрузка всех справочников через ajax
@main_blueprint.route('/main/dict_load_all_ajax/', methods= ['POST'])
@login_required
@permission_required('ADMIN')
def dict_load_all_ajax():
    # Загрузить список справочников  из файла
    LoadAllDictionary()
    return jsonify('ok')
