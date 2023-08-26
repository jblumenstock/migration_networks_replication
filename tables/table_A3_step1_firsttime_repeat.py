import pandas as pd
import numpy as np
from itertools import groupby
from turicreate import SFrame
import turicreate
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


turicreate.config.set_runtime_config('TURI_DEFAULT_NUM_PYLAMBDA_WORKERS', 40)

# type
# - 1: repeat migrant
# - 2: repeat non-migrant
# - 3: firsttime migrant
# - 4: firsttime non-migrant
def if_firsttime(x, dest):
    u = x['user']
    t = x['type']
    u_home = int(x['home'])
    u_dest_raw = int(x['dest_raw'])
    this_data = datetime.strptime('20' + x['date'][:2] + x['date'][-2:], '%Y%m')
    u_hist = []
    for i in range(-12, 0):
        date_ = this_data + relativedelta(months=i)
        data_date = date_.strftime('%Y%m')[2:]
        if u in loc_history:
            if data_date in loc_history[u]:
                u_hist.append(loc_history[u][data_date])
    # repeat
    repeat = 0
    for h, d in u_hist:
        if h == u_home and d == dest:
            repeat = 1
            break

    return repeat


def to_dest(users, districts_analyze):
    regression_all = pd.DataFrame(columns=column_name)
    for d_this in districts_analyze:
        users_this = users
        users_this['dest'] = d_this
        users_this = SFrame(data=users_this)
        users_this['if_repeat'] = users_this.apply(lambda x: if_firsttime(x, d_this))
        regression_all = regression_all.append(users_this[column_name].to_dataframe())
        print(d_this)
    return regression_all


if __name__ == '__main__':
    start_date = datetime.strptime('2005 7', '%Y %m')
    end_date = datetime.strptime('2008 6', '%Y %m')
    start_date_str = start_date.strftime('%Y%m')[2:]
    end_date_str = end_date.strftime('%Y%m')[2:]
    loop_num = (relativedelta(end_date, start_date).months
                + 12 * relativedelta(end_date, start_date).years
                + 1)

    date = start_date.strftime('%Y%m') + '-' + end_date.strftime('%Y%m')

    loc_history = {}
    for i in range(loop_num):
        date_ = start_date + relativedelta(months=i)
        data_date = date_.strftime('%Y%m')[2:]
        migration_file = 'data/' + data_date + '_migration.txt'
        migration = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]
        migration = migration[migration.type != 6]
        for idx, row in migration.iterrows():
            u = row['id']
            if u in loc_history:
                loc_history[u][data_date] = [int(row['home']), int(row['dest'])]
            else:
                loc_history[u] = {data_date: [int(row['home']), int(row['dest'])]}


    start_date = datetime.strptime('2006 7', '%Y %m')
    end_date = datetime.strptime('2008 6', '%Y %m')
    start_date_str = start_date.strftime('%Y%m')[2:]
    end_date_str = end_date.strftime('%Y%m')[2:]
    loop_num = (relativedelta(end_date, start_date).months
                + 12 * relativedelta(end_date, start_date).years
                + 1)
    # Different from other generating regression data,
    # for this heterogeneity (first-time vs repeat, short-term vs long-term),
    # we need to do it month by month.
    # But for urban vs rural, adjacent vs non-adjacent,
    # we can directly calculate it for all months
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
    users['dest_raw'] = users['dest'].tolist()
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
    for v in ['d', 'l', 'conn_weight']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)

    column_name = ['user',
                   'date',
                   'home', 'dest',
                   'if_repeat']
    # destination
    a = to_dest(users, dist)
    dest = a[column_name]
    covariates = pd.read_csv('data/dest_home_d_s_l.csv')

    result = covariates.merge(dest, left_on=['user', 'date', 'home_dest', 'dest_dest'], right_on=['user', 'date', 'home', 'dest'], how='inner')
    result.to_csv('dest_home_d_s_l_firsttime_repeat.csv', index=False)
