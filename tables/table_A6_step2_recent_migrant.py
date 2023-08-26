import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def to_dest(users, districts_analyze, if_fix):
    column_name = ['user', 'if_move', 'd', 'l', 's', 'recent_mig', 'co_mig',
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
            column_new_name = {'s_' + str(d_this): 's',
                               'l_' + str(d_this): 'l',
                               'd_' + str(d_this): 'd',
                               'recent_mig_' + str(d_this): 'recent_mig',
                               'co_mig_' + str(d_this): 'co_mig'}
            column_select = ['user', 'if_move',
                             'd_' + str(d_this),
                             'l_' + str(d_this),
                             's_' + str(d_this),
                             'recent_mig_' + str(d_this),
                             'co_mig_' + str(d_this),
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


def from_home(users, if_fix):
    column_name = ['user', 'if_move', 'd', 'l', 's',
                   'date', 't',
                   'home', 'dest']
    regression_all = pd.DataFrame(columns=column_name)
    users['t'] = 'r'
    users.loc[users['home'] == 11, 't'] = 'u'

    users_move = users[users.type.isin([1, 2, 5])]
    users_remain = users[~(users.type.isin([1, 2, 5]))]

    column_select = ['user', 'if_move', 'd_home', 'l_home', 's_home',
                     'date', 't', 'home', 'dest']
    column_new_name = {'l_home': 'l', 's_home': 's', 'd_home': 'd'}
    if if_fix:
        users_move['if_move'] = [1] * len(users_move)
        users_remain['if_move'] = [0] * len(users_remain)
        users_move = users_move[column_select]
        users_move.rename(columns=column_new_name, inplace=True)
        users_remain = users_remain[column_select]
        users_remain.rename(columns=column_new_name, inplace=True)
        regression_all = regression_all.append(users_move)
        regression_all = regression_all.append(users_remain)

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

    for i in range(loop_num):
        t2 = start_date + relativedelta(months=i)
        t2_str = t2.strftime('%Y%m')[2:]
        network_date = start_date + relativedelta(months=i - 1)
        network_date = network_date.strftime('%Y%m')[2:]
        network_file_2 = 'data/' + t2_str + '_user_result.csv'
        users_2 = pd.read_csv(network_file_2, sep=',')
        users_2['date'] = [t2_str] * len(users_2)
        recentmigrants = pd.read_csv('data/' + t2_str + '_user_result_recent_migrant.csv')
        recentmigrants = recentmigrants.drop(columns=['home'])
        for _i in dist:
            recentmigrants = recentmigrants.rename(
                columns={
                    'recent_mig_friend_' + str(_i): 'recent_mig_' + str(_i),
                    'co_mig_friend_' + str(_i): 'co_mig_' + str(_i),
                }
            )
        users_2 = users_2.merge(recentmigrants, on='user', how='left')
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
    for v in ['d', 'l', 's', 'recent_mig', 'co_mig']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)

    if_fix = True
    column_select = ['user', 'if_move',
                     'd', 'l', 's', 'recent_mig', 'co_mig',
                     't', 'date',
                     'home', 'dest']
    # destination
    a = to_dest(users, dist, if_fix)
    dest = a[column_select]

    # home
    b = from_home(users, if_fix)
    column_select.remove('recent_mig')
    column_select.remove('co_mig')
    home = b[column_select]

    # merge home and destination (for pull and push regression)
    dest.columns = ['user', 'if_move', 'd_dest', 'l_dest', 's_dest', 'recent_mig_dest', 'co_mig_dest',
                    't_dest', 'date', 'home_dest', 'dest_dest']
    home.columns = ['user', 'if_move', 'd_home', 'l_home', 's_home',
                    't_home', 'date', 'home_home', 'dest_home']

    dest_home = dest.merge(home, on=['user', 'date'], how='inner')
    dest_home['user_dest'] = dest_home.apply(lambda x: x['user']+'_'+str(x['dest_dest']), axis=1)
    dest_home['user_degree_dest'] = dest_home.apply(lambda x: x['user']+'_'+str(x['d_dest']), axis=1)
    dest_home['user_month'] = dest_home.apply(lambda x: x['user']+'_'+str(x['date']), axis=1)
    dest_home['home_dest_user'] = dest_home.apply(lambda x: str(x['home_dest'])+'_'+str(x['dest_dest'])+x['user'], axis=1)
    dest_home['home_dest_date'] = dest_home.apply(lambda x: str(x['home_dest'])+'_'+str(x['dest_dest'])+str(x['date']), axis=1)
    dest_home['if_move'] = dest_home['if_move_x']
    dest_home.to_csv('data/dest_home_d_s_l_recent_migrant.csv', index=None)
