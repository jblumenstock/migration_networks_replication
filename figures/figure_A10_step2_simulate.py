def get_accuracy(p):
    pi_home_i_this, pi_dest_i_this, pi_home_c_this, pi_dest_c_this, \
        alpha_home_this, alpha_dest_this, \
        lambda_home_this, rho_this, t_this, diffusion_p_this = p 

    all_ = all_add_feature.copy()
    # home
    all_['slink_home_multiply'] = alpha_home_this * all_['slink_home']
    all_['uc_home'] = all_['d_home'] + all_['slink_home_multiply']
    all_['uc_home_multiply'] = pi_home_c_this * all_['uc_home']
    all_['ui_home_'+str(lambda_home_this)] /= (0.016 ** 2)
    all_['ui_home_multiply'] = pi_home_i_this * all_['ui_home_'+str(lambda_home_this)]
    all_['u_home'] = all_['uc_home_multiply'] + all_['ui_home_multiply']
    # dest
    all_['slink_dest_multiply'] = alpha_dest_this * all_['slink_dest']
    all_['uc_dest'] = all_['d_dest'] + all_['slink_dest_multiply']
    all_['uc_dest_multiply'] = pi_dest_c_this * all_['uc_dest']
    all_['ui_dest_'+str(lambda_home_this)] /= (0.016 ** 2)
    all_['ui_dest_multiply'] = pi_dest_i_this * all_['ui_dest_'+str(lambda_home_this)]
    all_['u_dest'] = all_['uc_dest_multiply'] + all_['ui_dest_multiply']

    all_['u_home_multiply'] = rho_this * all_['u_home']
    all_['u_diff'] = all_['u_dest'] - all_['u_home_multiply']
    all_['move_result'] =\
        all_.apply(lambda x: move_or_not(x['u_diff'], 0), axis=1)

    remain = all_[all_['if_migrant'] == 0]
    migrant = all_[all_['if_migrant'] == 1]
    wrong_num_remain = remain[remain['move_result'] == 1].shape[0]
    right_num_remain = remain[remain['move_result'] == 0].shape[0]

    wrong_num_migrant = migrant[migrant['move_result'] == 0].shape[0]
    right_num_migrant = migrant[migrant['move_result'] == 1].shape[0]
    wrong_total = wrong_num_remain + wrong_num_migrant
    right_total = right_num_remain + right_num_migrant

    migrant_ui_dest = migrant['ui_dest_'+str(lambda_home_this)].median()
    migrant_ui_dest_mul = migrant['ui_dest_multiply'].median()
    migrant_uc_dest = migrant['uc_dest'].median()
    migrant_uc_dest_mul = migrant['uc_dest_multiply'].median()
    migrant_u_dest = migrant['u_dest'].median()
    migrant_ui_home = migrant['ui_home_'+str(lambda_home_this)].median()
    migrant_ui_home_mul = migrant['ui_home_multiply'].median()
    migrant_uc_home = migrant['uc_home'].median()
    migrant_uc_home_mul = migrant['uc_home_multiply'].median()
    migrant_u_home = migrant['u_home'].median()
    migrant_u_home_mul = migrant['u_home_multiply'].median()
    remain_ui_dest = remain['ui_dest_'+str(lambda_home_this)].median()
    remain_ui_dest_mul = remain['ui_dest_multiply'].median()
    remain_uc_dest = remain['uc_dest'].median()
    remain_uc_dest_mul = remain['uc_dest_multiply'].median()
    remain_u_dest = remain['u_dest'].median()
    remain_ui_home = remain['ui_home_'+str(lambda_home_this)].median()
    remain_ui_home_mul = remain['ui_home_multiply'].median()
    remain_uc_home = remain['uc_home'].median()
    remain_uc_home_mul = remain['uc_home_multiply'].median()
    remain_u_home = remain['u_home'].median()
    remain_u_home_mul = remain['u_home_multiply'].median()
    return [wrong_total, wrong_num_remain, wrong_num_migrant,
            right_total, right_num_remain, right_num_migrant,
            migrant_ui_dest, migrant_ui_dest_mul,
            migrant_uc_dest, migrant_uc_dest_mul,
            migrant_u_dest,
            migrant_ui_home, migrant_ui_home_mul,
            migrant_uc_home, migrant_uc_home_mul,
            migrant_u_home, migrant_u_home_mul,
            remain_ui_dest, remain_ui_dest_mul,
            remain_uc_dest, remain_uc_dest_mul,
            remain_u_dest,
            remain_ui_home, remain_ui_home_mul,
            remain_uc_home, remain_uc_home_mul,
            remain_u_home, remain_u_home_mul]

