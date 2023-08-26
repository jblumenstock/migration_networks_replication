import pandas as pd 
import random

df = pd.read_csv('data/support_dest_for_regression_22degree.csv')
users_unique = list(df.user.unique())
random.seed(1)
users_10pct = random.sample(users_unique, int(len(users_unique) * 0.1))
sampled_df = df[df.user.isin(users_10pct)]
sampled_df.to_csv('data/support_dest_for_regression_22degree_sampled_10pct.csv', index=None)

df = pd.read_csv('data/information_dest_for_regression_22degree.csv')
users_unique = list(df.user.unique())
random.seed(1)
users_10pct = random.sample(users_unique, int(len(users_unique) * 0.1))
sampled_df = df[df.user.isin(users_10pct)]
sampled_df.to_csv('data/information_dest_for_regression_22degree_sampled_10pct.csv', index=None)

df = pd.read_csv('data/cluster_dest_for_regression_22degree.csv')
users_unique = list(df.user.unique())
random.seed(1)
users_10pct = random.sample(users_unique, int(len(users_unique) * 0.1))
sampled_df = df[df.user.isin(users_10pct)]
sampled_df.to_csv('data/cluster_dest_for_regression_22degree_sampled_10pct.csv', index=None)
