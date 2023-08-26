import pandas as pd
import numpy as np
import itertools
from graphlab import SArray, SFrame, SGraph, Vertex, Edge, triangle_counting, aggregate as agg, degree_counting
from snap import *
from multiprocessing import Pool
import time
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib as mpl
mpl.rcParams['axes.unicode_minus'] = False
mpl.use('Agg')
import matplotlib.pyplot as plt


np.random.seed(123)


def get_outlier(user, degree, thre):
    if degree >= thre:
        return user
    else:
        return 'None'


def get_user_order(user_1, user_2):
    if user_1 > user_2:
        return [user_2, user_1]
    elif user_1 == user_2:
        return ['None', 'None']
    else:
        return [user_1, user_2]


def get_users(user_home_select, home_dist, dest_dist, to_remove_dict,
              if_match_degree, if_same_sum):
    to_remove = to_remove_dict[dest_dist]
    user_home_select['dest_analyzed'] = dest_dist
    user_home_select_migrant = user_home_select[user_home_select['dest'] == dest_dist]
    user_home_select_migrant = user_home_select_migrant[~user_home_select_migrant.user.isin(to_remove)]
    user_home_select_migrant = user_home_select_migrant[(user_home_select_migrant['d_' + str(dest_dist)] <= 22) &
                                                        (user_home_select_migrant['d_' + str(dest_dist)] > 0)]
    user_home_select_remain = user_home_select[user_home_select['dest'] == home_dist]
    user_home_select_remain = user_home_select_remain[~user_home_select_remain.user.isin(to_remove)]
    user_home_select_remain = user_home_select_remain[(user_home_select_remain['d_' + str(dest_dist)] <= 22) &
                                                      (user_home_select_remain['d_' + str(dest_dist)] > 0)]
    user_home_select_migrant['d_dest'] = user_home_select_migrant['d_'+str(dest_dist)]
    user_home_select_migrant['d_home'] = user_home_select_migrant['d_'+str(home_dist)]
    user_home_select_remain['d_dest'] = user_home_select_remain['d_'+str(dest_dist)]
    user_home_select_remain['d_home'] = user_home_select_remain['d_'+str(home_dist)]
    # add supported link
    user_home_select_migrant['slink_home'] = user_home_select_migrant['slink_' + str(home_dist)]
    user_home_select_migrant['slink_dest'] = user_home_select_migrant['slink_' + str(dest_dist)]
    user_home_select_remain['slink_home'] = user_home_select_remain['slink_' + str(home_dist)]
    user_home_select_remain['slink_dest'] = user_home_select_remain['slink_' + str(dest_dist)]
    if if_same_sum:
        if if_match_degree:
            migrant_d = user_home_select_migrant.groupby(['d_home', 'd_dest'])\
                                                .size().reset_index(name='num')
            d_home_all = []
            d_dest_all = []
            n_migrant_all = []
            n_remain_all = []
            remain = pd.DataFrame(columns=user_home_select_remain.columns.tolist())
            migrant = pd.DataFrame(columns=user_home_select_remain.columns.tolist())
            for i, row in migrant_d.iterrows():
                d_home = row['d_home']
                d_dest = row['d_dest']
                d_home_all.append(d_home)
                d_dest_all.append(d_dest)
                migrant_n = int(row['num'])
                remain_this = user_home_select_remain[(user_home_select_remain['d_dest'] == d_dest) &
                                                      (user_home_select_remain['d_home'] == d_home)]
                remain_n = remain_this.shape[0]
                migrant_this = user_home_select_migrant[(user_home_select_migrant['d_dest'] == d_dest) &
                                                        (user_home_select_migrant['d_home'] == d_home)]
                n_min = min(migrant_n, remain_n)
                if n_min > 0:
                    if migrant_n == remain_n:
                        remain = remain.append(remain_this)
                        migrant = migrant.append(migrant_this)
                    elif migrant_n > remain_n:
                        remain = remain.append(remain_this)
                        migrant = migrant.append(migrant_this.sample(n=remain_n))
                    else:
                        remain = remain.append(remain_this.sample(n=migrant_n))
                        migrant = migrant.append(migrant_this)
        else:
            sample_num = min(len(user_home_select_migrant), len(user_home_select_remain))
            if len(user_home_select_migrant) == sample_num:
                user_home_select_remain = user_home_select_remain.sample(n=sample_num)
            else:
                user_home_select_migrant = user_home_select_migrant.sample(n=sample_num)
            migrant = user_home_select_migrant
            remain = user_home_select_remain
        if len(remain) != len(migrant):
            print('error: home num != dest num')
    else:
        migrant = user_home_select_migrant
        remain = user_home_select_remain
    migrant['if_migrant'] = 1
    remain['if_migrant'] = 0
    return migrant.append(remain)


