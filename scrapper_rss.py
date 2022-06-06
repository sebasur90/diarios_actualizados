import os
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from diarios_rss import diarios
import agrega_sentimientos
import datetime as dt


class Scrapper:

    def __init__(self):
        self.noticias = {}

    def recorre_diarios(self):
        contador = 0
        for diario in diarios:
            try:
                print(
                    f"Obteniendo noticias de {diarios[diario]['diario']} ,seccion {diarios[diario]['seccion']} ")
                #st.session_state['muestra_progreso'] = f"{diarios[diario]['diario']} -- > seccion {diarios[diario]['seccion']} "
                # st.write(st.session_state['muestra_progreso'])
                time.sleep(0.5)
                url = requests.get(diarios[diario]['rss'])

                soup = BeautifulSoup(url.content, "xml")

                items_pagina = soup.find_all('item')

                for item in range(len(items_pagina)):
                    noticia = {}
                    noticia['diario'] = diarios[diario]['diario']
                    noticia['seccion'] = diarios[diario]['seccion']
                    noticia['titulo'] = items_pagina[item].title.text
                    if items_pagina[item].description == None or items_pagina[item].description == " " or items_pagina[item].description == "<NA>":
                        if diarios[diario]['diario'] == 'Perfil':
                            noticia['descripcion'] = items_pagina[item].description.text.split(
                                "</p>")[1].split('<a href')[0]
                        if diarios[diario]['diario'] == 'La_izquierda_diario':
                            noticia['descripcion'] = items_pagina[item].description.text.split("<p>")[
                                1].split('</p>')[0]
                        else:
                            noticia['descripcion'] = items_pagina[item].title.text
                    else:
                        if diarios[diario]['diario'] == 'Perfil':
                            noticia['descripcion'] = items_pagina[item].description.text.split(
                                "</p>")[1].split('<a href')[0]
                        if diarios[diario]['diario'] == 'La_izquierda_diario':
                            noticia['descripcion'] = items_pagina[item].description.text.split("<p>")[
                                1].split('</p>')[0]
                        else:
                            noticia['descripcion'] = (
                                items_pagina[item].description.text)

                    self.noticias[contador] = noticia
                    contador = contador + 1
            except:
                pass

    def formateo_noticias(self):
        dataframe_noticias = pd.DataFrame(self.noticias).transpose()
        dataframe_noticias = dataframe_noticias.drop_duplicates(subset=[
                                                                'titulo'])
        return dataframe_noticias

    def sentimientos(self, dataframe_noticias):

        dia_str = str(dt.datetime.today().date())
        noticias = agrega_sentimientos.genera_excel_sentimientos(
            dataframe_noticias)
        noticias.to_csv(
            f"diarios/noticias_con_sentimientos_{dia_str}.csv", index=False)

    def apila_diarios_historicos(self):
        lista_diarios = os.listdir('diarios')
        print(lista_diarios)
        lista_diarios.remove('diarios_historicos.csv')
        dataframes = []
        dataframes.append(pd.read_csv("diarios/diarios_historicos.csv"))
        for diarios in lista_diarios:
            dataframes.append(pd.read_csv("diarios/"+diarios))
        apilados = pd.concat(dataframes, axis=0)
        apilados = apilados.drop_duplicates(subset=['titulo'])
        apilados.to_csv(f"diarios/diarios_historicos.csv", index=False)

    def agrega_fecha_hoy(self):
        fechas = pd.read_csv("fechas.csv")
        dia_str = str(dt.datetime.today().date())
        fechas = fechas.append({'dia': dia_str}, ignore_index=True)
        fechas.to_csv("fechas.csv", index=False)

    def run(self):
        self.recorre_diarios()
        dataframe_noticias = self.formateo_noticias()
        print(dataframe_noticias)
        self.sentimientos(dataframe_noticias)
        self.apila_diarios_historicos()
        self.agrega_fecha_hoy()


if __name__ == '__main__':
    scrapper = Scrapper()
    scrapper.run()
