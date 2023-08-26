import pandas as pd
import numpy as np
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def to_dest(users, districts_analyze, if_fix):
    column_name = ['user', 'if_move', 'd', 'l', 's',
                   'date', 't',
                   'home', 'dest',
                   'permanent', 'temporary']
    # 't' is migration type
    # we don't need this for regression
    # leave 't' here as 'placeholder'
    regression_all = pd.DataFrame(columns=column_name)
    for d_this in districts_analyze:
        users_this = users
        users_this['t'] = 'placeholder'

        users_moveto = users_this[users_this.dest == d_this]
        users_remain = users_this[users_this.dest != d_this]

        #  fix degree
        if if_fix:
            users_moveto['if_move'] = [1] * len(users_moveto)
            users_remain['if_move'] = [0] * len(users_remain)
            column_new_name = {'s_' + str(d_this): 's',
                               'l_' + str(d_this): 'l',
                               'd_' + str(d_this): 'd'}
            column_select = ['user', 'if_move',
                             'd_' + str(d_this),
                             'l_' + str(d_this),
                             's_' + str(d_this),
                             'date', 't',
                             'home', 'dest',
                             'permanent', 'temporary']
            users_moveto = users_moveto[column_select]
            users_moveto.rename(columns=column_new_name, inplace=True)

            # at this step, 'dest' is the possible destination
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

    for i in range(loop_num):
        t2 = start_date + relativedelta(months=i)
        t2_str = t2.strftime('%Y%m')[2:]
        network_file_2 = 'data/' + t2_str + '_user_result.csv'
        users_2 = pd.read_csv(network_file_2, sep=',')
        users_2['date'] = [t2_str] * len(users_2)
        # permanent vs temporary is different from first vs repeat
        # if a user is not first time, then she is repeat
        # permanent is >=12, temporary is <=6. others are 6< <12
        # permanent is long-term
        # temporary is short-term
        # note: only migrants can be permanent or temporary
        # remains are neither permanent nor temporary
        permanent = pd.read_csv('data/' + t2_str + '_migration_longterm.csv')['uesr']
        users_2['permanent'] = 0
        users_2.loc[users_2['user'].isin(permanent), 'permanent'] = 1
        temporary = pd.read_csv('data/' + t2_str + '_migration_shortterm.csv')['uesr']
        users_2['temporary'] = 0
        users_2.loc[users_2['user'].isin(temporary), 'temporary'] = 1
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

    # remove roamers
    users = users[users.type != 6]

    # convert nan to 0 for degree and information
    for v in ['d', 'l', 's']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)

    if_fix = True
    column_select = ['user', 'if_move',
                     'd', 'l', 's',
                     't', 'date',
                     'home', 'dest',
                     'permanent', 'temporary']
    # destination
    a = to_dest(users, dist, if_fix)
    dest = a[column_select]
    dest.to_csv('data/dest_home_d_s_l_shorttime_longtime.csv', index=False)
