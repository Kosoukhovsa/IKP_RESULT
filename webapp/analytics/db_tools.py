import pandas as pd
from webapp import db 

"""
Набор функций для выборки данных из базы
"""

def get_research_groups():          
        """
        Получить список групп исследования
        """ 
        str_sql= """
        select 
        distinct description as value
        from "ResearchGroup" rg 
        ;
        """
        df_r_groups = pd.read_sql_query(str_sql, db.engine)
        return list(df_r_groups.value.unique())

def get_short_hist_data():          
        """
        Получить краткие данные по истории болезни
        """         
        sql_str_hist = """
            select
            h.clinic_id , -- Клиника           
            h.hist_number, -- Номер истории
            p.id as patient_id,
            '' as fio,
            '' as snils,
            case when p.sex = '1' then 'M' else 'F' end as sex , -- Пол
            (current_date - p.birthdate) / 365 as age, -- Возраст
            h.date_in, -- Дата открытия истории
            h.date_research_in , -- Дата включения в исследование
            h.date_research_out , -- Дата исключения из исследования
            rg.description as research_group, -- Группа исследования
            doc.fio as researcher, -- Врач-исследователь
            rsn.description as reson_out, -- Причина исключения из исследования
            diag.date_created as main_diagnose_date, -- Дата установления диагноза
            diag.side_damage, -- Сторона поражения
            diag_main.mkb10, -- Диагноз МКБ10
            diag_main.description as main_diagnose-- Диагноз
            from "History" as h
            left outer join "ResearchGroup" as rg on
            h.clinic_id = rg.clinic_id  and
            h.research_group_id = rg.id
            left outer join "Doctor" as doc on
            h.doctor_researcher_id = doc.id
            left outer join "Reason" as rsn on
            h.reason_id = rsn.id
            left outer join "Patient" as p on
            h.patient_id = p.id
            left outer join "Diagnose" as diag on
            h.clinic_id = diag.clinic_id and
            h.id = diag.history_id and 
            h.patient_id = diag.patient_id 
            left outer join "DiagnoseItem" as diag_main on
            diag.diagnose_item_id = diag_main.id 
            where (diag_main."type" = 'Основной' or diag_main."type" is null)
            and (current_date - p.birthdate) / 365 > 10
            order by h.date_in, h.hist_number
            ;
        """

        df_history = pd.read_sql_query(sql_str_hist, db.engine) 
        return df_history

