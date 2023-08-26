# To prepare the data for regression: 
# Disaggregating the friend of friend effect by the strength of the 2nd-degree tie

import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def to_dest(users, districts_analyze, if_fix):
    column_name = ['user', 'if_move', 'd', 'l', 's_s_infor', 's_w_infor', 'w_s_infor', 'w_w_infor',
                   'date', 't',
                   'home', 'dest']
    regression_all = pd.DataFrame(columns=column_name)
    for d_this in districts_analyze:
        users_this = users
        if d_this == 11:
            users_this['t'] = ['r2u'] * len(users_this)
        else:
            users_this['t'] = ['r2r'] * len(users_this)
            users_this.loc[users_this['home'] == 11, 't'] = 'u2r'
        users_moveto = users_this[users_this.dest == d_this]
        users_remain = users_this[users_this.dest != d_this]

        #  fix degree
        if if_fix:
            users_moveto['if_move'] = [1] * len(users_moveto)
            users_remain['if_move'] = [0] * len(users_remain)
            column_new_name = {
                'l_' + str(d_this): 'l',
                's_s_infor_' + str(d_this): 's_s_infor',
                's_w_infor_' + str(d_this): 's_w_infor',
                'w_s_infor_' + str(d_this): 'w_s_infor',
                'w_w_infor_' + str(d_this): 'w_w_infor',
                'd_' + str(d_this): 'd'
            }
            column_select = ['user', 'if_move',
                             'd_' + str(d_this),
                             'l_' + str(d_this),
                             's_s_infor_' + str(d_this),
                             's_w_infor_' + str(d_this),
                             'w_s_infor_' + str(d_this),
                             'w_w_infor_' + str(d_this),
                             'date', 't',
                             'home', 'dest']
            users_moveto = users_moveto[column_select]
            users_moveto.rename(columns=column_new_name, inplace=True)
            users_moveto['dest'] = [d_this] * len(users_moveto)
            users_remain = users_remain[column_select]
            users_remain.rename(columns=column_new_name, inplace=True)
            users_remain['dest'] = [d_this] * len(users_remain)
            regression_all = regression_all.append(users_moveto)
            regression_all = regression_all.append(users_remain)

        print(d_this)
    return regression_all

if __name__ == '__main__':
    t_s = time.time()
    start_date = datetime.strptime('2006 7', '%Y %m')
    end_date = datetime.strptime('2008 6', '%Y %m')
    start_date_str = start_date.strftime('%Y%m')[2:]
    end_date_str = end_date.strftime('%Y%m')[2:]
    loop_num = (relativedelta(end_date, start_date).months
                + 12 * relativedelta(end_date, start_date).years
                + 1)
    date = start_date.strftime('%Y%m') + '-' + end_date.strftime('%Y%m')

    migration_file = 'data/0801_migration.txt'
    migration = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]
    dist = list(set(migration['home']) | set(migration['dest']))
    print('migration read')
    print(migration.shape)

    for i in range(loop_num):
        t2 = start_date + relativedelta(months=i)
        t2_str = t2.strftime('%Y%m')[2:]
        network_file_2 = 'data/' + t2_str + '_user_result.csv'
        users_2 = pd.read_csv(network_file_2, sep=',')
        users_2['date'] = [t2_str] * len(users_2)
        cols = users_2.columns.tolist()
        d_list = []
        for c in cols:
            if c[:2] == 'd_':
                d_list.append(c)
        users_2 = users_2[['user', 'date'] + d_list]
        strongtie_file = 'data/' + t2_str + '_user_result_infor_support_strong.csv'
        strongtie = pd.read_csv(strongtie_file, sep=',')
        users_2 = users_2.merge(strongtie, on='user', how='inner')

        if i == 0:
            users = users_2
        else:
            users = users.append(users_2)
        print(t2)
    users = users.replace('None', np.nan)
    print('user result read')
    print(users.shape)

    types = users[['user', 'type']].groupby('type').count()
    types_value = types['user'].values.tolist()

    # remove roamers
    users = users[users.type != 6]

    for i in dist:
        users['l_' + str(i)] = users['s_s_infor_' + str(i)] + users['s_w_infor_' + str(i)] + users['w_s_infor_' + str(i)] + users['w_w_infor_' + str(i)]
    # convert nan to 0 for degree and information
    for v in ['d', 'l', 's_s_infor', 's_w_infor', 'w_s_infor', 'w_w_infor']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)

    if_fix = True
    column_select = ['user', 'if_move',
                     'd', 'l', 's_s_infor', 's_w_infor', 'w_s_infor', 'w_w_infor',
                     't', 'date',
                     'home', 'dest']
    # destination
    a = to_dest(users, dist, if_fix)
    dest = a[column_select]
    dest.to_csv('data/dest_home_d_s_l_infor_strong.csv', index=False)