def calculate_cent(n, coef_dict, nodes_frid, if_remove_t_1):
    f1 = nodes_frid[n]
    coef_t1_dict = {}
    for f1_ in f1:
        coef_t1_dict[f1_] = coef_dict[f1_] * coef_dict[n]
    coef_t1_sum = sum(coef_t1_dict.values())
    coef_this_2 = []
    coef_this_4 = []
    for f1_ in f1:
        f2 = nodes_frid[f1_]
        coef_t2_dict = {}
        for f2_ in f2:
            coef_t2_dict[f2_] = coef_dict[f2_] * coef_t1_dict[f1_]
        coef_s2 = sum(coef_t2_dict.values())
        coef_this_2.append(coef_s2)
        coef_this_3 = []
        for f2_ in f2:
            f3 = nodes_frid[f2_]
            coef_t3_dict = {}
            for f3_ in f3:
                coef_t3_dict[f3_] = coef_dict[f3_] * coef_t2_dict[f2_]
            coef_s3 = sum(coef_t3_dict.values())
            coef_this_3.append(coef_s3)
        coef_this_4.append(sum(coef_this_3))
    if if_remove_t_1:
        r = sum(coef_this_2) + sum(coef_this_4)
    else:
        r = coef_t1_sum + sum(coef_this_2) + sum(coef_this_4)
    return r


# calculate the diffusion
def get_centrality(diffusion_p_all, lambda_home, t_list, nodes_frid,
                   node_degree_dict, if_remove_t_1=False):
    # key in nodes_frid include users who are outside of Di
    # but have friends at Di
    # node_degree_dict does not include users outside of Di
    centrality_all = {}
    centrality_all_dest = {}
    t_max = max(t_list)
    nodes = nodes_frid.keys()
    nodes_sort = sorted(nodes)
    node_degree = []
    for i in nodes_sort:
        if i in node_degree_dict:
            node_degree.append(node_degree_dict[i])
        else:
            # it doesn't matter to choose what value
            # because it won't be used
            # the value of nodes_frid can only be those in Di
            node_degree.append(1.)
    node_degree = np.array(node_degree)
    centrality_all[diffusion_p_all[0]] = {}
    centrality_all_dest[diffusion_p_all[0]] = {}
    for lambda_home_this in lambda_home:
        coef = diffusion_p_all[0] / (node_degree ** lambda_home_this)
        coef_dict = dict(zip(nodes_sort, coef))
        centrality_all[diffusion_p_all[0]][lambda_home_this] = {}
        sf = SFrame({'node': nodes_sort})
        sf['centrality'] = sf.apply(lambda x: calculate_cent(x['node'], coef_dict, nodes_frid, if_remove_t_1))
        centrality_all[diffusion_p_all[0]][lambda_home_this][3] = dict(zip(sf['node'], sf['centrality']))
    return centrality_all


# get destination degree of migrants
# remove those migrants without friends at destination
def if_dest_degree(x):
    dest = str(int(x['dest']))
    dest_d = x['d_' + dest]
    if dest_d > 0:
        return 1
    else:
        return 0


