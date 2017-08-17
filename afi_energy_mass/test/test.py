import afi_energy_mass.tools.MeteoDataHandler as mdh
from afi_energy_mass.tools.MeteoDataPrediction import MeteoDataPrediction

df_left = mdh.reader(path='rp5.csv', source='rp5')
df_right = mdh.reader(path='ampac.csv', source='ampac')

df_right_av = mdh.average(df_right, source='ampac')



df = mdh.merge(df_left, df_right_av)


mdp = MeteoDataPrediction(df, df_left)
df_predict = mdp.meteo_linear_regression1(df, df_left, x=('T', 'Ff', 'U', 'P'), y=('t_air', 'wind_speed', 'rh', 'pressure'))
print(df_predict)



