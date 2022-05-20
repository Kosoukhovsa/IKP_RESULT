import pandas as pd
from webapp import db 

"""
Набор функций для выборки данных из базы
"""

def get_ind_values():          
        """
        Получить показатели: рост, вес, ИМТ
        """ 
        sql_str_ind = """
        select 
        h.clinic_id, -- клиника
        h.id as hist_id, -- id bcnjhbb
        rg.description as research_group, -- Группа исследования
        case when p.sex = '1' then 'M' else 'F' end as sex , -- Пол
        hist_ev.event_id , -- событие
        ind_vals.indicator_id as ind_id, -- показатель
        i.description as indicator,
        ind_vals.time_created as ind_time, -- время ввода показателя
        ind_vals.num_value -- значение показателя
        from "History" as h
        left outer join "HistoryEvent" hist_ev on
        hist_ev.clinic_id = h.clinic_id and 
        hist_ev.history_id = h.id and 
        hist_ev.patient_id = h.patient_id 
        left outer join "IndicatorValue" as ind_vals on 
        hist_ev.clinic_id = ind_vals.clinic_id and 
        hist_ev.history_id = ind_vals.history_id and 
        hist_ev.id = ind_vals.history_event_id 
        left outer join "Patient" p on 
        h.patient_id = p.id 
        left outer join "Indicator" i on 
        ind_vals.indicator_id = i.id 
        left outer join "ResearchGroup" as rg on
        h.clinic_id = rg.clinic_id  and
        h.research_group_id = rg.id
        ;
        """

        df_ind_values = pd.read_sql_query(sql_str_ind, db.engine)
        return df_ind_values

def get_observations():          
        """
        Получить статистику по наблюдениям
        """ 

        str_observations = """
        -- Сроки наблюдения в месяцах
        select 
        he_obs.history_id ,
        he_obs.clinic_id ,
        he_obs.patient_id,
        rg.description as research_group, -- Группа исследования
        case when p.sex = '1' then 'M' else 'F' end as sex , -- Пол
        he_obs .event_id ,
        case 
        when he_obs .event_id in('9','10') then e.description 
        when he_obs .event_id = 11 and 
        ((date_part('year', he_obs.date_begin) - date_part('year', he_hosp.date_begin)) * 12 + 
                (date_part('month', he_obs.date_begin) - date_part('month', he_hosp.date_begin))) <= 24            
        then 'Ежегодные наблюдения (1 год)'
        when he_obs .event_id = 11 and 
        ((date_part('year', he_obs.date_begin) - date_part('year', he_hosp.date_begin)) * 12 + 
                (date_part('month', he_obs.date_begin) - date_part('month', he_hosp.date_begin))) <= 36            
        then 'Ежегодные наблюдения (2 года)'
        when he_obs .event_id = 11 and 
        ((date_part('year', he_obs.date_begin) - date_part('year', he_hosp.date_begin)) * 12 + 
                (date_part('month', he_obs.date_begin) - date_part('month', he_hosp.date_begin))) <= 48            
        then 'Ежегодные наблюдения (3 года)'
        else '' end as description 
        ,
        -- Количество месяцев наблюдения считаем от операции
        ((date_part('year', he_obs.date_begin) - date_part('year', he_hosp.date_begin)) * 12 + 
                (date_part('month', he_obs.date_begin) - date_part('month', he_hosp.date_begin))) as monthes_observ
        from "HistoryEvent" he_obs -- Наблюдения 3, 6 мес, 1 год
        ---
        left join "HistoryEvent" he_hosp on 
        he_obs.clinic_id  = he_hosp.clinic_id  and 
        he_obs.history_id  = he_hosp.history_id  and 
        he_obs.patient_id  = he_hosp.patient_id  and 
        he_hosp.event_id = 4 and -- Операция
        he_hosp.date_begin is not null
        ---
        left join 
        ( select 
        clinic_id,
        history_id,
        patient_id,
        max(date_begin) as date_begin
        from "HistoryEvent" 
        where 
        event_id in(9,10,11)
        group by
        clinic_id,
        history_id,
        patient_id
        )  he_last_obs on -- Последнее наблюдение 
        he_obs.clinic_id   = he_last_obs.clinic_id  and 
        he_obs.history_id  = he_last_obs.history_id  and 
        he_obs.patient_id  = he_last_obs.patient_id  
        left join "Event" e on 
        he_obs.event_id  = e.id 
        left join "Patient" p on 
        p.id = he_obs.patient_id 
        left join "History" h on 
        he_obs.clinic_id = h.clinic_id and 
        he_obs.history_id = h.id 
        left join "ResearchGroup" rg on 
        h.research_group_id = rg.id 
        where 
        he_obs.event_id in(9,10,11)
        and 
        ((date_part('year', he_obs.date_begin) - date_part('year', he_hosp.date_begin)) * 12 + 
                (date_part('month', he_obs.date_begin) - date_part('month', he_hosp.date_begin))) >= 0
        ;
        """

        df_hevents = pd.read_sql_query(str_observations, db.engine)
        return df_hevents

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

