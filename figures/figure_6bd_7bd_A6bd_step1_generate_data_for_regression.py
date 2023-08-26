import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta


def to_dest(users, districts_analyze, if_fix, variable):
    v = variable_dict[variable]
    col = ['user', 'if_move', 'v', 'd', 'date', 't', 'home', 'dest']
    regression_all = pd.DataFrame(columns=col)
    for d_this in districts_analyze:
        users_this = users
        if d_this == 11:
            users_this['t'] = ['r2u'] * len(users_this)
        else:
            users_this['t'] = ['r2r'] * len(users_this)
            users_this.loc[users_this['home'] == 11, 't'] = 'u2r'
        users_moveto = users_this[users_this.dest == d_this]
        users_remain = users_this[users_this.dest != d_this]

        if if_fix:
            col_select = ['user', 'if_move', v + '_' + str(d_this),
                          'd_' + str(d_this), 'date', 't', 'home', 'dest']
            col_new_name = {v + '_' + str(d_this): 'v',
                            'd_' + str(d_this): 'd'}
            users_moveto['if_move'] = [1] * len(users_moveto)
            users_remain['if_move'] = [0] * len(users_remain)
            users_moveto = users_moveto[col_select]
            users_moveto.rename(columns=col_new_name,
                                inplace=True)
            #  neet to set the destination as the one which is being analyzed
            users_moveto['dest'] = [d_this] * len(users_moveto)
            users_remain = users_remain[col_select]
            users_remain.rename(columns=col_new_name,
                                inplace=True)
            users_remain['dest'] = [d_this] * len(users_remain)
            regression_all = regression_all.append(users_moveto)
            regression_all = regression_all.append(users_remain)

        print(d_this)
    return regression_all


def from_home(users, if_fix, variable):
    col = ['user', 'if_move', 'v', 'd', 'date', 't', 'home', 'dest']
    regression_all = pd.DataFrame(columns=col)
    users['t'] = 'r'
    users.loc[users['home'] == 11, 't'] = 'u'

    users_move = users[users.type.isin([1, 2, 5])]
    users_remain = users[~(users.type.isin([1, 2, 5]))]

    v = variable_dict[variable]

    if if_fix:
        col_select = ['user', 'if_move', v + '_home',
                      'd_home', 'date', 't', 'home', 'dest']
        col_new_name = {v + '_home': 'v', 'd_home': 'd'}
        users_move['if_move'] = [1] * len(users_move)
        users_remain['if_move'] = [0] * len(users_remain)
        users_move = users_move[col_select]
        users_move.rename(columns=col_new_name, inplace=True)
        users_remain = users_remain[col_select]
        users_remain.rename(columns=col_new_name, inplace=True)
        regression_all = regression_all.append(users_move)
        regression_all = regression_all.append(users_remain)

    return regression_all


if __name__ == '__main__':
    start_date = datetime.strptime('2006 7', '%Y %m')
    end_date = datetime.strptime('2008 6', '%Y %m')
    start_date_str = start_date.strftime('%Y%m')[2:]
    end_date_str = end_date.strftime('%Y%m')[2:]
    loop_num = (relativedelta(end_date, start_date).months
                + 12 * relativedelta(end_date, start_date).years
                + 1)

    date = start_date.strftime('%Y%m') + '-' + end_date.strftime('%Y%m')

    for i in range(loop_num):
        t2 = start_date + relativedelta(months=i)
        t2_str = t2.strftime('%Y%m')[2:]
        network_file_2 = 'data/' + t2_str + '_user_result.csv'
        users_2 = pd.read_csv(network_file_2, sep=',')
        users_2['date'] = [t2_str] * len(users_2)
        if i == 0:
            users = users_2
        else:
            users = users.append(users_2)
        print(t2)

    users = users.replace('None', np.nan)
    print('user result read')
    print(users.shape)

    migration_file = 'data/0801_migration.txt'
    migration = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]
    dist = list(set(migration['home']) | set(migration['dest']))
    print('migration read')
    print(migration.shape)

    types = users[['user', 'type']].groupby('type').count()
    types_value = types['user'].values.tolist()

    # remove roamers
    users = users[users.type != 6]

    # convert nan to 0 for degree and information
    for v in ['d', 'l', 's']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)

    variables = []
    variable_dict = {'degree': 'd',
                     'support': 's',
                     'cluster': 'c',
                     'information': 'l'}
    variables.append(['Information', 0, 1001, 10])
    variables.append(['Support', 0, 1.01, 0.04])
    variables.append(['Cluster', 0, 1.01, 0.04])

    for v_all in variables:
        v, v_min, v_max, v_step = v_all
        if v == 'Degree':
            if_fix = False
        else:
            if_fix = True
        v_lower = v.lower()

        dest = to_dest(users, dist, if_fix, v_lower)
        dest.to_csv('data/' + v_lower + '_dest_for_regression.csv', index=False)