def get_network_at_dist(dist):
    edge_both_1 = conn.filter_by(dist, 'home_1')
    edge_both = edge_both_1.filter_by(dist, 'home_2')
    edge_out_1 = edge_both_1.filter_by(dist, 'home_2', exclude=True)  # user_1 in, user_2 out
    edge_out_1_inverse = SFrame({'user_1': edge_out_1['user_2'], 'user_2': edge_out_1['user_1'],
                                 'home_1': edge_out_1['home_2'], 'home_2': edge_out_1['home_1'],
                                 'conn_num': edge_out_1['conn_num']})
    edge_out_2 = conn.filter_by(dist, 'home_2').filter_by(dist, 'home_1', exclude=True)  # user_1 out, user_2 in
    edge_out = edge_out_2.append(edge_out_1_inverse)
    # when analyzing district Di
    # information can only diffused at Di
    # so focus on home
    nodes_friends = {}
    for line in edge_both:
        node_1 = int(line['user_1'][1:])
        node_2 = int(line['user_2'][1:])
        if node_1 not in nodes_friends:
            nodes_friends[node_1] = [node_2]
        else:
            nodes_friends[node_1].append(node_2)
        if node_2 not in nodes_friends:
            nodes_friends[node_2] = [node_1]
        else:
            nodes_friends[node_2].append(node_1)
    nodes_home = nodes_friends.keys()
    # nodes_degree is home degree
    # not add the num of destination friends
    nodes_degree = {}
    for i in nodes_friends:
        nodes_degree[i] = len(nodes_friends[i])
    # find the destination friends
    nodes_dest_friends = {}
    nodes_to_remove = []
    nodes_home_str = ['L' + '0' * (8 - len(str(i))) + str(i) for i in nodes_home]
    edge_out_in = edge_out.filter_by(nodes_home_str, 'user_2')
    edge_out_out = edge_out.filter_by(nodes_home_str, 'user_2', exclude=True)
    nodes_to_remove = list(edge_out_out['user_1'].unique())
    for line in edge_out_in:
        node_1 = int(line['user_1'][1:])
        node_2 = int(line['user_2'][1:])
        # remove those home users who have dest friends but don't have home friends
        if node_1 not in nodes_dest_friends:
            nodes_dest_friends[node_1] = [node_2]
            nodes_friends[node_1] = [node_2]
        else:
            nodes_dest_friends[node_1].append(node_2)
            nodes_friends[node_1].append(node_2)
    nodes_to_remove = list(set(nodes_to_remove))
    # key of node_friends include node at destination
    # but nodes_degree only count the number of person at home
    return nodes_friends, nodes_home_str, nodes_degree, nodes_dest_friends, nodes_to_remove


# SIMULATION
lambda_home = [0., 0.1, 0.3, 0.5, 0.7, 1.]
t_home = [3]
# to save computing time, directly use the 1 over eigenvalue of network
diffusion_p_all = [0.016]

t00 = time.time()
IF_MATCH_DEGREE = False 
IF_REMOVE_T_1 = False
IF_SAME_NUM = True

start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = (relativedelta(end_date, start_date).months
            + 12 * relativedelta(end_date, start_date).years
            + 1)

