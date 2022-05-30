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

def get_asa():          
        """
        Получить данные опросника ASA из госпитализации
        """ 
        sql_str_asa = """
        -- Данные опросника ASA из госпитализации
        select 
        rg.description as research_group, -- Группа исследования
        p.id as patient_id,
        he.event_id,
        case when p.sex = '1' then 'M' else 'F' end as sex , -- Пол
        psr.response_str as "ASA"
        from "ProfileSectionResponse" psr 
        left outer join "Patient" p on
        psr.patient_id  = p.id 
        left join "HistoryEvent" he on 
        psr.clinic_id = he.clinic_id and 
        psr.history_id = he.history_id and 
        psr.patient_id = he.patient_id and 
        psr.history_event_id = he.id 
        left join "History" h on 
        psr.clinic_id = h.clinic_id  and 
        psr.history_id = h.id and 
        psr.patient_id = h.patient_id 
        left outer join "ResearchGroup" rg on 
        h.research_group_id = rg.id and 
        h.clinic_id = rg.clinic_id 
        where psr.profile_id = 2 and he.event_id = 9 
        ;
        """
        df_asa = pd.read_sql_query(sql_str_asa, db.engine)
        return df_asa

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

def get_b_days():
        sql_str_b_days = """
        -- Койко - дни
        select 
        --o.clinic_id ,
        h.id as history_id,
        --he.id ,
        --he.date_begin,
        --he.date_end ,
        --o.time_begin ,
        --o.time_end ,
        --cast(operation_log.time_from as date) as oper_date_from,
        --cast(operation_log.time_to as date) as oper_date_to,
        rg.description as research_group, -- Группа исследования
        --he.days1 , -- койко-день
        case 
        when (he.date_end - he.date_begin) > 0 then he.date_end - he.date_begin 
        else 0 end as c_days1, -- общий койко-день
        case 
        when (cast(operation_log.time_from as date) - he.date_begin) > 0 then (cast(operation_log.time_from as date) - he.date_begin) 
        else 0 end as c_days2, -- предоперационный койко-день
        case 
        when (he.date_end - cast(operation_log.time_to as date)) > 0 then (he.date_end - cast(operation_log.time_to as date)) 
        else 0 end as c_days3 -- послеоперационный койко-день
        from "HistoryEvent" he 
        left outer join "History" as h on 
        h.clinic_id  = he.clinic_id  and 
        h.id = he.history_id 
        left outer join "ResearchGroup" rg on 
        h.research_group_id  = rg.id 
        left outer join "Operation" o on 
        he.clinic_id = o.clinic_id and 
        he.history_id = o.history_id and 
        he.id = o.hospital_id 
        left outer join 
        (
        select ol.clinic_id as clinic_id,
        ol.history_id as history_id,
        ol.operation_id as operation_id,
        min(ol.time_begin) as time_from,
        max(ol.time_end) as time_to
        from "OperationLog" ol 
        group by
        ol.clinic_id ,
        ol.history_id ,
        ol.operation_id
        ) as operation_log on 
        o.clinic_id = operation_log.clinic_id and 
        o.history_id = operation_log.history_id and 
        o.id = operation_log.operation_id 
        where 
        he.event_id in(3)
        and (he.date_end - he.date_begin) > 0
        ;
        """
        df_b_days = pd.read_sql(sql_str_b_days, db.engine)
        return df_b_days

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

def get_oper_logs():
        sql_str_oper_logs = """
        -- Статистика по этапам операции
        select 
        ol. history_id as history_id,
        rg.description as research_group,
        ol. operation_id as operation_id,
        os.description as operation_step,
        os."order" as step_order,
        ol.duration_min 
        from "OperationLog" ol 
        left join "OperationStep" os on 
        ol.operation_step_id  = os.id 
        left join "History" h on 
        ol.clinic_id = h.clinic_id and 
        ol.history_id = h.id 
        left join "ResearchGroup" rg on 
        h.research_group_id = rg.id 
        where 
        ol.duration_min is not null 
        and ol.duration_min <= 500
        order by 
        ol.history_id,
        ol.operation_id ,
        --os."order" 
        ol.duration_min desc
        ;
        """

        df_op_logs = pd.read_sql(sql_str_oper_logs, db.engine)
        return df_op_logs

def get_operations():
        sql_str_operations = """
        select 
        o.id ,
        rg.description as research_group, -- Группа исследования
        o.history_id ,
        o.doctor_surgeon_id ,
        d.fio 
        from "Operation" o 
        left join "Doctor" d on 
        o.doctor_surgeon_id  = d.id 
        left join "History" h on 
        h.id = o.history_id and 
        h.clinic_id = o.clinic_id
        left join "ResearchGroup" rg on 
        rg.id = h.research_group_id 
        ;
        """

        df_operations = pd.read_sql(sql_str_operations, db.engine)
        return df_operations

