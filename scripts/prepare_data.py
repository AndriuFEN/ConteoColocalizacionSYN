def run(descomprimir=True, verbose=False):
        
    import os
    import pandas as pd
    import tqdm
    import shutil
    import zipfile
    import streamlit as st
    
    if verbose: 
        text = 'Trabajando archivo ...'
        print(text)
        st.write(text)

    #%% DEFINIR FUNCIONES

    def descomprimir_zip(archivo_origen, carpeta_destino):

        with zipfile.ZipFile(archivo_origen, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)

        return True

    def SAVE_EXCEL_MULTISHEET(container, path, engine='openpyxl', ind=False):
            
            import numpy as np
            import pandas as pd

            ext = path.split('.')[-1]
            if ext != 'xlsx':
                print('\nERROR: Use .xlsx path...')

            else:

                if type(container) == dict:
                    
                    keys  = list(container.keys())
                    
                    with pd.ExcelWriter(path) as writer:
                        print('Writing to {}'.format(path))
                        for k in keys:
                            print('     ...',k,'sheet')
                            container[k].to_excel(writer, sheet_name=k, index=ind, engine=engine)
                        print('     ... done!')
                
                elif type(container) == list:
                    
                    with pd.ExcelWriter(path) as writer:
                        print('Writing to {}'.format(path))
                        for i in np.arange(len(container)):
                            k = 'sheet' + str(i)
                            print('     ...', k)
                            container[i].to_excel(writer, sheet_name=k, index=ind, engine=engine)
                        print('     ... done!')

    #%% CONFIGURAR ENTORNO

    if verbose: 
        text = '     ... configurando entorno'
        print(text)
        st.write(text)

    archivo_origen_nombre =  os.listdir('origen/')[0]
    archivo_origen = 'origen/' + os.listdir('origen/')[0]
    carpeta_destino = 'input/'

    nombre_muestra = archivo_origen.split('/')[-1].split('.zip')[0]

    nombre_muestra_sin_fecha = nombre_muestra.split(' ')[:2]
    nombre_muestra_sin_fecha = ' '.join([str(x) for x in nombre_muestra_sin_fecha])

    fecha_toma_muestra = nombre_muestra.split(' ')[-1]
    fecha_toma_muestra = fecha_toma_muestra[0:2] + '-' + fecha_toma_muestra[2:4] + '-20' + fecha_toma_muestra[4:7]


    #%% DESCOMPRIMIR ARCHIVO

    if verbose: 
        text = '     ... descomprimiento carpeta origen'
        print(text)
        st.write(text)

    if descomprimir: 

        if len(os.listdir(carpeta_destino)) != 0:
            shutil.rmtree(carpeta_destino)
            os.mkdir(carpeta_destino)

        descomprimir_zip(archivo_origen = archivo_origen, carpeta_destino=carpeta_destino)
    
    carpetas_en_input = os.listdir(carpeta_destino)
    nombre_descomprimido = carpetas_en_input[0]

    if nombre_descomprimido != nombre_muestra:        
        os.rename(carpeta_destino + nombre_descomprimido, carpeta_destino + nombre_muestra)

    carpeta_input = carpeta_destino + nombre_muestra + '/'

    #%% RECONOCER BUCLES

    if verbose: 
        text = '     ... reconociendo bucles'
        print(text)
        st.write(text)

    # reconocer carpetas
    carpetas = [x for x in os.listdir(carpeta_input) if not x.endswith('.nd2')]

    # reconocer condiciones
    condiciones = [x.split(nombre_muestra)[-1][1:] for x in carpetas]
    condiciones = [x.lower().split('cubre')[0][:-1].upper() for x in condiciones]
    condiciones = list(set(condiciones))

    # reconocer cubres de cada condicion
    dicto = {}

    for cond in condiciones:

        cubres = [x.split(nombre_muestra)[-1][1:] for x in carpetas]
        cubres = [x for x in cubres if cond in x]
        cubres = [x.lower().split('cubre')[-1][1:].upper() for x in cubres]
        cubres = [x.split(' ')[0] for x in cubres]
        cubres = list(set(cubres))

        dicto[cond] = cubres

    # reconocer stacks de cada cubre de cada condicion
    stacks_01 = [x.split(nombre_muestra)[-1][1:] for x in carpetas]

    dicto01 = {}

    for cond in condiciones:

        stacks_02 = [x for x in stacks_01 if cond in x]

        dicto02 = {}
        
        for cubre in cubres:
            stacks_03 = [x.lower().split(f'cubre {cubre}')[-1][1:] for x in stacks_02 if f'cubre {cubre}' in x.lower()]
            dicto02[cubre] = stacks_03

        dicto01[cond] = dicto02

    #%% PREPARAR TABLAS

    if verbose: 
        text = '     ... preparando tablas'
        print(text)
        st.write(text)

    carpeta_analisis_ruta = 'input/' + nombre_muestra + '/'
    carpetas_analisis_originales = os.listdir(carpeta_analisis_ruta)

    carpetas_analisis_map = {}
    for c in carpetas_analisis_originales:
        carpetas_analisis_map[carpeta_analisis_ruta + c.lower() + '/'] = carpeta_analisis_ruta + c + '/' 

    print(carpetas_analisis_map)

    tablas = {}

    condiciones = list(dicto01.keys())
    condiciones = sorted(condiciones)

    for t in condiciones:

        if t == 'GRK5 GRK6 TH':
            variables = ['TH', 'GRK5', 'GRK6', 'GRK5/TH', 'GRK6/TH', 'GRK5-GRK6/TH']
        elif t == 'GRK2 GRK3 TH':
            variables = ['TH', 'GRK2', 'GRK3', 'GRK2/TH', 'GRK3/TH', 'GRK2-GRK3/TH']
        elif t == 'Control Negativo':
            variables = ['647', '488', 'Cy3', '488/647', 'Cy3/647', '488-Cy3/647']

        valor0 = None
        valor1 = None
        valor2 = None
        valor3 = None
        valor4 = None
        valor5 = None

        filas = []

        cubres = list(dicto01[t].keys())

        for c in cubres:

            stacks = list(dicto01[t][c])

            for s in stacks:
                
                # busco carpeta
                carpeta_analisis = carpeta_analisis_ruta + nombre_muestra.lower()
                carpeta_analisis = carpeta_analisis + ' ' + t.lower()
                carpeta_analisis = carpeta_analisis + ' ' + 'cubre' + ' ' + c.lower()
                carpeta_analisis = carpeta_analisis + ' ' + s.lower() + '/'

                # leo archivos
                archivos = os.listdir(carpetas_analisis_map[carpeta_analisis])
                archivos = [x for x in archivos if not x.endswith(('.tif', '.csv'))]
                archivos = [x for x in archivos if not 'Segmentacion' in x]
                archivos = sorted(archivos)

                a1 = archivos[0]
                a2 = archivos[1]
                a3 = archivos[2]

                # extraigo informacion
                with open(carpetas_analisis_map[carpeta_analisis] + a1, 'r') as f:
                    a1_text = f.readlines()
                    a1_text = [int(x.replace('\n', '').split(' =')[-1]) for x in a1_text]

                valor0 = a1_text[0]
                valor1 = a1_text[1]
                valor3 = a1_text[2]

                with open(carpetas_analisis_map[carpeta_analisis] + a2, 'r') as f:
                    a2_text = f.readlines()
                    a2_text = [int(x.replace('\n', '').split(' =')[-1]) for x in a2_text]

                valor5 = a2_text[2]

                with open(carpetas_analisis_map[carpeta_analisis] + a3, 'r') as f:
                    a3_text = f.readlines()
                    a3_text = [int(x.replace('\n', '').split(' =')[-1]) for x in a3_text]

                valor2 = a3_text[1]
                valor4 = a3_text[2]

                valores = [valor0, valor1, valor2, valor3, valor4, valor5]

                # creo fila
                fila = {}
                fila['Fecha'] = fecha_toma_muestra
                fila['Stack'] = s
                fila['Cubre'] = int(c)
                fila['Región del cerebro'] = nombre_muestra_sin_fecha

                for v in variables:
                    indice = variables.index(v)
                    fila[v] = valores[indice]

                fila = pd.Series(fila)

                filas.append(fila)

        filas = pd.concat(filas, axis=1).T
        #ilas['Fecha'] = pd.to_datetime(filas['Fecha'], format='%d-%m-%Y')
        filas = filas.sort_values(by=['Cubre', 'Stack'])
        
        tablas[nombre_muestra_sin_fecha + ' ' + t] = filas

    #%% EXPORTAR EXCEL

    if verbose: 
        text = '     ... exportando excel'
        print(text)
        st.write(text)

    cond_outtext = condiciones
    cond_outtext = [x for x in cond_outtext if 'Control' not in x]
    cond_outtext = sorted(cond_outtext)
    cond_outtext = [x.replace(' TH', '') for x in cond_outtext]
    cond_outtext = ' '.join(cond_outtext) + ' TH'

    nombre_archivo = f'Datos {nombre_muestra_sin_fecha} {cond_outtext}'

    filename = f'output/{nombre_archivo}.xlsx'
    SAVE_EXCEL_MULTISHEET(tablas, filename)

