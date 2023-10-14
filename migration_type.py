from datetime import datetime
from dateutil.relativedelta import relativedelta

start_date = datetime.strptime('2006 7','%Y %m')
end_date = datetime.strptime('2008 6','%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

def migration_type(user, d2, d3, d4, d5):
    district = '11'
    if d2 == d3 and d3 == d4 and d4 == d5:
        if d2 == district:
            return [user, '3', d2, d4, d2, d3, d4, d5] # user, home, destination
        else:
            return [user, '4', d2, d4, d2, d3, d4, d5]
    elif d2 == d3 and d4 == d5 and d3 != d4:
        if d2 == district:
            return [user, '2', d2, d4, d2, d3, d4, d5]
        elif d4 == district:
            return [user, '1', d2, d4, d2, d3, d4, d5]
        else:
            return [user, '5', d2, d4, d2, d3, d4, d5]
    else:
        return [user, '6', d2, d4, d2, d3, d4, d5] # roamer has no home and destination.

modal_district_dir = 'data/'
for i in range(loop_num):
    t2 = start_date + relativedelta(months=i)
    t2_str = t2.strftime('%Y%m')[2:]
    t1 = t2 + relativedelta(months=-1)
    t1_str = t1.strftime('%Y%m')[2:]
    t3 = t2 + relativedelta(months=1)
    t3_str = t3.strftime('%Y%m')[2:]
    t4 = t2 + relativedelta(months=2)
    t4_str = t4.strftime('%Y%m')[2:]

    text_2 = sc.textFile(modal_district_dir + t1_str+'_modal_district.txt', use_unicode=False)
    text_split_2 = text_2.map(lambda line: line.split('\t'))
    d2 = text_split_2.map(lambda line: (line[0].split('_')[0], line[1]))

    text_3 = sc.textFile(modal_district_dir + t2_str+'_modal_district.txt', use_unicode=False)
    text_split_3 = text_3.map(lambda line: line.split('\t'))
    d3 = text_split_3.map(lambda line: (line[0].split('_')[0], line[1]))

    text_4 = sc.textFile(modal_district_dir + t3_str+'_modal_district.txt', use_unicode=False)
    text_split_4 = text_4.map(lambda line: line.split('\t'))
    d4 = text_split_4.map(lambda line: (line[0].split('_')[0], line[1]))

    text_5 = sc.textFile(modal_district_dir + t4_str+'_modal_district.txt', use_unicode=False)
    text_split_5 = text_5.map(lambda line: line.split('\t'))
    d5 = text_split_5.map(lambda line: (line[0].split('_')[0], line[1]))

    t1 = d2.join(d3).join(d4).join(d5)

    t2 = t1.map(lambda line:(line[0], line[1][0][0][0], line[1][0][0][1], line[1][0][1], line[1][1]))

    t3 = t2.map(lambda line: migration_type(line[0], line[1], line[2], line[3], line[4]))

    output_file = open(modal_district_dir + t2_str + '_migration.txt', 'w')
    output_file.write('id,type,home,dest,d1,d2,d3,d4\n')
    result = sorted(t3.collect())
    for i in result:
        output_file.write(i[0]+','+i[1]+','+i[2]+','+i[3]+','+i[4]+','+i[5]+','+i[6]+','+i[7]+'\n')
    output_file.close()
