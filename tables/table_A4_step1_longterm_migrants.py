import pandas as pd
import numpy as np
from graphlab import SFrame
from datetime import datetime
from dateutil.relativedelta import relativedelta


def if_longterm_migrant(x, i):
    next_12_month = ['district.' + str(n) for n in range(i + 2, i + 13)]
    district_all = []
    a = migration_file_all[migration_file_all['user'] == x['id']].head(1)
    for n in next_12_month:
        if a[n][0] != None:
            district_all.append(a[n][0])
    if len(list(set(district_all))) != 1:
        return 0
    else:
        return 1


def if_shortterm_migrant(x, i):
    next_6_month = ['district.' + str(n) for n in range(i + 2, i + 7)]
    district_all = []
    a = migration_file_all[migration_file_all['user'] == x['id']].head(1)
    for n in next_6_month:
        if a[n][0] != None:
            district_all.append(a[n][0])
    if len(list(set(district_all))) != 1:
        return 1
    else:
        return 0

start_date = datetime.strptime('2006 1', '%Y %m')
end_date = datetime.strptime('2009 1', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    migration_file = SFrame.read_csv('data/' + data_date + '_modal_district.txt', delimiter='\t', header=False)
    migration_file.rename({'X1': 'user_time', 'X2':'district'})
    a = migration_file.flat_map(['user_time'], lambda x: [[x['user_time'].split('_')[0]]])
    migration_file = migration_file.add_column(a['user_time'], name='user')[['user', 'district']]
    if i > 0:
        migration_file_all = migration_file_all.join(migration_file, on={'user': 'user'}, how='outer')
    else:
        migration_file_all = migration_file
migration_file_all.rename({'district': 'district.0'})

start_date = datetime.strptime('2006 2', '%Y %m')
end_date = datetime.strptime('2008 1', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    migration_file = SFrame.read_csv('data/' + data_date + '_migration.txt')
    migrants = migration_file.filter_by([1, 2, 5], 'type')
    migrants['if_longterm'] = migrants.apply(lambda x: if_longterm_migrant(x, i))
    migrants['if_shortterm'] = migrants.apply(lambda x: if_shortterm_migrant(x, i))
    print(i)
    if i == 0:
        tmp = migration_file_all.filter_by(migrants[migrants['if_longterm'] == 1]['id'], 'user')
        tmp['date'] = [data_date] * len(tmp)
        result_longterm = tmp
        tmp = migration_file_all.filter_by(migrants[migrants['if_shortterm'] == 1]['id'], 'user')
        tmp['date'] = [data_date] * len(tmp)
        result_tmp = tmp
    else:
        tmp = migration_file_all.filter_by(migrants[migrants['if_longterm'] == 1]['id'], 'user')
        tmp['date'] = [data_date] * len(tmp)
        result_longterm = result_longterm.append(tmp)
        tmp = migration_file_all.filter_by(migrants[migrants['if_shortterm'] == 1]['id'], 'user')
        tmp['date'] = [data_date] * len(tmp)
        result_tmp = result_tmp.append(tmp)


for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    result_this_month = list(result_longterm[result_longterm['date'] == data_date]['user'])
    print(len(result_this_month))
    with open('data/' + data_date + '_migration_longterm.csv', 'w') as f:
        f.write('uesr\n')
        for x in result_this_month:
            f.write(x + '\n')

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    result_this_month = list(result_tmp[result_tmp['date'] == data_date]['user'])
    print(len(result_this_month))
    with open('data/' + data_date + '_migration_shortterm.csv', 'w') as f:
        f.write('uesr\n')
        for x in result_this_month:
            f.write(x + '\n')