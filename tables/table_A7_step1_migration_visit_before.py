import pandas as pd
import numpy as np
from graphlab import SArray, SFrame, aggregate as agg
import random
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

random.seed(0)


def get_net(network_date, u):
    network_file = 'data/' + network_date + '_call.txt'
    conn_raw = SFrame.read_csv(network_file, delimiter='|', header=False, verbose=False)['X1', 'X2', 'X3', 'X4', 'X6', 'X8']
    conn_raw.rename({'X1': 'user_1', 'X2': 'user_2', 'X3': 'date', 'X4': 'time', 'X6':'user_1_cell', 'X8':'user_2_cell'})
    conn_raw['hour'] = conn_raw.apply(lambda x: int(x['time'].split(':')[0]))
    u1 = conn_raw[['user_1', 'user_1_cell', 'date', 'hour']]
    u2 = conn_raw[['user_2', 'user_2_cell', 'date', 'hour']]
    u2.rename({'user_2': 'user_1',
                'user_2_cell': 'user_1_cell'})
    u_all = u1.append(u2)
    u_all = u_all.filter_by(u['id'], 'user_1')
    u_all1 = u_all.unique()
    u_all1 = u_all1.filter_by(towers.keys(), 'user_1_cell')
    u_all1['district'] = u_all1.apply(lambda x: towers[x['user_1_cell']])
    u_all2 = u_all1[['user_1', 'date', 'district']].unique()
    u_all2.rename({'user_1': 'user'})
    u_all2_night = u_all1[(u_all1['hour'] >= 18) | (u_all1['hour'] <= 7)]
    u_all2_night = u_all2_night[['user_1', 'date', 'district']].unique()
    u_all2_night.rename({'user_1': 'user'})
    return u_all2, u_all2_night


def if_visit(x, loc_hist):
    u = x['id']
    dest = x['dest']
    loc_ = loc_hist.filter_by(u, 'user')
    loc_ = loc_.filter_by(dest, 'district')
    return len(loc_)


start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

tower_file = "data/tower_district.csv"
towers = {}
with open(tower_file) as t:
    t.readline()
    for line in t:
        line = line.split(',')
        tower_key = int(line[0])
        towers[tower_key] = int(line[6])

migration_file_name = 'data/0801_migration.txt'
users = SFrame.read_csv(migration_file_name, usecols=['id', 'type', 'home', 'dest'])
dists = list(users['home'].unique())

for i in xrange(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    network_date = start_date + relativedelta(months=i - 1)
    network_date = network_date.strftime('%Y%m')[2:]

    # assign migration info to connection
    migration_file_name = 'data/' + data_date + '_migration.txt'
    users = SFrame.read_csv(migration_file_name, usecols=['id', 'type', 'home', 'dest'])
    users = users[users['type'] != 6]
    _u = []
    _dist = []
    for i in users['id']:
        for j in dists:
            _u.append(i)
            _dist.append(j)

    loc, loc_night = get_net(network_date, users)
    df = SFrame(data={'id': _u, 'dist': _dist})
    b = loc.groupby(['user', 'district'], {'num_visit_dest_before_migration': agg.COUNT()})
    a = df.join(b, on={'id': 'user', 'dist': 'district'}, how='left')
    a = a.fillna('num_visit_dest_before_migration', 0)
    a_df = a.to_dataframe()
    a_df_pivot = a_df.pivot(index='id', columns='dist', values='num_visit_dest_before_migration')
    a_df_pivot = a_df_pivot.rename(columns={'id': 'user'})
    a_df_pivot = a_df_pivot.reset_index()
    new_col = {}
    for i in dists:
        new_col[i] = 'if_visit_' + str(i)
    a_df_pivot = a_df_pivot.rename(columns=new_col)

    df = SFrame(data={'id': _u, 'dist': _dist})
    b_night = loc_night.groupby(['user', 'district'], {'num_visit_dest_before_migration_night': agg.COUNT()})
    a = df.join(b_night, on={'id': 'user', 'dist': 'district'}, how='left')
    a = a.fillna('num_visit_dest_before_migration_night', 0)
    a_df = a.to_dataframe()
    a_df_pivot_night = a_df.pivot(index='id', columns='dist', values='num_visit_dest_before_migration_night')
    a_df_pivot_night = a_df_pivot_night.rename(columns={'id': 'user'})
    a_df_pivot_night = a_df_pivot_night.reset_index()
    new_col = {}
    for i in dists:
        new_col[i] = 'if_visit_night_' + str(i)
    a_df_pivot_night = a_df_pivot_night.rename(columns=new_col)
    print(a_df_pivot.shape, a_df_pivot_night.shape)
    a_df_pivot = a_df_pivot.merge(a_df_pivot_night, left_on='id', right_on='id', how='inner')
    print(a_df_pivot.shape)
    a_df_pivot.to_csv('data/' + network_date + '_migrant_if_visit_before.csv', index=None)
    print(network_date)