start_date_str = start_date.strftime('%Y%m')[2:]
end_date_str = end_date.strftime('%Y%m')[2:]
time_span = start_date_str + '-' + end_date_str

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    network_date = start_date + relativedelta(months=i - 1)
    network_date = network_date.strftime('%Y%m')[2:]

    network_file = 'data/' + network_date + '_call.txt'
    conn_raw = SFrame.read_csv(network_file, delimiter='|', header=False)['X1', 'X2']
    conn_raw.rename({'X1': 'user_1', 'X2': 'user_2'})

    conn_order = conn_raw.flat_map(['user_1', 'user_2'],
                                    lambda x: [get_user_order(x['user_1'], x['user_2'])])
    conn_order = conn_order.filter_by('None', 'user_1', exclude=True)
    conn_count = conn_order.groupby(key_columns=['user_1', 'user_2'],
                                    operations={'conn_num': agg.COUNT()})
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

    # get support link
    user_file = 'data/' + data_date + '_user_result.csv'
    users_network_features = pd.read_csv(user_file)
    users_network_features = users_network_features[users_network_features.type != 6]
   
    migration_file = 'data/' + data_date + '_migration.txt'
    migration = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]
    migration = migration[migration.type != 6]
    dist = list(set(migration['home']) | set(migration['dest']))
    for dist_this in dist:
        dist_this = str(dist_this)
        users_network_features['slink_' + dist_this] = users_network_features['s_' + dist_this] * \
            users_network_features['d_' + dist_this]
        users_network_features['slink_' + dist_this] = users_network_features['slink_' + dist_this].round()
        users_network_features['slink_unsupport_' + dist_this] = users_network_features['d_' + dist_this] - \
            users_network_features['slink_' + dist_this]
    print('support link calculated')

    users_network_features['if_dest_d'] =\
        users_network_features.apply(lambda x: if_dest_degree(x), axis=1)

    users_network_features =\
        users_network_features[((users_network_features.type.isin([1, 2, 5])) &
                                (users_network_features.if_dest_d == 1)) |
                                (users_network_features.type.isin([3, 4]))]
    migrant_other = users_network_features[users_network_features.type.isin([1, 2, 5])]
    home_dest = migrant_other.groupby(['home', 'dest']).size().reset_index(name='num')
    home_dest = home_dest.sort_values(by='num', ascending=False)
    # only keep those district pairs with more than 20 migrants
    home_dest = home_dest[home_dest.num >= 20]
    home_dest = home_dest.reset_index()
    print('migrant num: {}'.format(home_dest.shape[0]))

    if len(home_dest) > 0:
        # calculate centrality first
        # it will be used repeatly
        t_cen_0 = time.time()
        dists = list(set(home_dest.home.tolist() + home_dest.dest.tolist()))
        
        nodes_home_dict = {}
        to_remove_dict = {}
        centrality_dict = {}
        nodes_dest_friends_dict = {}
        for dist_this in dists:
            t_centra_0 = time.time()
            nodes_friends, nodes_home_str, nodes_degree, nodes_dest_friends, to_remove = get_network_at_dist(dist_this)
            nodes_home_dict[dist_this] = nodes_home_str
            to_remove_dict[dist_this] = to_remove
            nodes_dest_friends_dict[dist_this] = nodes_dest_friends
            centrality_all = get_centrality(diffusion_p_all,
                                            lambda_home,
                                            t_home,
                                            nodes_friends,
                                            nodes_degree,
                                            IF_REMOVE_T_1)
            centrality_dict[dist_this] = centrality_all
            t_centra_1 = time.time()
            print('{} centrality done. Time: {:.2f}'.format(dist_this, t_centra_1 - t_centra_0))
        t_cen_1 = time.time()
        print('centrality done. time: {:.2f}'.format(t_cen_1 - t_cen_0))
        for idx, row in home_dest.iterrows():
            home_dist = int(row['home'])
            dest_dist = int(row['dest'])
            nodes_dest_friends = nodes_dest_friends_dict[dest_dist]
            columns_select = ['user', 'home', 'dest',
                                'd_' + str(home_dist),
                                'd_' + str(dest_dist),
                                's_' + str(home_dist),
                                's_' + str(dest_dist),
                                'slink_' + str(home_dist),
                                'slink_' + str(dest_dist),
                                'slink_unsupport_' + str(home_dist),
                                'slink_unsupport_' + str(dest_dist)]
            user_home_select = users_network_features[users_network_features['home'] == home_dist][columns_select]
            user_home_select = user_home_select[user_home_select['user'].isin(nodes_home_dict[home_dist])]
            user_home_select = user_home_select.fillna(0)
            all_ = get_users(user_home_select, home_dist, dest_dist,
                                to_remove_dict,
                                if_match_degree=IF_MATCH_DEGREE,
                                if_same_sum=IF_SAME_NUM)
            print('selected uesr num: {}'.format(len(all_)))
            all_['date'] = data_date
            if len(all_) > 0:
                for l_idx, lambda_home_this in enumerate(lambda_home):
                    diffusion_centrality_dic_home = centrality_dict[home_dist][diffusion_p_all[0]][lambda_home_this][t_home[0]]
                    diffusion_centrality_dic_dest = centrality_dict[dest_dist][diffusion_p_all[0]][lambda_home_this][t_home[0]]
                    all_['ui_home_'+str(lambda_home_this)] = all_.apply(lambda x: diffusion_centrality_dic_home[int(x['user'][1:])], axis=1)
                    all_['ui_dest_'+str(lambda_home_this)] = all_.apply(lambda x: diffusion_centrality_dic_dest[int(x['user'][1:])], axis=1)
                    if l_idx == 0:
                        fields = ['user', 'date', 'home', 'dest', 'd_home',
                                    'd_dest', 'slink_home', 'slink_dest',
                                    'if_migrant', 'dest_analyzed',
                                    'ui_home_'+str(lambda_home_this),
                                    'ui_dest_'+str(lambda_home_this)]
                        all_add_feature_ = all_[fields]
                    else:
                        fields = ['user', 'date', 'home', 'dest_analyzed', 'ui_home_'+str(lambda_home_this), 'ui_dest_'+str(lambda_home_this)]
                        all_add_feature_ = all_add_feature_.merge(all_[fields], on=['user', 'date', 'home', 'dest_analyzed'], how='inner')
                if idx == 0 and i == 0:
                    all_add_feature = all_add_feature_
                else:
                    all_add_feature = all_add_feature.append(all_add_feature_)
                print(all_add_feature.shape)
        print('migrant remain sampling done')
    print(data_date + ' done')
