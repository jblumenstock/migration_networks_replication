import pandas as pd


df = SFrame.read_csv('data/dest_home_d_s_l.csv')
adjacent_dist = pd.read_csv('data/neighbor_district.csv')

adj_dist_dict = {}
for idx, row in adjacent_dist.iterrows():
    d1 = int(row['Dist_ID'])
    d2 = row['NEIGHBORS']
    d2 = [int(x) for x in d2.split(',')]
    adj_dist_dict[d1] = d2


def if_neighbor(x):
    h = x['home_dest']
    d = x['dest_dest']
    if d in adj_dist_dict[h]:
        return 1
    else:
        return 0


df['if_neighbor'] = df.apply(lambda x: if_neighbor(x))
df.export_csv('data/dest_home_d_s_l_adjacent.csv')