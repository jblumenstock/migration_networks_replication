import pandas as pd
import numpy as np
from graphlab import SFrame, SGraph, aggregate as agg, degree_counting
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


def get_variables(g, nodes_dict):
    # add four new features
    # Strong-Strong information
    # Strong-Weak information
    # Weak-Strong information
    # Weak-Weak information
    columns_this = ['user', 's_s_infor', 's_w_infor', 'w_s_infor', 'w_w_infor',
                    's_s_support', 's_w_support', 'w_s_support', 'w_w_support']
    result = []
    a = 1
    start_time = time.time()
    for v_0 in nodes_dict.keys():
        v = int(v_0[1:])
        level_1 = []
        conn_weight = []
        level_1_strong = []
        level_1_weak = []
        for i in g.GetNI(v).GetOutEdges():
            w = g.GetIntAttrDatE(g.GetEI(v, i), 'weight')
            conn_weight.append(w)
            level_1.append(i)
            # strong tie
            if w > 5:
                level_1_strong.append(i)
            else:
                level_1_weak.append(i)

        strong_strong = []
        strong_weak = []
        # strong
        for i in level_1_strong:
            for j in g.GetNI(i).GetOutEdges():
                w = g.GetIntAttrDatE(g.GetEI(i, j), 'weight')
                if w > 5:
                    strong_strong.append(j)
                else:
                    strong_weak.append(j)
        weak_strong = []
        weak_weak = []
        # strong
        for i in level_1_weak:
            for j in g.GetNI(i).GetOutEdges():
                w = g.GetIntAttrDatE(g.GetEI(i, j), 'weight')
                if w > 5:
                    weak_strong.append(j)
                else:
                    weak_weak.append(j)

        # get information
        level_1 = set(level_1)
        level_1_strong = set(level_1_strong)
        level_1_weak = set(level_1_weak)
        strong_strong = set(strong_strong)
        strong_weak = set(strong_weak)
        weak_strong = set(weak_strong)
        weak_weak = set(weak_weak)

        information_ss = strong_strong - level_1 - set([v])
        information_sw = strong_weak - level_1 - set([v])
        information_ws = weak_strong - level_1 - set([v])
        information_ww = weak_weak - level_1 - set([v])

        degree = len(level_1)
        support_ss = len(strong_strong & level_1)
        support_sw = len(strong_weak & level_1)
        support_ws = len(weak_strong & level_1)
        support_sw = len(weak_weak & level_1)
        if degree > 0:
            support_ss = support_ss / float(degree)
            support_sw = support_sw / float(degree)
            support_ws = support_ws / float(degree)
            support_ww = support_ww / float(degree)
        else:
            support_ss = np.nan
            support_sw = np.nan
            support_ws = np.nan
            support_ww = np.nan

        result.append([v_0, len(information_ss), len(information_sw),
                       len(information_ws), len(information_ww),
                       support_ss, support_sw, support_ws, support_ww])
        if a % 10000 == 0:
            end_time = time.time()
            print(a)
            print('time: ' + str(end_time - start_time))
            start_time = time.time()
        a += 1
    if len(result) != 0:
        result_np = np.array(result)
    else:
        result_np = result
    user_this = pd.DataFrame(data=result_np, columns=columns_this)
    user_this[columns_this[1:]] = user_this[columns_this[1:]].astype(float)
    user_this[columns_this[0]] = user_this[columns_this[0]].astype(str)
    return user_this


start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1
# strong tie threshold
stong_tie_thre = 5

for i in xrange(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    network_date = start_date + relativedelta(months=i - 1)
    network_date = network_date.strftime('%Y%m')[2:]
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
    conn_4 = conn_2
    print('remove outliers done')

    # assign migration info to connection
    migration_file_name = 'data/' + data_date + '_migration.txt'
    users = SFrame.read_csv(migration_file_name, usecols=['id', 'type', 'home', 'dest'])
    dist = list(set(users['home']) | set(users['dest']))

    all_columns = ['user']
    for i in dist:
        all_columns.append('d_' + str(i))
        all_columns.append('c_' + str(i))
        all_columns.append('s_' + str(i))
        all_columns.append('l_' + str(i))

    users_with_modal_tower = SFrame.read_csv('data/' + network_date + '_modal_district.txt', delimiter='\t', header=False)
    users_with_modal_tower.rename({'X1': 'user', 'X2': 'home'})
    users_with_modal_tower = users_with_modal_tower.flat_map(['user', 'home'], lambda x: [[x['user'].split('_')[0], x['home']]])

    # create result frame
    user_result = pd.DataFrame(columns=['user', 'home'])
    user_result['user'] = users_with_modal_tower['user']
    user_result['home'] = users_with_modal_tower['home']
    user_result = SFrame(data=user_result)

    conn_5 = conn_4.join(users_with_modal_tower, on={'user_1': 'user'}, how='inner')
    conn = conn_5.join(users_with_modal_tower, on={'user_2': 'user'}, how='inner')
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
        user_result_this.rename({'s_s_infor': 's_s_infor_' + str(i),
                                 's_w_infor': 's_w_infor_' + str(i),
                                 'w_s_infor': 'w_s_infor_' + str(i),
                                 'w_w_infor': 'w_w_infor_' + str(i),
                                 's_s_support': 's_s_support_' + str(i),
                                 's_w_support': 's_w_support_' + str(i),
                                 'w_s_support': 'w_s_support_' + str(i),
                                 'w_w_support': 'w_w_support_' + str(i)})

        user_result_this.remove_column('degree_overall')
        user_result_final = user_result_final.join(user_result_this, on='user', how='inner')
        print(i)

    user_h_d_r = user_result_final.join(users[['id', 'type', 'dest']],
                                        on={'user': 'id'},
                                        how='inner')

    for c in ['s_s_infor', 's_w_infor', 'w_s_infor', 'w_w_infor',
              's_s_support', 's_w_support', 'w_s_support', 'w_w_support']:
        user_h_d_r[c+'_home'] = user_h_d_r.apply(lambda x: x[c+'_'+str(x['home'])])

    user_h_d_r.export_csv('data/' + data_date + '_user_result_infor_support_strong.csv')
    print(data_date + ' done')
