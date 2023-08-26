import pandas as pd
import numpy as np
from graphlab import SArray, SFrame, SGraph, Vertex, Edge, triangle_counting, aggregate as agg, degree_counting
import random
from snap import *
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

random.seed(0)


def get_sum(x):
    if x is None:
        return 0
    elif np.isnan(x):
        return 0
    else:
        return x


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


def weak_tie(data):
    strong_tie_num = 0
    weak_tie_num = 0
    for x in data:
        if x > 4:
            strong_tie_num += 1
        else:
            weak_tie_num += 1
    return strong_tie_num, weak_tie_num


def get_variables(g, nodes_dict):
    columns_this = ['user', 'd', 'c', 's', 'l', 'conn_weight', 'support_weight', 'information_weight', 'strong_tie', 'weak_tie']
    result = []
    a = 1
    start_time = time.time()
    for v_0 in nodes_dict.keys():
        v = int(v_0[1:])
        level_1 = []
        conn_weight = []
        for i in g.GetNI(v).GetOutEdges():
            level_1.append(i)
            conn_weight.append(g.GetIntAttrDatE(g.GetEI(v, i), 'weight'))
        if len(conn_weight) > 0:
            strong_tie_n, weak_tie_n = weak_tie(conn_weight)
        else:
            strong_tie_n, weak_tie_n = np.nan, np.nan
        level_2 = []
        cluster = 0
        support_weight = 0
        information_weight = 0
        for i in level_1:
            for j in g.GetNI(i).GetOutEdges():
                level_2.append(j)
                if j in level_1:
                    support_weight += g.GetIntAttrDatE(g.GetEI(i, j), 'weight')
                    cluster += 1
                else:
                    if j != v:
                        information_weight += g.GetIntAttrDatE(g.GetEI(i, j), 'weight')
        level_1_set = set(level_1)
        level_2_set = set(level_2)

        degree = len(level_1)
        support = len(level_1_set & level_2_set)
        information = level_2_set - level_1_set - set([v])  # remove the node itself

        if degree > 0:
            support = support / float(degree)
        else:
            support = np.nan

        if degree > 1:
            cc = cluster / float(degree * (degree - 1))
        else:
            cc = np.nan
        result.append([v_0, degree, cc, support, len(information), sum(conn_weight),
                       support_weight, information_weight, strong_tie_n, weak_tie_n])
        if a % 10000 == 0:
            end_time = time.time()
            print(a)
            print('time: ' + str(end_time - start_time))
            start_time = time.time()
        a += 1
    if len(result) != 0:
        result_np = np.array(result)
    else:
        result_np = result  # if no data in the result, like the district 29 (empty). it will report an error.
    user_this = pd.DataFrame(data=result_np, columns=columns_this)
    user_this[columns_this[1:]] = user_this[columns_this[1:]].astype(float)
    user_this[columns_this[0]] = user_this[columns_this[0]].astype(str)
    return user_this


