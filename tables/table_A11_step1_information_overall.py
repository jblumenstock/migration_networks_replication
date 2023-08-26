import pandas as pd
import numpy as np
from graphlab import SArray, SFrame, SGraph, aggregate as agg, degree_counting
import random
from snap import *
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

random.seed(0)


def get_user_order(user_1, user_2):
    if user_1 > user_2:
        return [user_2, user_1]
    elif user_1 == user_2:
        return ['None', 'None']
    else:
        return [user_1, user_2]


def get_outlier(user, degree, thre):
    if degree >= thre:
        return user
    else:
        return 'None'


start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    network_date = start_date + relativedelta(months=i - 1)
    network_date = network_date.strftime('%Y%m')[2:]

    conn_base = SFrame.read_csv('data/' + network_date + '_call.txt', delimiter='|', header=False)['X1', 'X2']
    conn_base.rename({'X1': 'user_1', 'X2': 'user_2'})
    conn_order = conn_base.flat_map(['user_1', 'user_2'], lambda x: [get_user_order(x['user_1'], x['user_2'])])
    conn_order = conn_order.filter_by('None', 'user_1', exclude=True)
    conn_base = conn_order.groupby(key_columns=['user_1', 'user_2'], operations={'conn_num': agg.COUNT()})

    # delete users with degree < 95%
    g = SGraph()
    g = g.add_edges(conn_base, src_field='user_1', dst_field='user_2')
    d = degree_counting.create(g)
    g_d = d['graph']
    degree = g_d.vertices['__id', 'total_degree']
    degree.rename({'__id': 'user'})
    degree_sort = degree.sort('total_degree', ascending=False)
    degree_95 = degree_sort.head(len(degree_sort) * 0.05)[-1]['total_degree']
    user_if_outlier = degree.apply(lambda x: get_outlier(x['user'], x['total_degree'], degree_95))
    user_outlier = user_if_outlier.filter(lambda x: x != 'None')
    conn_1 = conn_base.filter_by(user_outlier, 'user_1', exclude=True)
    conn_base = conn_1.filter_by(user_outlier, 'user_2', exclude=True)
    print('remove outliers done')

    users_with_modal_tower_base = SFrame.read_csv('data/' + network_date + '_modal_district.txt', delimiter='\t', header=False)
    users_with_modal_tower_base.rename({'X1': 'user', 'X2': 'home'})
    users_loc_base = users_with_modal_tower_base.flat_map(['user', 'home'], lambda x: [[x['user'].split('_')[0], x['home']]])

    conn_base = conn_base.join(users_loc_base, on={'user_1': 'user'}, how='inner')
    conn_base.rename({'home': 'user_1_home'})
    conn_base = conn_base.join(users_loc_base, on={'user_2': 'user'}, how='inner')
    conn_base.rename({'home': 'user_2_home'})
    conn_base_bidir = conn_base.copy()
    tmp = conn_base.copy()
    tmp.rename({'user_1': 'u2', 'user_2': 'u1',
                'user_1_home': 'u2_home', 'user_2_home': 'u1_home'})
    tmp.rename({'u2': 'user_2', 'u1': 'user_1',
                'u2_home': 'user_2_home', 'u1_home': 'user_1_home'})
    conn_base_bidir = conn_base_bidir.append(tmp)
    del tmp

    tie_loc_base = conn_base_bidir.groupby(['user_1', 'user_2_home'],
                                                 {'friends': agg.CONCAT('user_2')})
    tie_loc_base.rename({'user_2_home': 'loc'})
    tie_loc_base = tie_loc_base.groupby('user_1',
                                              {'friends_loc': agg.CONCAT('loc', 'friends')})
    tie_loc_base.rename({'user_1': 'user'})

    # assign migration info to connection
    migration_file_name = 'data/' + data_date + '_migration.txt'
    users = SFrame.read_csv(migration_file_name, usecols=['id', 'type', 'home', 'dest'])
    dist = list(set(users['home'].unique()) | set(users['dest'].unique()))
    # create result frame
    user_result = pd.DataFrame(columns=['user'])
    user_result['user'] = users['id']
    user_result = SFrame(data=user_result)

    # remove those without connection
    user_base = list(set(conn_base_bidir['user_1'].unique()))
    user_result_final = user_result.filter_by(user_base, 'user')

    # fof all
    edge1 = conn_base_bidir.copy()
    edge1.rename({'user_2': 'user_3',
                  'user_1': 'user_tmp',
                  'user_2_home': 'user_3_home',
                  'user_1_home': 'user_tmp_home'})

    # home information
    edge_fof_home = edge1.join(conn_base_bidir,
                          on={'user_tmp': 'user_2'},
                          how='inner')
    edge_fof_home = edge_fof_home[edge_fof_home['user_1'] != edge_fof_home['user_3']]
    edge_fof_home = edge_fof_home[edge_fof_home['user_1_home'] == edge_fof_home['user_3_home']]

    edge_fof_home_if_1st_frid = edge_fof_home.join(conn_base_bidir, on={'user_1': 'user_1', 'user_3': 'user_2'}, how='left')
    # information cannot come from the first-degree friends
    edge_fof_home_not_1st_frid = edge_fof_home_if_1st_frid[edge_fof_home_if_1st_frid['user_1_home.1'] == None]
    fof_home_case_1 = edge_fof_home_not_1st_frid[edge_fof_home_not_1st_frid['user_1_home'] == edge_fof_home_not_1st_frid['user_2_home']]
    fof_home_case_3 = edge_fof_home_not_1st_frid
    infor_home_1 = fof_home_case_1.groupby('user_1', {'information_home_case_1': agg.COUNT_DISTINCT('user_3')})
    infor_home_1.rename({'user_1': 'user'})
    infor_home_3 = fof_home_case_3.groupby('user_1', {'information_home_case_3': agg.COUNT_DISTINCT('user_3')})
    infor_home_3.rename({'user_1': 'user'})
    infor_home_1_3 = infor_home_1.join(infor_home_3, on='user', how='right')

    # home support
    home_edge = conn_base_bidir[conn_base_bidir['user_1_home'] == conn_base_bidir['user_2_home']]
    home_degree = home_edge.groupby('user_1', {'degree': agg.COUNT()})
    home_degree.rename({'user_1': 'user'})
    edge_support_home = edge_fof_home_if_1st_frid[edge_fof_home_if_1st_frid['user_1_home.1'] != None]
    edge_support_home = edge_support_home.remove_columns(['user_1_home.1', 'user_2_home.1'])
    # i: user_1_home; j: user_tmp_home, k: user_3_home
    support_tie_home_1 = edge_support_home[edge_support_home['user_1_home'] == edge_support_home['user_tmp_home']]
    support_tie_home_3 = edge_support_home
    support_home_1 = support_tie_home_1.groupby('user_1', {'support_tie_home_case_1': agg.COUNT_DISTINCT('user_3')})
    support_home_1.rename({'user_1': 'user'})
    support_home_3 = support_tie_home_3.groupby('user_1', {'support_tie_home_case_3': agg.COUNT_DISTINCT('user_3')})
    support_home_3.rename({'user_1': 'user'})
    support_home_1 = support_home_1.join(home_degree, on='user', how='left')
    support_home_3 = support_home_3.join(home_degree, on='user', how='left')
    support_home_1['support_home_case_1'] = support_home_1['support_tie_home_case_1'] / support_home_1['degree']
    support_home_3['support_home_case_3'] = support_home_3['support_tie_home_case_3'] / support_home_3['degree']
    support_home_1 = support_home_1.remove_columns(['support_tie_home_case_1', 'degree'])
    support_home_3 = support_home_3.remove_columns(['support_tie_home_case_3', 'degree'])
    support_home_1_3 = support_home_1.join(support_home_3, on='user', how='right')

    for i in dist:
        # destination
        edge_with_loc = conn_base_bidir.filter_by(i, 'user_2_home')
        degree_in_loc = edge_with_loc.groupby('user_1', {'degree': agg.COUNT()})
        degree_in_loc.rename({'user_1': 'user'})
        edge_with_loc.rename({'user_2': 'user_at_loc',
                              'user_1': 'u_f',
                              'user_2_home': 'user_at_loc_home',
                              'user_1_home': 'u_f_home'})

        edge_fof = edge_with_loc.join(conn_base_bidir,
                                      on={'u_f': 'user_2'},
                                      how='inner')
        edge_fof = edge_fof[edge_fof['user_1'] != edge_fof['user_at_loc']]
        # information
        # k -> j -> i
        # 1) i:home, j:dest, k:dest
        # 2) i:home, j:home/dest, k:dest
        # 3) i:home, j:anywhere, k:dest
        edge_fof_if_1st_frid = edge_fof.join(edge_with_loc, on={'user_1': 'u_f', 'user_at_loc': 'user_at_loc'}, how='left')
        # information cannot come from the first-degree friends
        edge_fof_not_1st_frid = edge_fof_if_1st_frid[edge_fof_if_1st_frid['user_at_loc_home.1'] == None]
        case_1 = edge_fof_not_1st_frid[edge_fof_not_1st_frid['u_f_home'] == i]
        # case_2_only is the information when j is from home
        case_2_only = edge_fof_not_1st_frid[edge_fof_not_1st_frid['u_f_home'] == edge_fof_not_1st_frid['user_1_home']]
        # case_2 is the information when j is from home/dest
        case_2 = case_2_only.append(case_1)
        # case_3_only is the information when j is from other
        case_3_only = edge_fof_not_1st_frid[(edge_fof_not_1st_frid['u_f_home'] != i) & (edge_fof_not_1st_frid['u_f_home'] != edge_fof_not_1st_frid['user_1_home'])]
        # case_3 is the information when j is anywhere
        case_3 = edge_fof_not_1st_frid
        infor_1 = case_1.groupby('user_1', {'information_dest_case_1_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        infor_1.rename({'user_1': 'user'})
        infor_2_only = case_2_only.groupby('user_1', {'information_dest_case_2_only_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        infor_2_only.rename({'user_1': 'user'})
        infor_2 = case_2.groupby('user_1', {'information_dest_case_2_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        infor_2.rename({'user_1': 'user'})
        infor_3_only = case_3_only.groupby('user_1', {'information_dest_case_3_only_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        infor_3_only.rename({'user_1': 'user'})
        infor_3 = case_3.groupby('user_1', {'information_dest_case_3_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        infor_3.rename({'user_1': 'user'})
        infor = infor_1.join(infor_2, on='user', how='inner')
        infor = infor.join(infor_2_only, on='user', how='left')
        infor = infor.join(infor_3, on='user', how='inner')
        infor = infor.join(infor_3_only, on='user', how='left')
        # home information
        fof_home_case_2_only = edge_fof_home_not_1st_frid.filter_by(i, 'user_2_home')
        fof_home_case_2 = fof_home_case_2_only.append(fof_home_case_1)
        infor_home_2_only = fof_home_case_2_only.groupby('user_1', {'information_home_case_2_only_'+str(i): agg.COUNT_DISTINCT('user_3')})
        infor_home_2_only.rename({'user_1': 'user'})
        infor_home_2 = fof_home_case_2.groupby('user_1', {'information_home_case_2_'+str(i): agg.COUNT_DISTINCT('user_3')})
        infor_home_2.rename({'user_1': 'user'})
        fof_home_case_3_only = edge_fof_home_not_1st_frid[(edge_fof_home_not_1st_frid['user_2_home'] != i) & (edge_fof_home_not_1st_frid['user_1_home'] != edge_fof_home_not_1st_frid['user_2_home'])]
        infor_home_3_only = fof_home_case_3_only.groupby('user_1', {'information_home_case_3_only_'+str(i): agg.COUNT_DISTINCT('user_3')})
        infor_home_3_only.rename({'user_1': 'user'})

        user_result_final = user_result_final.join(infor, on='user', how='left')
        user_result_final = user_result_final.join(infor_home_2, on='user', how='left')
        user_result_final = user_result_final.join(infor_home_2_only, on='user', how='left')
        user_result_final = user_result_final.join(infor_home_3_only, on='user', how='left')

        # support
        edge_support = edge_fof_if_1st_frid[edge_fof_if_1st_frid['user_at_loc_home.1'] != None]
        edge_support = edge_support.remove_columns(['user_2_home', 'u_f_home.1', 'user_at_loc_home.1'])
        case_1 = edge_support[edge_support['u_f_home'] == i]
        case_2_only = edge_support[edge_support['u_f_home'] == edge_support['user_1_home']]
        case_2 = case_2_only.append(case_1)
        case_3_only = edge_support[(edge_support['u_f_home'] != i) & (edge_support['u_f_home'] != edge_support['user_1_home'])]
        case_3 = edge_support
        support_1 = case_1.groupby('user_1', {'support_tie_dest_case_1_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        support_1.rename({'user_1': 'user'})
        support_2_only = case_2_only.groupby('user_1', {'support_tie_dest_case_2_only_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        support_2_only.rename({'user_1': 'user'})
        support_2 = case_2.groupby('user_1', {'support_tie_dest_case_2_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        support_2.rename({'user_1': 'user'})
        support_3_only = case_3_only.groupby('user_1', {'support_tie_dest_case_3_only_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        support_3_only.rename({'user_1': 'user'})
        support_3 = case_3.groupby('user_1', {'support_tie_dest_case_3_'+str(i): agg.COUNT_DISTINCT('user_at_loc')})
        support_3.rename({'user_1': 'user'})
        support = support_1.join(support_2, on='user', how='inner')
        support = support.join(support_3, on='user', how='inner')
        support = support.join(support_2_only, on='user', how='left')
        support = support.join(support_3_only, on='user', how='left')
        support = support.join(degree_in_loc, on='user', how='left')
        support['support_dest_case_1_'+str(i)] = support['support_tie_dest_case_1_'+str(i)] / support['degree']
        support['support_dest_case_2_'+str(i)] = support['support_tie_dest_case_2_'+str(i)] / support['degree']
        support['support_dest_case_3_'+str(i)] = support['support_tie_dest_case_3_'+str(i)] / support['degree']
        support['support_dest_case_2_only_'+str(i)] = support['support_tie_dest_case_2_only_'+str(i)] / support['degree']
        support['support_dest_case_3_only_'+str(i)] = support['support_tie_dest_case_3_only_'+str(i)] / support['degree']
        support = support.remove_columns(['support_tie_dest_case_1_'+str(i), 'support_tie_dest_case_2_'+str(i), 'support_tie_dest_case_3_'+str(i), 'support_tie_dest_case_2_only_'+str(i), 'support_tie_dest_case_3_only_'+str(i)])
        # home support
        support_tie_home_case_2_only = edge_support_home.filter_by(i, 'user_tmp_home')
        support_tie_home_case_2 = support_tie_home_case_2_only.append(support_tie_home_1)
        support_home_2 = support_tie_home_case_2.groupby('user_1', {'support_tie_home_case_2_'+str(i): agg.COUNT_DISTINCT('user_3')})
        support_home_2.rename({'user_1': 'user'})
        support_home_2 = support_home_2.join(home_degree, on='user', how='left')
        support_home_2['support_home_case_2_'+str(i)] = support_home_2['support_tie_home_case_2_'+str(i)] / support_home_2['degree']
        support_home_2 = support_home_2.remove_columns(['support_tie_home_case_2_'+str(i), 'degree'])
        support_home_2_only = support_tie_home_case_2_only.groupby('user_1', {'support_tie_home_case_2_only_'+str(i): agg.COUNT_DISTINCT('user_3')})
        support_home_2_only.rename({'user_1': 'user'})
        support_home_2_only = support_home_2_only.join(home_degree, on='user', how='left')
        support_home_2_only['support_home_case_2_only_'+str(i)] = support_home_2_only['support_tie_home_case_2_only_'+str(i)] / support_home_2_only['degree']
        support_home_2_only = support_home_2_only.remove_columns(['support_tie_home_case_2_only_'+str(i), 'degree'])
        support_tie_home_case_3_only = edge_support_home[(edge_support_home['user_1_home'] != edge_support_home['user_tmp_home']) & (edge_support_home['user_tmp_home'] != i)]
        support_home_3_only = support_tie_home_case_3_only.groupby('user_1', {'support_tie_home_case_3_only_'+str(i): agg.COUNT_DISTINCT('user_3')})
        support_home_3_only.rename({'user_1': 'user'})
        support_home_3_only = support_home_3_only.join(home_degree, on='user', how='left')
        support_home_3_only['support_home_case_3_only_'+str(i)] = support_home_3_only['support_tie_home_case_3_only_'+str(i)] / support_home_3_only['degree']
        support_home_3_only = support_home_3_only.remove_columns(['support_tie_home_case_3_only_'+str(i), 'degree'])

        user_result_final = user_result_final.join(support, on='user', how='left')
        user_result_final = user_result_final.join(support_home_2, on='user', how='left')
        user_result_final = user_result_final.join(support_home_2_only, on='user', how='left')
        user_result_final = user_result_final.join(support_home_3_only, on='user', how='left')
        print(i)

    user_h_d_r = user_result_final.join(infor_home_1_3, on='user', how='left')
    user_h_d_r = user_h_d_r.join(support_home_1_3, on='user', how='left')
    user_h_d_r = user_h_d_r.join(users[['id','type','dest','home']], on={'user':'id'}, how='inner')
    user_h_d_r.export_csv('result/' + data_date + '_information_overall_network.csv')
    print(data_date + ' done')
