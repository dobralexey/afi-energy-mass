import numpy as np
import pandas as pd

from afi_energy_mass.tools import Rp5Dicts


class MeteoDataReader:
    def __init__(self, path, source, average=True):
        self.path = path
        self.source = source
        self.average = average


    def rp5(self):

        # Initial parameters
        sep = ';'
        quotechar = '"'
        skiprows = 6
        header = 0

        # Read csv functuion
        df = pd.read_csv(self.path, sep=sep, quotechar=quotechar, skiprows=skiprows, header=header)

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

        if self.average == True:

            df['Date'] = pd.to_datetime(df.index.date)
            df = df.loc[:, ['Date', 'T', 'P', 'U', 'Ff', 'Tn', 'Tx', 'N', 'Nh', 'Cl', 'Cm', 'Ch']]
            df_group = df.groupby('Date').agg({np.mean})
            #df_group['DOY'] = pd.to_numeric(group.index.strftime('%j'))
            df_group['Date'] = df_group.index

            return df_group

        else:
            return df

    def fluxnet(self):

        sep = ','
        quotechar = '"'
        skiprows = 0
        header = 0

        # Read csv functuion
        df = pd.read_csv(self.path, sep=sep, quotechar=quotechar, skiprows=skiprows, header=header, na_values=-9999)
        df['Datetime'] = pd.to_datetime(df['TIMESTAMP_START'], format='%Y%m%d%H%M')
        df = df.set_index(df['Datetime'])

        if self.average == True:

            df['Date'] = pd.to_datetime(df.index.date)
            df_group = df.groupby('Date').agg({np.mean})
            df_group['Date'] = df_group.index

            return df_group

        else:
            return df

    def mos(self):

        sep = ';'
        quotechar = '"'
        skiprows = 1
        header = None

        # Read csv functuion
        df = pd.read_csv(self.path, sep=sep, quotechar=quotechar, skiprows=skiprows, header=header)

        df.columns = ['Initial_Date', 'Time', 'T_soil', 'T_a',
                      'RH', 'FAR', 'Rn', 'PP',
                      'Wind', 'Uv']

        ser = pd.Series([0, 10, 20, 30, 40, 50])
        ser = pd.concat([ser] * (len(df['Initial_Date']) // 6))
        ser.index = df.index
        df['minute'] = ser
        df['Datetime'] = pd.to_datetime(df['Initial_Date'])
        td = df.apply(lambda x: pd.Timedelta(hours=x['Time'], minutes=x['minute']), axis=1)
        df['Datetime'] = df['Datetime'] + td


        if self.average == True:

            df['Date'] = pd.to_datetime(df.index.date)
            df_group = df.groupby('Date').agg({np.mean})
            df_group['Date'] = df_group.index

            return df_group

        else:
            return df

    def ampac(self):

        # Initial parameters
        sep = ';'

        # Read csv functuion
        df = pd.read_csv(self.path, sep=sep, decimal=',', na_values=9999)

        df.index = df['date']
        del df['date']
        df['Datetime'] = df.index

        # It converts string datetime to python datetime type.

        if self.average == True:

            date = (pd.to_datetime(df['Datetime']))
            date = date.apply(lambda x: pd.datetime(x.year, x.month, x.day, x.hour, (x.minute // 10) * 10, ))
            df['Datetime'] = date
            df_group = df.groupby('Datetime').mean()
            df_group['Datetime'] = df_group.index

            return df_group

        else:
            return df

    def run(self):

        if self.source == 'rp5':
            df = self.rp5()
        elif self.source == 'fluxnet':
            df = self.fluxnet()
        elif self.source == 'mos':
            df = self.mos()
        elif self.source == 'ampac':
            df = self.ampac()
        else:
            print('Unknown file source format')
            df = None

        return df



if __name__=='__main__':
    mdr_tst = MeteoDataReader(path='../test/ampac.csv', source='ampac')
    df = mdr_tst.run()
    print(df)