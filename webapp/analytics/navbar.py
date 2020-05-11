import dash_bootstrap_components as dbc


def Navbar():

    navbar = dbc.NavbarSimple(
    children = [
        #dbc.NavItem(dbc.NavLink('ИКП', href='/'))
        dbc.DropdownMenu(
            children = [
                dbc.DropdownMenuItem('Общая статистика',href='/dashapp1_1', external_link = True),
                dbc.DropdownMenuItem('Количественные показатели',href='/dashapp1_2', external_link = True),
                dbc.DropdownMenuItem('Качественные показатели',href='/dashapp1_3', external_link = True)
            ],
            nav=True,
            in_navbar = True,
            label = 'Общие показатели распределения'
                        ),
        dbc.DropdownMenu(
            children = [
                dbc.DropdownMenuItem('Общая статистика по группе',href='/dashapp2_1', external_link = True),
                dbc.DropdownMenuItem('Количественные показатели',href='/dashapp2_2', external_link = True),
                dbc.DropdownMenuItem('Качественные показатели',href='/dashapp2_3', external_link = True)
            ],
            nav=True,
            in_navbar = True,            
            label = 'Анализ показателей одной группы'
                        ),
        dbc.DropdownMenu(
            children = [
                dbc.DropdownMenuItem('Общая статистика',href='/dashapp3_1', external_link = True),
                dbc.DropdownMenuItem('Количественные показатели',href='/dashapp3_2', external_link = True),
                dbc.DropdownMenuItem('Качественные показатели',href='/dashapp3_3', external_link = True)
            ],
            nav=True,
            in_navbar = True,
            label = 'Сравнительный анализ групп'
                        ),
                            ],
    brand = 'ИКП',
    brand_href = "/",
    sticky = 'top',
    brand_external_link = True,
    color = 'secondary',
    dark = True,
    className = 'justify-content-start text-uppercase font-weight-bold px-3'
    )

    return navbar
