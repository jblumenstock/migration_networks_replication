import pandas as pd
import numpy as np
from graphlab import SArray, SFrame, SGraph, aggregate as agg, degree_counting
import random
import sys
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

freeze_month_n = int(sys.argv[1])
compare_month_n = int(sys.argv[2])
# # Say in district D, i has contacts {a,b} at t-6 at {b,c} at t-2.
# # -- a has contacts {a1,a2} at t-6 and {a3,a4} at t-2
# # -- b has contacts {b1,b2} at t-6 and {b3,b4} at t-2
# # -- c has contacts {c1,c2} at t-6 and {c3,c4} at t-2
# # we can include a, or remove a.
# # IF_ONLY_REMAIN is the case of removing a
IF_ONLY_REMAIN = True

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    network_date = start_date + relativedelta(months=i + freeze_month_n + 1)
    network_date = network_date.strftime('%Y%m')[2:]
    network_base_date = network_date
    network_compare_date = start_date + relativedelta(months=i + compare_month_n + 1)
    network_compare_date = network_compare_date.strftime('%Y%m')[2:]

    conn_base = SFrame.read_csv('data/' + network_base_date + '_call.txt', delimiter='|', header=False)['X1', 'X2']
    conn_base.rename({'X1': 'user_1', 'X2': 'user_2'})
    conn_order = conn_base.flat_map(['user_1', 'user_2'], lambda x: [get_user_order(x['user_1'], x['user_2'])])
    conn_order = conn_order.filter_by('None', 'user_1', exclude=True)
    conn_base = conn_order.groupby(key_columns=['user_1', 'user_2'], operations={'conn_num': agg.COUNT()})

    conn_compare = SFrame.read_csv('data/' + network_compare_date + '_call.txt', delimiter='|', header=False)['X1', 'X2']
    conn_compare.rename({'X1': 'user_1', 'X2': 'user_2'})
    conn_order = conn_compare.flat_map(['user_1', 'user_2'], lambda x: [get_user_order(x['user_1'], x['user_2'])])
    conn_order = conn_order.filter_by('None', 'user_1', exclude=True)
    conn_compare = conn_order.groupby(key_columns=['user_1', 'user_2'], operations={'conn_num': agg.COUNT()})
    print('connection count done')

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

    g = SGraph()
    g = g.add_edges(conn_compare, src_field='user_1', dst_field='user_2')
    d = degree_counting.create(g)
    g_d = d['graph']
    degree = g_d.vertices['__id', 'total_degree']
    degree.rename({'__id': 'user'})
    degree_sort = degree.sort('total_degree', ascending=False)
    degree_95 = degree_sort.head(len(degree_sort) * 0.05)[-1]['total_degree']
    user_if_outlier = degree.apply(lambda x: get_outlier(x['user'], x['total_degree'], degree_95))
    user_outlier = user_if_outlier.filter(lambda x: x != 'None')
    conn_1 = conn_compare.filter_by(user_outlier, 'user_1', exclude=True)
    conn_compare = conn_1.filter_by(user_outlier, 'user_2', exclude=True)
    user_compare = set(conn_compare['user_1'].unique()) | set(conn_compare['user_1'].unique())

    # user_both = user_base & user_compare
    print('remove outliers done')

    # assign migration info to connection
    migration_file_name = 'data/' + data_date + '_migration.txt'
    users = SFrame.read_csv(migration_file_name, usecols=['id', 'type', 'home', 'dest'])
    dist = list(set(users['home'].unique()) | set(users['dest'].unique()))

    users_with_modal_tower_base = SFrame.read_csv(network_base_date + '_modal_district.txt', delimiter='\t', header=False)
    users_with_modal_tower_base.rename({'X1': 'user', 'X2': 'home'})
    users_loc_base = users_with_modal_tower_base.flat_map(['user', 'home'], lambda x: [[x['user'].split('_')[0], x['home']]])

    users_with_modal_tower_compare = SFrame.read_csv(network_compare_date + '_modal_district.txt', delimiter='\t', header=False)
    users_with_modal_tower_compare.rename({'X1': 'user', 'X2': 'home'})
    users_loc_compare = users_with_modal_tower_compare.flat_map(['user', 'home'], lambda x: [[x['user'].split('_')[0], x['home']]])

    conn_compare = conn_compare.join(users_loc_compare, on={'user_1': 'user'}, how='inner')
    conn_compare.rename({'home': 'user_1_home'})
    conn_compare = conn_compare.join(users_loc_compare, on={'user_2': 'user'}, how='inner')
    conn_compare.rename({'home': 'user_2_home'})
    conn_compare_bidir = conn_compare.copy()
    tmp = conn_compare.copy()
    tmp.rename({'user_1': 'u2', 'user_2': 'u1',
                'user_1_home': 'u2_home', 'user_2_home': 'u1_home'})
    tmp.rename({'u2': 'user_2', 'u1': 'user_1',
                'u2_home': 'user_2_home', 'u1_home': 'user_1_home'})
    conn_compare_bidir = conn_compare_bidir.append(tmp)
    tie_loc_compare = conn_compare_bidir.groupby(['user_1', 'user_2_home'],
                                                 {'friends': agg.CONCAT('user_2')})
    tie_loc_compare.rename({'user_2_home': 'loc'})
    tie_loc_compare = tie_loc_compare.groupby('user_1',
                                              {'friends_loc': agg.CONCAT('loc', 'friends')})
    tie_loc_compare.rename({'user_1': 'user'})
    del tmp

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
    tie_loc_base = conn_base_bidir.groupby(['user_1', 'user_2_home'],
                                                 {'friends': agg.CONCAT('user_2')})
    tie_loc_base.rename({'user_2_home': 'loc'})
    tie_loc_base = tie_loc_base.groupby('user_1',
                                              {'friends_loc': agg.CONCAT('loc', 'friends')})
    tie_loc_base.rename({'user_1': 'user'})
    del tmp
    user_base = list(set(conn_base_bidir['user_1'].unique()))

    # create result frame
    user_result = pd.DataFrame(columns=['user', 'home'])
    user_result['user'] = users['id']
    user_result['home'] = users['home']
    user_result = SFrame(data=user_result)

    # remove those without connection
    user_result_final = user_result.filter_by(user_base, 'user')

    for i in dist:
        edge_with_frid_at_loc = conn_base_bidir.filter_by(i, 'user_2_home')
        edge_with_frid_at_loc_compare = conn_compare_bidir.filter_by(i, 'user_2_home')
        # make sure the tie to a friend still exists in the compare month
        tie_exist_two_month = edge_with_frid_at_loc.join(edge_with_frid_at_loc_compare[['user_1', 'user_2']], on=['user_1', 'user_2'], how='inner')
        if IF_ONLY_REMAIN:
            edge_df = tie_exist_two_month
        else:
            edge_df = edge_with_frid_at_loc

        egofrid_with_frid_at_loc = edge_df['user_2'].unique()
        #### base
        edge_egofrid_with_frid_at_loc = conn_base_bidir.filter_by(egofrid_with_frid_at_loc, 'user_1').filter_by(i, 'user_2_home')
        # calculate information
        edge_egofrid_with_frid_at_loc_group = edge_egofrid_with_frid_at_loc.groupby('user_1',
                                                                                    {
                                                                                    'friends': agg.CONCAT('user_2'),
                                                                                     })
        base_frid = edge_df.join(edge_egofrid_with_frid_at_loc_group[['user_1', 'friends']], on={'user_2': 'user_1'}, how='inner')
        base_frid = base_frid.groupby('user_1',
                                      {'fof_all': agg.CONCAT('friends'),
                                       'degree': agg.COUNT()})
        base_frid.rename({'user_1': 'user', 'fof_all': 'fof_all_base'})
        base_frid['fof_all_base1'] = base_frid.apply(lambda x: [item for sublist in x['fof_all_base'] for item in sublist])
        base_frid['fof_num_base'] = base_frid.apply(lambda x: len(set(x['fof_all_base1']) - set([x['user']])))
        base_frid = base_frid.remove_columns(['fof_all_base', 'fof_all_base1'])
        # calculate support
        ego_alter_base = edge_df.join(edge_egofrid_with_frid_at_loc, on={'user_2': 'user_1'}, how='inner')
        ego_alter_base.rename({'user_2.1': 'user_3'})
        supported_tie_base = edge_df.join(ego_alter_base, on={'user_1': 'user_1', 'user_2': 'user_3'}, how='inner')
        # a friend might have multiple common friends with ego i
        supported_tie_base2 = supported_tie_base[['user_1', 'user_2']].unique()
        supported_base = supported_tie_base2.groupby('user_1', {'support': agg.COUNT()})
        supported_base.rename({'user_1': 'user', 'support': 'support_base'})
        # join should on left. because if support exist, then information must exist,
        base_result = base_frid.join(supported_base, on='user', how='left')
        base_result['support_base'] = base_result['support_base'] / base_result['degree']
        base_result = base_result.fillna('support_base', 0)
        #### compare
        edge_egofrid_frid_at_loc_compare = conn_compare_bidir.filter_by(egofrid_with_frid_at_loc, 'user_1').filter_by(i, 'user_2_home')
        # calculate information
        edge_egofrid_frid_at_loc_compare_group = edge_egofrid_frid_at_loc_compare.groupby('user_1',
                                                                                     {
                                                                                     'friends': agg.CONCAT('user_2'),
                                                                                     })
        compare_frid = edge_df.join(edge_egofrid_frid_at_loc_compare_group[['user_1', 'friends']], on={'user_2': 'user_1'}, how='inner')
        compare_frid = compare_frid.groupby('user_1',
                                         {'fof_all': agg.CONCAT('friends'),
                                          'degree': agg.COUNT()})
        compare_frid.rename({'user_1': 'user', 'fof_all': 'fof_all_compare'})
        compare_frid['fof_all_compare1'] = compare_frid.apply(lambda x: [item for sublist in x['fof_all_compare'] for item in sublist])
        compare_frid['fof_num_compare'] = compare_frid.apply(lambda x: len(set(x['fof_all_compare1']) - set([x['user']])))
        compare_frid = compare_frid.remove_columns(['fof_all_compare', 'fof_all_compare1'])
        # calculate support
        if IF_ONLY_REMAIN:
            edge_df_2 = tie_exist_two_month
        else:
            edge_df_2 = edge_with_frid_at_loc_compare
        ego_alter_compare = edge_df_2.join(edge_egofrid_frid_at_loc_compare, on={'user_2': 'user_1'}, how='inner')
        ego_alter_compare.rename({'user_2.1': 'user_3'})
        supported_tie_compare = edge_df_2.join(ego_alter_compare, on={'user_1': 'user_1', 'user_2': 'user_3'}, how='inner')
        supported_tie_compare2 = supported_tie_compare[['user_1', 'user_2']].unique()
        supported_compare = supported_tie_compare2.groupby('user_1', {'support': agg.COUNT()})
        supported_compare.rename({'user_1': 'user', 'support': 'support_compare'})

        compare_result = compare_frid.join(supported_compare, on='user', how='left')
        compare_result['support_compare'] = compare_result['support_compare'] / compare_result['degree']
        compare_result = compare_result.fillna('support_compare', 0)
        compare_result = compare_result.remove_column('degree')

        result = base_result.join(compare_result, on={'user': 'user'}, how='left')
        result = result.fillna('fof_num_compare', 0)
        result['information_diff'] = result['fof_num_compare'] - result['fof_num_base']
        result = result.fillna('support_compare', 0)
        result['support_diff'] = result['support_compare'] - result['support_base']
        result.rename({'information_diff': 'information_diff_' + str(i),
                       'degree': 'degree_' + str(i),
                       'support_diff': 'support_diff_' + str(i)})
        user_result_final = user_result_final.join(result[['user', 'information_diff_' + str(i), 'support_diff_' + str(i), 'degree_' + str(i)]], on='user', how='left')
        print(i)
    user_h_d_r = user_result_final.join(users[['id','type','dest','home']], on={'user':'id'}, how='inner')
    users_loc_base.rename({'home': 'home_' + str(freeze_month_n) + 'month'})
    user_h_d_r = user_h_d_r.join(users_loc_base, on={'user': 'user'}, how='inner')
    users_loc_compare.rename({'home': 'home_' + str(compare_month_n) + 'month'})
    user_h_d_r = user_h_d_r.join(users_loc_compare, on={'user': 'user'}, how='inner')
    for c in ['information_diff', 'support_diff', 'degree']:
        user_h_d_r[c+'_home'] = user_h_d_r.apply(lambda x: x[c+'_'+str(x['home'])])

    user_h_d_r.export_csv('data/user_result_information_support_diff_if_remained_' + str(IF_ONLY_REMAIN) + '_' +data_date+'_between_'+str(freeze_month_n) +'_to_' + str(compare_month_n) + '_months.csv')
    print(data_date + ' done')