version = 'same_tao'
pi_i_home = [0.1, 1, 5., 10., 16.0, 20., 30., 50.]
pi_i_dest = pi_i_home
pi_c_home = [1.]
pi_c_dest = [.1, 1, 5, 10, 20]
alpha_home = [0., 0.5, 1., 5., 10.]
alpha_dest = alpha_home
lambda_home = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
tao = [0.]
t_home = [3]
t_dest = t_home
rho = [1.]
diffusion_p_all = [0.016]


paras = [pi_i_home,
         pi_i_dest,
         pi_c_home,
         pi_c_dest,
         alpha_home,
         alpha_dest,
         lambda_home,
         rho,
         t_home,
         diffusion_p_all]

# itertools.product stands for many for loops
p_all = list(itertools.product(pi_i_home,
                               pi_i_dest,
                               pi_c_home,
                               pi_c_dest,
                               alpha_home,
                               alpha_dest,
                               lambda_home,
                               rho,
                               t_home,
                               diffusion_p_all))

t0 = time.time()
pool = Pool(50)
result = pool.map(get_accuracy, p_all)
result = np.asarray(result)
pool.close()
pool.join()
t1 = time.time()
print('time: {}'.format(t1 - t0))

result = np.asarray(result)

tp = result[:, 5]
tn = result[:, 4]
fp = result[:, 1]
fn = result[:, 2]

migrant_ui_dest = result[:, 6]
migrant_ui_dest_mul = result[:, 7]
migrant_uc_dest = result[:, 8]
migrant_uc_dest_mul = result[:, 9]
migrant_u_dest = result[:, 10]
migrant_ui_home = result[:, 11]
migrant_ui_home_mul = result[:, 12]
migrant_uc_home = result[:, 13]
migrant_uc_home_mul = result[:, 14]
migrant_u_home = result[:, 15]
migrant_u_home_mul = result[:, 16]
remain_ui_dest = result[:, 17] 
remain_ui_dest_mul = result[:, 18] 
remain_uc_dest = result[:, 19]
remain_uc_dest_mul = result[:, 20]
remain_u_dest = result[:, 21]
remain_ui_home = result[:, 22]
remain_ui_home_mul = result[:, 23]
remain_uc_home = result[:, 24]
remain_uc_home_mul = result[:, 25]
remain_u_home = result[:, 26]
remain_u_home_mul = result[:, 27]

accuracy = np.true_divide((tp + tn), (tp + tn + fp + fn))
print("max accuracy: {:.4f}".format(np.max(accuracy)))
idx_max = np.argsort(accuracy)[-1]
print(p_all[idx_max])

ps = ['pi_i_home',
      'pi_i_dest',
      'pi_c_home',
      'pi_c_dest',
      'alpha_home',
      'alpha_dest',
      'lambda_home',
      'rho',
      't_home',
      'diffusion_p'
      ]

accuracy_top2 = accuracy[np.argsort(accuracy)[::-1]][int(len(accuracy) * 0.02)]

# this will record the index of each value of parameters
pi_i_home_idx = [[] for i in range(len(pi_i_home))]
pi_i_dest_idx = [[] for i in range(len(pi_i_dest))]
pi_c_dest_idx = [[] for i in range(len(pi_c_dest))]
alpha_home_idx = [[] for i in range(len(alpha_home))]
alpha_dest_idx = [[] for i in range(len(alpha_dest))]
lambda_home_idx = [[] for i in range(len(lambda_home))]

i = 0
for z1, pi_i_home_this in enumerate(pi_i_home):
    for z2, pi_i_dest_this in enumerate(pi_i_dest):
        for z3, pi_c_dest_this in enumerate(pi_c_dest):
            for z4, alpha_home_this in enumerate(alpha_home):
                for z5, alpha_dest_this in enumerate(alpha_dest):
                    for z6, lambda_home_this in enumerate(lambda_home):
                        pi_i_home_idx[z1].append(i)
                        pi_i_dest_idx[z2].append(i)
                        pi_c_dest_idx[z3].append(i)
                        alpha_home_idx[z4].append(i)
                        alpha_dest_idx[z5].append(i)
                        lambda_home_idx[z6].append(i)
                        i += 1
t11 = time.time()
print('total time: {:.2f}'.format(t11 - t00))
