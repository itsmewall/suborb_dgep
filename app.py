from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz

"""
Created on Tue Feb 21 11:52:02 2023
Updated on Jan 07 2025

@author: caduq
"""

app = Flask(__name__)
Rt = 6400000
tz_London = pytz.timezone('Europe/London')

def delta_grau(v, h, tempo):
    v = float(v)
    h = float(h)
    t = float(tempo)
    deltaS = v * t
    delta = deltaS / (Rt + h)
    return np.degrees(delta)

def sub_EM(lat0, long0, H0, V0, Elev, Azi):
    h0 = float(H0)
    v0 = float(V0)
    elev = float(Elev)
    azi = float(Azi)
    vNorte = v0 * np.cos(np.radians(elev)) * np.cos(np.radians(azi))
    vLeste = v0 * np.cos(np.radians(elev)) * np.sin(np.radians(azi))
    V0z = v0 * np.sin(np.radians(elev))
    passo = 1
    g = 9.81
    t = 0
    plotLats = []
    plotLongs = []
    plotZ = []
    tempo = []
    Z = h0
    while Z >= 0:
        if plotLats == []:
            lat = lat0
            long = long0
        else:
            lat = plotLats[-1] + delta_grau(vNorte, Z, passo)
            long = plotLongs[-1] + delta_grau(vLeste, Z, passo)
        Z = h0 + V0z * t - (g / 2) * (t ** 2)
        if Z > 0:
            plotLats.append(lat)
            plotZ.append(Z)
            plotLongs.append(long)
            tempo.append(t)
        t += passo

    resultados = [tempo, plotLats, plotLongs, plotZ]
    df = pd.DataFrame(resultados).T
    df.columns = ["Tempo", "Latitude", "Longitude", "Altitude"]
    df['Tempo'] = df['Tempo'].astype(int)
    reference_time = datetime.utcnow()
    df['Tempo_ISO8601'] = (reference_time + pd.to_timedelta(df['Tempo'], unit='s')).astype(str)
    return df[['Latitude', 'Longitude', 'Altitude', 'Tempo_ISO8601']]

@app.route('/', methods=['GET', 'POST'])
def index():
    lat0 = -2
    long0 = 0
    h0 = 0
    v0 = 2079.90371637393
    elev = 87.3
    azi = 0

    if request.method == 'POST':
        lat0 = float(request.form['lat0'])
        long0 = float(request.form['long0'])
        h0 = float(request.form['h0'])
        v0 = float(request.form['v0'])
        elev = float(request.form['elev'])
        azi = float(request.form['azi'])

    cesium_ion_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjOWE3NjlkYy05MzcxLTQzOTEtODEzYS1iN2VjOGQzNTQwYzciLCJpZCI6MTk3NDUzLCJpYXQiOjE3MzYyNzg2MjB9.3TiujUpyH9xoNRM3H1GjdrEtpdYNY1dXUiJT2yLnKJ4"
    positions = sub_EM(lat0, long0, h0, v0, elev, azi).to_dict(orient='records')

    return render_template('index.html', cesium_ion_token=cesium_ion_token, positions=positions,
                           lat0=lat0, long0=long0, h0=h0, v0=v0, elev=elev, azi=azi)

if __name__ == '__main__':
    app.run(debug=True)