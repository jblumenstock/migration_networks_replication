from datetime import datetime
from dateutil.relativedelta import relativedelta


def if_night(t):
	h = int(t.split(':')[0])
	if h >= 18 or h <=7:
		return True
	else:
		return False

# format data
def hour_modal_tower(line, number):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2] + '_' + line[3] + '_' + line[4], number)

# format data
def hour_modal_tower_1(line, number):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2] + '_' + line[3] + '_' + line[4] + '_' + str(number))

# format data: id_year_month_day_tower
# from today 18:00 - 24:00 to tomorrow 0:00 - 7:00 => as today's location
def daily_modal_tower_1(v1):
	v1_split = v1.split('_')
	hour = int(v1_split[2])
	if hour >= 18:
		return (v1_split[0] + '_' + v1_split[1][:2] + '_' + v1_split[1][2:4] + '_' + v1_split[1][4:6] + '_' + v1_split[3])
	#if hour is within 0:00 - 7:00, it is the previous day according to the algorithm
	else:
		if int(v1_split[1][4:6]) > 10:
			return (v1_split[0] + '_' + v1_split[1][:2] + '_' + v1_split[1][2:4] + '_' + str(int(v1_split[1][4:6])-1) + '_' + v1_split[3])
		else:
			return (v1_split[0] + '_' + v1_split[1][:2] + '_' + v1_split[1][2:4] + '_0' + str(int(v1_split[1][4:6])-1) + '_' + v1_split[3])

def daily_modal_tower_1_2(v1):
	v1_split = v1.split('_')
	hour = int(v1_split[2])
	if hour >= 18:
		return (v1_split[0] + '_' + v1_split[1][:2] + '_' + v1_split[1][2:4] + '_' + v1_split[1][4:6] + '_' + v1_split[2] + '_' + v1_split[3])
	#if hour is within 0:00 - 7:00, it is the previous day according to the algorithm
	else:
		if int(v1_split[1][4:6]) > 10:
			return (v1_split[0] + '_' + v1_split[1][:2] + '_' + v1_split[1][2:4] + '_' + str(int(v1_split[1][4:6])-1) + '_' + v1_split[2] + '_' + v1_split[3])
		else:
			return (v1_split[0] + '_' + v1_split[1][:2] + '_' + v1_split[1][2:4] + '_0' + str(int(v1_split[1][4:6])-1) + '_' + v1_split[2] + '_' + v1_split[3])

def daily_modal_tower_1_3(line, dist):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2] + '_' + line[3] + '_' + dist)

def daily_modal_tower_2(line, number):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2] + '_' + line[3], number)

def daily_modal_tower_3(line, number):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2] + '_' + line[3] + '_' + str(number))

def daily_modal_tower_3_2(line, number):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2] + '_' + str(number))

def monthly_modal_tower_1(v1, v2):
	v1_split = v1.split('_')
	return (v1_split[0] + '_' + v1_split[1] + '_' + v1_split[2] + '_' + v2)

def monthly_modal_tower_2(line, number):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2], number)

def monthly_modal_tower_3(line, number):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2] + '_' + str(number))

def monthly_modal_tower_4(line):
	line = line.split('_')
	return (line[0] + '_' + line[1] + '_' + line[2])

def tower_to_district(v1, v2, towers):
	if int(v2) in towers.keys():
		return (v1, towers[int(v2)])

def get_one_dist_hour(v1, v2):
    if len(v2) == 1:
        return (v1, v2[0])
    else:
        # first use daily all modal
        v1_split = v1.split('_')
        num = {} 
        for i in v2:
            v = v1_split[0] + '_' +v1_split[1] + '_' +v1_split[2] + '_' +v1_split[3] + '_' +i
            n1 = daily_all_tower_sc.value[v]
            num[v] = n1
        values = sorted(num.values())
        if values[-1] != values [-2]:
            for x, y in num.iteritems():
                if y == values[-1]:
                    return (v1, x.split('_')[-1])
        else:
            # if daily all modal cannot solve, then use month all modal
            v2_new = []
            for x, y in num.iteritems():
                if y == values[-1]:
                    v2_new.append(int(x.split('_')[-1]))
            num = {}
            for i in v2_new:
                v = v1_split[0] + '_' +v1_split[1] + '_' +v1_split[2] + '_' +str(i)
                n1 = monthly_all_tower_sc.value[v]
                num[v] = n1
            values = sorted(num.values())
            if values[-1] != values [-2]:
                for x, y in num.iteritems():
                    if y == values[-1]:
                        return (v1, x.split('_')[-1])
            else:
                return (v1,None)

