import pandas as pd

from afi_energy_mass.dicts import Rp5Dicts


def rp5(path):
    '''
    :param args: List of the columns which will stay in DataFrame
    :return: Pandas DataFrame
    '''

    # Initial parameters
    sep = ';'
    quotechar = '"'
    skiprows = 6
    header = 0

    # Read csv functuion
    df = pd.read_csv(path, sep=sep, quotechar=quotechar, skiprows=skiprows, header=header)

    # It is our future header
    new_col = df.columns[1:]
    df.drop(df.columns[len(df.columns) - 1], axis=1, inplace=True)
    df.columns = new_col

    # It converts string datetime to python datetime type
    df.index = pd.to_datetime(df.index, dayfirst=True)
    df.sort_index(inplace=True)
    df['Datetime'] = df.index

    # Replace word description to numeric or string values from dicts
    df['N'] = df['N'].replace(Rp5Dicts.N_DICT)
    df['Nh'] = df['Nh'].replace(Rp5Dicts.N_DICT)
    df['H'] = df['H'].replace(Rp5Dicts.H_DICT)
    df['Cl'] = df['Cl'].replace(Rp5Dicts.CL_DICT)
    df['Cm'] = df['Cm'].replace(Rp5Dicts.CM_DICT)
    df['Ch'] = df['Ch'].replace(Rp5Dicts.CH_DICT)

    return df


def fluxnet(path):

    sep = ','
    quotechar = '"'
    skiprows = 0
    header = 0

    # Read csv functuion
    df = pd.read_csv(path, sep=sep, quotechar=quotechar, skiprows=skiprows, header=header, na_values=-9999)
    df['Datetime'] = pd.to_datetime(df['TIMESTAMP_START'], format='%Y%m%d%H%M')
    df = df.set_index(df['Datetime'])

    return df


def mos(path):

    sep = ';'
    quotechar = '"'
    skiprows = 1
    header = None

    # Read csv functuion
    df = pd.read_csv(path, sep=sep, quotechar=quotechar, skiprows=skiprows, header=header)

    df.columns = ['Initial_Date', 'Time', 'T_soil', 'T_a',
                  'RH', 'FAR', 'Rn', 'PP',
                  'Wind', 'Uv']

    ser = pd.Series([0, 10, 20, 30, 40, 50])
    ser = pd.concat([ser] * (len(df['Initial_Date']) // 6))
    ser.index = df.index
    df['minute'] = ser
    df['Date'] = pd.to_datetime(df['Initial_Date'], dayfirst=True)
    td = df.apply(lambda x: pd.Timedelta(hours=x['Time'], minutes=x['minute']), axis=1)
    df['Datetime'] = df['Date'] + td
    df = df.set_index(['Datetime'])

    return df



def ampac(path):

    # Initial parameters
    sep = ';'

    # Read csv functuion
    df = pd.read_csv(path, sep=sep, decimal=',', na_values=9999)

    df.index = df['date']
    del df['date']
    df['Datetime'] = df.index

    return df


def reader(path, source):

    if source == 'rp5':
        df = rp5(path)
    elif source == 'fluxnet':
        df = fluxnet(path)
    elif source == 'mos':
        df = mos(path)
    elif source == 'ampac':
        df = ampac(path)
    else:
        print('Unknown file source format')
        df = None

    return df

def columns_filter(df, *args):

    columns = args
    if len(columns) > 0:
        df = df.col[:, columns]

    return df

def average(df, source):

    if source == 'rp5':
        df['Date'] = pd.to_datetime(df.index.date)
        df = df.loc[:, ['Date', 'T', 'P', 'U', 'Ff', 'Tn', 'Tx', 'N', 'Nh', 'Cl', 'Cm', 'Ch']]
        df_group = df.groupby('Date').mean()
        # df_group['DOY'] = pd.to_numeric(group.index.strftime('%j'))
        df_group['Date'] = df_group.index

        return df_group


    elif source == 'fluxnet':
        df['Date'] = pd.to_datetime(df.index.date)
        df_group = df.groupby('Date').mean()
        df_group['Date'] = df_group.index

        return df_group

    elif source == 'mos':
        df_group = df.groupby('Date').mean()
        return df_group

    elif source == 'ampac':
        date = (pd.to_datetime(df['Datetime']))
        date = date.apply(lambda x: pd.datetime(x.year, x.month, x.day, x.hour, (x.minute // 10) * 10, ))
        df['Datetime'] = date
        df_group = df.groupby('Datetime').mean()
        df_group['Datetime'] = df_group.index

        return df_group

def merge(*args, how='inner', on='Datetime'):
    '''
    This function allows to merge Pandas DataFrames with meteorological data.
    The merge occurs on the "on" field (default is 'Datetime')
    :param how: how make merge inner, outer or left, right
    :param on: it is a field on which DataFrames is merged
    :return: Combined Pandas DataFrame
    '''

    dfs = args

    df = dfs[0]    #Initial df assignment as fisrt DataFrame

    for i in range(1,len(dfs)):
        df = df.merge(dfs[i], how=how, on=on)

    return df

def concat(*args, axis=0):
    '''
    This function allows to concatenate DataFrames with meteorological data.
    The merge occurs on the datetime field
    :param axis: axes on which DataFrame is concatenated (0 - by row, 1 - by columns)

    :return: Combined pandas DataFrame
    '''

    dfs = args
    df = pd.concat(dfs, axis=axis)
    return df