start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    network_date = start_date + relativedelta(months=i - 1)
    network_date = network_date.strftime('%Y%m')[2:]
    tower_date = start_date + relativedelta(months=i - 1)
    tower_date = tower_date.strftime('%Y%m')[2:]
    conn_raw = SFrame.read_csv('data/' + network_date + '_call.txt', delimiter='|', header=False)['X1', 'X2']
    conn_raw.rename({'X1': 'user_1', 'X2': 'user_2'})

    conn_order = conn_raw.flat_map(['user_1', 'user_2'], lambda x: [get_user_order(x['user_1'], x['user_2'])])
    conn_order = conn_order.filter_by('None', 'user_1', exclude=True)
    conn_count = conn_order.groupby(key_columns=['user_1', 'user_2'], operations={'conn_num': agg.COUNT()})
    print('connection count done')

    # delete users with degree < 95%
    g = SGraph()
    g = g.add_edges(conn_count, src_field='user_1', dst_field='user_2')
    d = degree_counting.create(g)
    g_d = d['graph']
    degree = g_d.vertices['__id', 'total_degree']
    degree.rename({'__id': 'user'})
    degree_sort = degree.sort('total_degree', ascending=False)
    degree_95 = degree_sort.head(len(degree_sort) * 0.05)[-1]['total_degree']
    user_if_outlier = degree.apply(lambda x: get_outlier(x['user'], x['total_degree'], degree_95))
    user_outlier = user_if_outlier.filter(lambda x: x != 'None')

    conn_1 = conn_count.filter_by(user_outlier, 'user_1', exclude=True)
    conn_2 = conn_1.filter_by(user_outlier, 'user_2', exclude=True)
    print('remove outliers done')

    # assign migration info to connection
    migration_file_name = data_date + '_migration.txt'
    users = SFrame.read_csv('data/' + migration_file_name, usecols=['id', 'type', 'home', 'dest'])
    dist = list(set(users['home']) | set(users['dest']))

    all_columns = ['user']
    for i in dist:
        # degree
        all_columns.append('d_' + str(i))
        # clustering coefficient
        all_columns.append('c_' + str(i))
        # support
        all_columns.append('s_' + str(i))
        # friends of friends
        all_columns.append('l_' + str(i))

    users_with_modal_tower = SFrame.read_csv('data/' + tower_date + '_modal_district.txt', delimiter='\t', header=False)
    users_with_modal_tower.rename({'X1': 'user', 'X2': 'home'})
    users_with_modal_tower = users_with_modal_tower.flat_map(['user', 'home'], lambda x: [[x['user'].split('_')[0], x['home']]])

    # create result frame
    user_result = pd.DataFrame(columns=['user', 'home'])
    user_result['user'] = users_with_modal_tower['user']
    user_result['home'] = users_with_modal_tower['home']
    user_result = SFrame(data=user_result)

    conn_3 = conn_2.join(users_with_modal_tower, on={'user_1': 'user'}, how='inner')
    conn = conn_3.join(users_with_modal_tower, on={'user_2': 'user'}, how='inner')
    conn.rename({'home': 'home_1', 'home.1': 'home_2'})
    print('assign migration info done')

    # remove those without connection
    users_with_conn = conn['user_1'].append(conn['user_2'])
    users_with_conn_uniq = users_with_conn.unique()
    user_result_raw = user_result.filter_by(users_with_conn_uniq, 'user')
    user_result_final = user_result_raw.filter_by(users_with_conn_uniq, 'user')

    # overall
    g = SGraph()
    g = g.add_edges(conn, src_field='user_1', dst_field='user_2')
    d = degree_counting.create(g)
    g_d = d['graph']
    degree = g_d.vertices['__id', 'total_degree']
    if len(degree) == 0:
        degree['__id'] = degree['__id'].astype(str)
    user_result = user_result_raw.join(degree, on={'user': '__id'}, how='left')
    user_result.rename({'total_degree': 'degree_overall'})

    user_result_frame = SFrame({'user': user_result['user'], 'd_all': user_result['degree_overall']})
    user_result_final = user_result_final.join(user_result_frame['user', 'd_all'], on={'user': 'user'}, how='left')

    for i in dist:
        edge_both_1 = conn.filter_by(i, 'home_1')
        edge_both = edge_both_1.filter_by(i, 'home_2')
        edge_out_1 = edge_both_1.filter_by(i, 'home_2', exclude=True)  # user_1 in, user_2 out
        edge_out_1_inverse = SFrame({'user_1': edge_out_1['user_2'], 'user_2': edge_out_1['user_1'],
                                     'home_1': edge_out_1['home_2'], 'home_2': edge_out_1['home_1'],
                                     'conn_num': edge_out_1['conn_num']})
        edge_out_2 = conn.filter_by(i, 'home_2').filter_by(i, 'home_1', exclude=True)  # user_1 out, user_2 in
        edge_out = edge_out_2.append(edge_out_1_inverse)
        user_out = edge_out['user_1'].unique()

        g_snap = TNEANet.New()
        nodes = []
        edge_id = 0
        for line in edge_both:
            node_1 = int(line['user_1'][1:])
            node_2 = int(line['user_2'][1:])
            conn_num = int(line['conn_num'])
            if not g_snap.IsNode(node_1):
                g_snap.AddNode(node_1)
                nodes.append(line['user_1'])
            if not g_snap.IsNode(node_2):
                g_snap.AddNode(node_2)
                nodes.append(line['user_2'])
            g_snap.AddEdge(node_1, node_2)
            g_snap.AddIntAttrDatE(edge_id, conn_num, 'weight')
            edge_id += 1
            g_snap.AddEdge(node_2, node_1)
            g_snap.AddIntAttrDatE(edge_id, conn_num, 'weight')
            edge_id += 1
        for line in edge_out:
            node_1 = int(line['user_1'][1:])
            node_2 = int(line['user_2'][1:])
            conn_num = int(line['conn_num'])
            if not g_snap.IsNode(node_1):
                g_snap.AddNode(node_1)
                nodes.append(line['user_1'])
            if not g_snap.IsNode(node_2):
                g_snap.AddNode(node_2)
                nodes.append(line['user_2'])
            g_snap.AddEdge(node_1, node_2)
            g_snap.AddIntAttrDatE(edge_id, conn_num, 'weight')
            edge_id += 1
        nodes_dict = {}
        for n in nodes:
            nodes_dict[n] = [0] * 5
        result = get_variables(g_snap, nodes_dict)
        result = SFrame(result)
        result['user'] = result['user'].astype(str) 
        user_result_this = user_result.copy()
        user_result_this = user_result_this[['user', 'degree_overall']].join(result, on={'user': 'user'}, how='left')
        user_result_this['d_percent'] = user_result_this['d'] / user_result_this['degree_overall']
        user_result_this.rename({'d': 'd_' + str(i), 'c': 'c_' + str(i), 's': 's_' + str(i), 'l': 'l_' + str(i),
                                 'conn_weight': 'conn_weight_' + str(i), 'support_weight': 'support_weight_' + str(i),
                                 'information_weight': 'information_weight_' + str(i), 'd_percent': 'd_percent_' + str(i),
                                 'strong_tie': 'strong_tie_' + str(i), 'weak_tie': 'weak_tie_' + str(i)})

        user_result_this.remove_column('degree_overall')
        user_result_final = user_result_final.join(user_result_this, on='user', how='inner')
        print(i)

    user_h_d_r = user_result_final.join(users[['id','type','dest']], on={'user':'id'}, how='inner')

    for c in ['d','c','s','l','conn_weight','support_weight','information_weight', 'd_percent', 'strong_tie', 'weak_tie']:
        user_h_d_r[c+'_home'] = user_h_d_r.apply(lambda x: x[c+'_'+str(x['home'])])

    user_h_d_r.export_csv('data/' + data_date + '_user_result.csv')
    print(data_date + ' done')
