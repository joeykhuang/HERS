import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import plotly.plotly as py
import plotly.graph_objs as go
import plotly
import dash
import dash_core_components as dcc
import dash_html_components as html
plotly.tools.set_credentials_file(username='straightsoup', api_key='aKCQfFygLpwLkuExldXI')

gf = pd.read_csv('Data/RankedHospitalInfo1.csv')
ziplocs = pd.read_csv('Data/zipcode.csv')
df = gf.copy()
df.set_index(['State', 'City', 'Hospital Name'], inplace=True)


def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

def getHosRankings(usrMort, usrRatings, usrSaf, usrSpen, hosDf1):
    hosDf = hosDf1.copy()
    usrSum = float(usrMort + usrRatings + usrSaf + usrSpen)
    usrMort /= usrSum
    usrRatings /= usrSum
    usrSaf /= usrSum
    usrSpen /= usrSum

    hosDf['TotalRanking'] = 0
    for row in hosDf.itertuples():
        hosDf.loc[row.Index, 'TotalRanking'] = row[4] * usrMort + \
            row[5] * usrRatings + row[6] * usrSaf + row[7] * usrSpen
    hosDf['TotalRankingReranked'] = 0
    l_min = hosDf['TotalRanking'].min()
    l_max = hosDf['TotalRanking'].max()
    l_range = l_max - l_min
    if hosDf.iat[0, 10] != 0:
        for row in hosDf.itertuples():
            hosDf.loc[row.Index, 'TotalRankingReranked'] = 10 * (float(row[11]) - l_min) / l_range
    else:
        for row in hosDf.itertuples():
            hosDf.loc[row.Index, 'TotalRankingReranked'] = 10 * (float(row[10]) - l_min) / l_range
    hosDf.drop(['TotalRanking'], axis = 1)
    return hosDf


def getHosDistance(usrzip, numHospitals, hosDf1):
    hosDf = hosDf1.copy()
    for row in ziplocs.itertuples():
        if row[1] == usrzip:
            userState = row[3]
            userCity = row[2]
            userLat = row[4]
            userLon = row[5]
    stateHospitals = hosDf.xs(userState).copy()
    stateHospitals.loc[:, 'Distance'] = None
    for row in stateHospitals.itertuples():
        if row[8] is not None:
            stateHospitals.loc[row.Index, 'Distance'] = haversine(userLon, userLat, row[9], row[8])
    stateHospitals = stateHospitals.sort_values(['Distance'], ascending=True)
    if numHospitals <= len(stateHospitals) and numHospitals > 0:
        closeHospitals = stateHospitals[:numHospitals]
    return closeHospitals

app = dash.Dash()
app.layout = html.Div('Hi')
if __name__ == '__main__':
    app.server.run(port=3000, host='127.0.0.1')
