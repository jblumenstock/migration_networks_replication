import pandas as pd
import numpy as np
import sys
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def to_dest(users, districts_analyze, if_fix):
    column_name = ['user', 'if_move', 'degree', 'information_diff', 'support_diff',
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
            column_new_name = {'information_diff_' + str(d_this): 'information_diff',
                               'support_diff_' + str(d_this): 'support_diff',
                               'degree_' + str(d_this): 'degree'}
            column_select = ['user', 'if_move',
                             'degree_' + str(d_this),
                             'information_diff_' + str(d_this),
                             'support_diff_' + str(d_this),
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
    column_name = ['user', 'if_move', 'degree', 'information_diff', 'support_diff',
                   'date', 't',
                   'home', 'dest']
    regression_all = pd.DataFrame(columns=column_name)
    users['t'] = 'r'
    users.loc[users['home'] == 11, 't'] = 'u'

    users_move = users[users.type.isin([1, 2, 5])]
    users_remain = users[~(users.type.isin([1, 2, 5]))]

    column_select = ['user', 'if_move', 'degree_home', 'information_diff_home', 'support_diff_home',
                     'date', 't', 'home', 'dest']
    column_new_name = {'information_diff_home': 'information_diff',
                       'support_diff_home': 'support_diff',
                       'degree_home': 'degree'}
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

    freeze_month_n = int(sys.argv[1])
    compare_month_n = int(sys.argv[2])
    if_same_home = 'No'
    IF_ONLY_REMAIN = True
    date = start_date.strftime('%Y%m') + '-' + end_date.strftime('%Y%m')

    for i in range(loop_num):
        t2 = start_date + relativedelta(months=i)
        t2_str = t2.strftime('%Y%m')[2:]
        network_file_2 = 'data/user_result_information_support_diff_if_remained_' + str(IF_ONLY_REMAIN) + '_' +t2_str+'_between_'+str(freeze_month_n) +'_to_' + str(compare_month_n) + '_months.csv'
        users_2 = pd.read_csv(network_file_2, sep=',')
        users_2['date'] = [t2_str] * len(users_2)
        if i == 0:
            users = users_2
        else:
            users = users.append(users_2)
        print(t2)

    # make sure home in -6month = home in -2month
    if if_same_home == 'Yes':
        users = users[users['home'] == users['home_'+str(freeze_month_n)+'month']]

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
    users = users[~((users.home == 32) | (users.dest == 32))]

    # convert nan to 0 for degree and information
    for v in ['degree', 'information_diff', 'support_diff']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)
        users[v + '_home'] = users[v + '_home'].fillna(value=0)

    if_fix = True
    column_select = ['user', 'if_move',
                     'degree',
                     'information_diff',
                     'support_diff',
                     't', 'date',
                     'home', 'dest']
    # destination
    a = to_dest(users, dist, if_fix)
    dest = a[column_select]

    # home
    b = from_home(users, if_fix)
    home = b[column_select]

    # merge home and destination (for pull and push regression)
    dest.columns = ['user', 'if_move', 'degree_dest', 'information_diff_dest', 'support_diff_dest',
                    't_dest', 'date', 'home_dest', 'dest_dest']
    home.columns = ['user', 'if_move', 'degree_home', 'information_diff_home', 'support_diff_home',
                    't_home', 'date', 'home_home', 'dest_home']

    dest_home = dest.merge(home, on=['user', 'date'], how='inner')
    dest_home.to_csv('data/dest_home_for_regression_information_support_diff_between_'+str(freeze_month_n) +'_to_' + str(compare_month_n) + '_month.csv', index=None)