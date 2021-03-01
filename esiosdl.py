import urllib
import json
import seaborn as sns
import pandas as pd
import re

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
pd.set_option("display.max_rows", 100)


def remove_tags(text):
    ta = re.compile(r'&aacute;').sub('á', text)
    te = re.compile(r'&eacute;').sub('é', ta)
    ti = re.compile(r'&iacute;').sub('í', te)
    to = re.compile(r'&oacute;').sub('ó', ti)
    tu = re.compile(r'&uacute;').sub('ú', to)
    tn = re.compile(r'&ntilde;').sub('ñ', tu)
    tnbsp = re.compile(r'&nbsp;').sub(' ', tn)
    return re.compile(r'<[^>]+>|\n|\r').sub('', tnbsp)


def mk_head(token):
    headers = dict()
    headers['Accept'] = 'application/json; application/vnd.esios-api-v1+json'
    headers['Content-Type'] = 'application/json'
    headers['Host'] = 'api.esios.ree.es'
    headers['Authorization'] = 'Token token=\"' + token + '\"'
    headers['Cookie'] = ''
    return headers


def download_indicators(token):
    print("Downloading indicators")
    headers = mk_head(token)
    url = 'https://api.esios.ree.es/indicators'
    resultado_indicadores = list()
    solicitud_indicadores = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(solicitud_indicadores) as respuesta:
        try:
            json_data = respuesta.read()
        except:
            json_data = respuesta.readall()
    resultado_indicadores.extend(json.loads(json_data)['indicators'])
    ind_df = pd.DataFrame(resultado_indicadores)
    ind_df = ind_df.set_index('id')
    ind_df = ind_df.sort_index()
    ind_df['description'] = ind_df['description'].apply(lambda x: remove_tags(x))
    ind_df['publication'] = ind_df['description'].apply(lambda x: x.rsplit("Publicación:")[1].lstrip().capitalize())
    ind_df['description'] = ind_df['description'].apply(lambda x: x.rsplit("Publicación:")[0])

    return ind_df


def download_values(indicators, start, end, tk):
    print("Downloading values")
    headers = mk_head(tk)
    df_list = list()
    for indicador in indicators:
        url = 'https://api.esios.ree.es/indicators/' + str(
            indicador) + '?start_date=' + start + '&end_date=' + end + '&geo_agg=sum&geo_ids=3&time_trunc=hour&time_agg=&locale=es'
        solicitud = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(solicitud) as respuesta:
                try:
                    json_data = respuesta.read().decode('utf-8')
                except:
                    json_data = respuesta.readall().decode('utf-8')
            resultado = json.loads(json_data)
            nombre_indicador = resultado['indicator']['name'].replace(' ', '_')
            id = resultado['indicator']['id']

            if resultado['indicator']['values']:
                print(id, "\t", nombre_indicador)
                if resultado['indicator']['disaggregated']:
                    df = pd.DataFrame(resultado['indicator']['values'])
                    df = df[df.geo_id == 3][['datetime', 'value']]
                else:
                    df = pd.DataFrame(resultado['indicator']['values'])
                    df = df[['datetime', 'value']]
                df = df.set_index('datetime')
                df.index = pd.to_datetime(df.index, utc=True)
                df = df.asfreq("h", fill_value=None)
                df.columns = [nombre_indicador]
                df_list.append(df)
            else:
                print(id, "\t", nombre_indicador, "NO VALUES")
        except:
            print(str(indicador), "\t", "EXCEPT")
            continue
    try:
        df = df_list[0].join(df_list[1:])
        print("\nDESCRIPCIÓN:")
        print(df.describe().T.round())
        print("\nINFORMACIÓN:")
        print(df.info(verbose=True), "\n")
        return df

    except:
        return None
