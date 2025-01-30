import os
import sys
import io
import gdown
import traceback
import streamlit as st
from scripts import prepare_data

# Inicializar la variable de estado
if "download_flag" not in st.session_state:
    st.session_state.download_flag = False

if "prepared_flag" not in st.session_state:
    st.session_state.prepared_flag = False

#if os.getcwd().replace('\\', '/').split('/')[-1] != 'python':
#    os.chdir('python/')

st.image(".configs/banner.png")

st.subheader('CONTEO DE COLOCALIZACION:rocket::moon:')

#%% Configurar carpetas

basefolder = ''
ofolder = basefolder + 'origen/'
infolder = basefolder + 'input/'
outfolder = basefolder + 'output/'

def remove_gitkeep(folder):
    
    for f in os.listdir(folder):
        if f == '.gitkeep':
            os.remove(folder + f)
            break

    return True

remove_gitkeep(ofolder)
remove_gitkeep(infolder)
remove_gitkeep(outfolder)

#%% Cargar datos

# url = 'https://drive.google.com/file/d/1PJlQGSkdYcaaK6B8Bhf1Hs2dzo-I00WI/view?usp=drive_link'
# nombre_archivo = 'SYN09 DS 080124'

url = st.text_input("Url de Google Drive", "https://drive.google.com/file/d/...")
nombre_archivo = st.text_input("Nombre del Archivo", "miarchivo.zip")

def download_data(output_folder, url, nombre_archivo):
    
    # corrijo la url
    file_id = url.split('d/')[-1].split('/view')[0]
    url_fix = f'https://drive.google.com/uc?id={file_id}&confirm=t'

    # corrijo el nombre
    if not nombre_archivo.endswith('.zip'):
        nombre_archivo += '.zip'

    # decargo archivo
    savename = f'{output_folder}{nombre_archivo}'
    gdown.download(url_fix, savename, quiet=False)

    return savename

#st.button("Reset", type="primary")
if st.button("Download"):

    if os.path.exists(ofolder + nombre_archivo):
        st.write('Archivo ya descargado!')
        st.session_state.download_flag = True

    if st.session_state.download_flag == False:

        with st.spinner('Descargando...'):
            try: 
                download_data(ofolder, url, nombre_archivo)
                st.session_state.download_flag = True
                st.success('       ... done!')
            except Exception as e:
                st.error('       ... error!')
                st.text(traceback.format_exc())

if st.session_state.download_flag:

    on = st.toggle("Carpeta ya descomprimida")

    if st.button("Preparar datos"):

        with st.spinner('Preparando...'):
            
            try: 
                if on == False:
                    prepare_data.run(True, True)
                else:
                    prepare_data.run(False, True)
            
                st.session_state.prepared_flag = True 

                st.success('       ... done!')
                
            except Exception as e:

                st.error('       ... error!')
                st.text(traceback.format_exc())


    if st.session_state.prepared_flag:
        
        archivo_excel = outfolder + os.listdir(outfolder)[-1]

        with open(archivo_excel, "rb") as f:

            # Botón de descarga
            st.download_button(
                label="📥 Descargar Excel",
                data=f,
                file_name=os.listdir(outfolder)[-1],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    