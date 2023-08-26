import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


####### in Jan 2008  #######
num_lines = sum(1 for line in open('data/0801_call.txt'))
# Number of CDR transactions
print(num_lines)
net_result_0801 = pd.read_csv('data/0801_user_result.csv')
# Number of unique individuals
print(len(list(net_result_0801['user'].unique())))
# Number of migrants
migrants_0801 = net_result_0801[net_result_0801['type'].isin([1, 2, 5])]
print(len(migrants_0801))
# Number of migrants by urban/rural breakdown
print(migrants_0801.groupby('type').size())


####### over two years: July 2006 - June 2008 #######
start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

num_lines = 0
net_results = []
for i in range(loop_num):
    network_date = start_date + relativedelta(months=i)
    network_date = network_date.strftime('%Y%m')[2:]
    num_lines += sum(1 for line in open('data/' + network_date + '_call.txt'))
    net_result = pd.read_csv('data/' + network_date + '_user_result.csv')
    print(i)
    net_results.append(net_result)

all_users = pd.concat(net_results)

# Number of CDR transactions
print(num_lines)
# Number of unique individuals
print(len(all_users['user'].unique()))
# Number of migrants
migrants = all_users[all_users['type'].isin([1, 2, 5])]
print(len(migrants))
# Number of migrants by urban/rural breakdown
print(migrants.groupby('type').size())

