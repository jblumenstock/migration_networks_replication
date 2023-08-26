# convert the regression input data
# to the format ''information.1', 'information.2', ...'
from turicreate import SFrame
import turicreate.aggregate as agg
import pandas as pd


# destination
def get_v_dest(x):
    # with the first one always zero to make name easier
    r = [0.0] * 23
    d = int(x['d'])
    r[d] = x['v']
    return r


def get_d3_dest(x):
    r = [0.0] * 23
    d = int(x['d'])
    r[d] = x['d3_degree']
    return r


def get_infor_dest(x):
    r = [0.0] * 23
    d = int(x['d'])
    r[d] = x['l']
    return r


def get_v_dest_support(x):
    r = [0.0] * 23
    d = int(x['d'])
    r[d] = x['s']
    return r


def get_d3_d2_dest(x):
    r = [0.0] * 51
    l = int(x['information'])
    l = int(l / 10 + 1)
    r[l] = x['d3_degree']
    return r


variables = ['information', 'support', 'cluster']

for v in variables:
    df = SFrame.read_csv('data/' + v + '_dest_for_regression.csv')
    df = df.fillna('d', 0)
    df = df.fillna('v', 0)
    df = df[df['d'] <= 22]
    r = df.apply(lambda x: get_v_dest(x))
    r1 = r.unpack(column_name_prefix=v)
    r2 = df.add_columns(r1)
    r3 = r2.remove_column(v + '.0')
    r3.export_csv('data/'+v + '_dest_for_regression_22degree.csv')

