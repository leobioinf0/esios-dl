
from esiosdl import download_values
import datetime

if __name__ == '__main__':
    tkn = '615e6d8c80629b8eef25c8f3d0c36094e23db4ed50ce5458f3462129d7c46dba'
    inicio = datetime.datetime(2020, 1, 1, 1, 0, 0).strftime('%Y-%m-%dT%H:%M:%S')
    final = datetime.datetime(2020, 1, 2, 1, 0, 0).strftime('%Y-%m-%dT%H:%M:%S')
    indicadores = list(range(600, 618))
    df = download_values(indicadores, inicio, final, tkn)
    print(df)