def get_one_dist_day(v1, v2):
    if len(v2) == 1:
        return (v1, v2[0])
    else:
        # first use daily all modal
        v1_split = v1.split('_')
        num = {} 
        for i in v2:
            v = v1_split[0] + '_' +v1_split[1] + '_' +v1_split[2] + '_' +v1_split[3] + '_'+ str(int(i))
            n1 = daily_all_tower_sc.value[v]
            num[v] = n1
        values = sorted(num.values())
        if values[-1] != values [-2]:
            for x, y in num.iteritems():
                if y == values[-1]:
                    return (v1, x.split('_')[-1])
        else:
            # if daily all modal cannot solve, then use month all modal
            v2_new = []
            for x, y in num.iteritems():
                if y == values[-1]:
                    v2_new.append(int(x.split('_')[-1]))
            num = {} 
            for i in v2_new:
                v = v1_split[0] + '_' +v1_split[1] + '_' +v1_split[2] + '_' +str(int(i))
                n1 = monthly_all_tower_sc.value[v]
                num[v] = n1
            values = sorted(num.values())
            if values[-1] != values [-2]:
                for x, y in num.iteritems():
                    if y == values[-1]:
                        return (v1, x.split('_')[-1])
            else:
                return (v1,None)

def get_one_dist_month(v1, v2):
    if len(v2) == 1:
        return (v1, v2[0])
    else:
        # first use daily all modal
        v1_split = v1.split('_')
        num = {} 
        for i in v2:
            v = v1_split[0] + '_' +v1_split[1] + '_' +v1_split[2] + '_' +i
            n1 = monthly_all_tower_sc.value[v]
            num[v] = n1
        values = sorted(num.values())
        if values[-1] != values [-2]:
            for x, y in num.iteritems():
                if y == values[-1]:
                    return (v1, x.split('_')[-1])
        else:
            return (v1,None)

