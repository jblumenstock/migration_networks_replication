# To prepare the data for regression: 
# Disaggregating the friend of friend effect by the strength of the 2nd-degree tie

import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def to_dest(users, districts_analyze, if_fix):
    column_name = ['user', 'if_move', 'd', 'support_sss', 'support_ssw', 'support_sws', 'support_sww', 'support_wss', 'support_wsw', 'support_wws', 'support_www', 'strong_tie', 
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
                'support_sss_' + str(d_this): 'support_sss',
                'support_ssw_' + str(d_this): 'support_ssw',
                'support_sws_' + str(d_this): 'support_sws',
                'support_sww_' + str(d_this): 'support_sww',
                'support_wss_' + str(d_this): 'support_wss',
                'support_wsw_' + str(d_this): 'support_wsw',
                'support_wws_' + str(d_this): 'support_wws',
                'support_www_' + str(d_this): 'support_www',
                'strong_tie_' + str(d_this): 'strong_tie',
                'd_' + str(d_this): 'd'
            }
            column_select = ['user', 'if_move',
                             'd_' + str(d_this),
                             'support_sss_' + str(d_this),
                             'support_ssw_' + str(d_this),
                             'support_sws_' + str(d_this),
                             'support_sww_' + str(d_this),
                             'support_wss_' + str(d_this),
                             'support_wsw_' + str(d_this),
                             'support_wws_' + str(d_this),
                             'support_www_' + str(d_this),
                             'strong_tie_' + str(d_this),
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
        support_strongtie_file = 'data/' + t2_str + '_user_result_infor_support_strong.csv'
        support_strongtie = pd.read_csv(support_strongtie_file, sep=',')
        users_2 = users_2.merge(support_strongtie, on='user', how='inner')

        strongtie_file = 'data/' t2_str + '_user_result_strongtie.csv'
        strongtie = pd.read_csv(strongtie_file, sep=',')
        cols = strongtie.columns.tolist()
        s_list = []
        for c in cols:
            if c[:11] == 'strong_tie_':
                s_list.append(c)
        strongtie = strongtie[['user'] + s_list]
        users_2 = users_2.merge(strongtie, on='user', how='left')

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

    # convert nan to 0 for degree and information
    for v in ['d', 'support_sss', 'support_ssw', 'support_sws', 'support_sww', 'support_wss', 'support_wsw', 'support_wws', 'support_www', 'strong_tie']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)

    if_fix = True
    column_select = ['user', 'if_move',
                     'd', 'support_sss', 'support_ssw', 'support_sws', 'support_sww', 'support_wss', 'support_wsw', 'support_wws', 'support_www', 'strong_tie',
                     't', 'date',
                     'home', 'dest']
    # destination
    a = to_dest(users, dist, if_fix)
    dest = a[column_select]
    dest.to_csv('data/dest_home_d_s_l_support_strong.csv', index=False)
