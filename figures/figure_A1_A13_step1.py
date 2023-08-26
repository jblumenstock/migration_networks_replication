import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 2 month version 
start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

result = []
for i in range(loop_num):
    network_date = start_date + relativedelta(months=i)
    network_date = network_date.strftime('%Y%m')[2:]
    migration_result = pd.read_csv('data/' + network_date + '_migration.txt')
    migration_result = migration_result[migration_result['type'].isin([1, 2, 5])]
    _df = migration_result.groupby(['home', 'dest']).size().reset_index(name='num')
    print(i)
    print(_df.shape)
    result.append(_df)

final = pd.concat(result)
dest = final.groupby('dest', as_index=False)['num'].sum()
home = final.groupby('home', as_index=False)['num'].sum()

dest.to_csv('data/cdr_move_to_district_proportion_2month.csv', index=None)
home.to_csv('data/cdr_move_from_district_proportion_2month.csv', index=None)

# 6 month version
start_date = datetime.strptime('2006 6', '%Y %m')
end_date = datetime.strptime('2008 5', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

result = []
for i in range(loop_num):
    network_date = start_date + relativedelta(months=i)
    network_date = network_date.strftime('%Y%m')[2:]
    migration_result = pd.read_csv('data/' + network_date + '_migration_6month.txt')
    migration_result = migration_result[migration_result['type'].isin([1, 2, 5])]
    _df = migration_result.groupby(['home', 'dest']).size().reset_index(name='num')
    print(i)
    print(_df.shape)
    result.append(_df)

final = pd.concat(result)
dest = final.groupby('dest', as_index=False)['num'].sum()
home = final.groupby('home', as_index=False)['num'].sum()

dest.to_csv('data/cdr_move_to_district_proportion_6month.csv', index=None)
home.to_csv('data/cdr_move_from_district_proportion_6month.csv', index=None)

# 12 month version
start_date = datetime.strptime('2006 6', '%Y %m')
end_date = datetime.strptime('2008 5', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

result = []
for i in range(loop_num):
    network_date = start_date + relativedelta(months=i)
    network_date = network_date.strftime('%Y%m')[2:]
    migration_result = pd.read_csv('data/' + network_date + '_migration_12month.txt')
    migration_result = migration_result[migration_result['type'].isin([1, 2, 5])]
    _df = migration_result.groupby(['home', 'dest']).size().reset_index(name='num')
    print(i)
    print(_df.shape)
    result.append(_df)

final = pd.concat(result)
dest = final.groupby('dest', as_index=False)['num'].sum()
home = final.groupby('home', as_index=False)['num'].sum()

dest.to_csv('data/cdr_move_to_district_proportion_12month.csv', index=None)
home.to_csv('data/cdr_move_from_district_proportion_12month.csv', index=None)