if __name__ == "__main__":
    tower_file = "data/tower_district.csv"
    towers = {}
    with open(tower_file) as t:
            t.readline()
            for line in t:
                    line = line.split(',')
                    if int(line[0]) < 10:
                            tower_key = '00' + line[0]
                    elif int(line[0]) < 100:
                            tower_key = '0' + line[0]
                    else:
                            tower_key = line[0]
                    towers[tower_key] = line[6]  # 11 belong to Kigali

    start_date = datetime.strptime('2007 2', '%Y %m')
    end_date = datetime.strptime('2008 6', '%Y %m')
    loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

    for i in range(loop_num):
        date_ = start_date + relativedelta(months=i)
        date_str = date_.strftime('%Y%m')[2:]
        input_file = date_str + '_mobility.txt'
        text = sc.textFile("data/" + input_file, use_unicode=False)
        text_split = text.map(lambda line: line.split('|'))

        record_night = text_split.filter(lambda line: if_night(line[2]))
        record_night_2 = record_night.filter(lambda line: line[1][:4] == input_file[:4]) # find 060301 record in 0602 mobility file, remove this
        record_night_tower_exist = record_night_2.filter(lambda line: line[3] in towers.keys()) # some towers do not exsit in Tower2.csv file. just delete it.

        # get all daily district not based on hour. this is used to choose hour tie
        daily_all_tower = record_night_tower_exist.map(lambda line: (daily_modal_tower_1(line[0] + '_' + line[1] + '_' + line[2].split(':')[0] + '_' + towers[line[3]]), 1)).reduceByKey(lambda a, b: a+b)
        daily_all_tower_dict = {}
        for i in daily_all_tower.collect():
                daily_all_tower_dict[i[0]] = i[1]

        daily_all_tower_sc = sc.broadcast(daily_all_tower_dict)

        # get all monthly district not based on day.
        monthly_all_tower = record_night_tower_exist.map(lambda line: (line[0] + '_' + line[1][:2] +'_' + line[1][2:4] + '_' + towers[line[3]], 1)).reduceByKey(lambda a, b: a+b)
        monthly_all_tower_dict = {}
        for i in monthly_all_tower.collect():
                monthly_all_tower_dict[i[0]] = i[1]

        monthly_all_tower_sc = sc.broadcast(monthly_all_tower_dict)

        #===========================
        ## calculate hourly modal tower
        # select all the records at night 
        hour_tower_1 = record_night_tower_exist.map(lambda line: (daily_modal_tower_1_2(line[0] + '_' + line[1] + '_' + line[2].split(':')[0] + '_' + towers[line[3]]), 1)).reduceByKey(lambda a, b: a+b)
        hour_tower_2 = hour_tower_1.map(lambda line: hour_modal_tower(line[0], line[1])).reduceByKey(lambda a, b: a if (a > b) else b)
        a = hour_tower_1.map(lambda line: (hour_modal_tower_1(line[0], line[1]),line[0].split('_')[5]))
        b = hour_tower_2.map(lambda line: (hour_modal_tower_1(line[0], line[1]), 1))
        hour_tower_3 = a.join(b)
        hour_tower_4 = hour_tower_3.map(lambda line: (line[0], line[1][0])).groupByKey().map(lambda x : (x[0], list(x[1])))
        hour_tower_5 = hour_tower_4.map(lambda line: get_one_dist_hour(line[0], line[1]))
        hour_tower_6 = hour_tower_5.filter(lambda line: line[1] != None)

        daily_tower_1 = hour_tower_6.map(lambda line: (daily_modal_tower_1_3(line[0],line[1]), 1)).reduceByKey(lambda a, b: a+b)
        daily_tower_2 = daily_tower_1.map(lambda line: daily_modal_tower_2(line[0], line[1])).reduceByKey(lambda a, b: a if (a > b) else b)

        d1 = daily_tower_1.map(lambda line: (daily_modal_tower_3(line[0], line[1]), line[0].split('_')[4]))
        d2 = daily_tower_2.map(lambda line: (daily_modal_tower_3(line[0], line[1]), 1))
        daily_tower_3 = d1.join(d2)

        daily_tower_4 = daily_tower_3.map(lambda line: (line[0], line[1][0])).groupByKey().map(lambda x: (x[0], list(x[1])))
        daily_tower_5 = daily_tower_4.map(lambda line: get_one_dist_day(line[0], line[1]))
        daily_tower_6 = daily_tower_5.filter(lambda line: line[1] != None)

        #==========================
        ## calculate monthly modal tower
        monthly_tower_1 = daily_tower_6.map(lambda line: (monthly_modal_tower_1(line[0], line[1]), 1)).reduceByKey(lambda a, b: a+b)
        monthly_tower_2 = monthly_tower_1.map(lambda line: monthly_modal_tower_2(line[0], line[1])).reduceByKey(lambda a, b: a if (a > b) else b)

        m1 = monthly_tower_1.map(lambda line: (monthly_modal_tower_3(line[0], line[1]), line[0].split('_')[3]))
        m2 = monthly_tower_2.map(lambda line: (monthly_modal_tower_3(line[0], line[1]), 1))
        monthly_tower_3 = m1.join(m2)
        monthly_tower_4 = monthly_tower_3.map(lambda line: (line[0], line[1][0])).groupByKey().map(lambda x: (x[0], list(x[1])))
        monthly_tower_5 = monthly_tower_4.map(lambda line: get_one_dist_month(line[0], line[1]))
        monthly_tower_6 = monthly_tower_5.filter(lambda line: line[1] != None)

        result = sorted(monthly_tower_6.collect())
        output_file = open("data/" + input_file[:4] + '_modal_district.txt','w')
        for i in result:
            if i != None:
                output_file.write(i[0]+'\t'+i[1]+'\n')

        output_file.close()


