# ===========================================================================================
# Objeto........: fnc_zip_files
# Data Criacao..: 09/01/2023
# Descricao.....: Zipa arquivos e efetua upload para o bucket
# ===========================================================================================
import io 
import datetime, time
from zipfile import ZipFile, ZIP_DEFLATED
import sys
from utils import Blob
import logging

import functions_framework

start_time = time.time()

@functions_framework.http
def main(request):
  print('main')
  print(f'{datetime.datetime.now()}')

  # Variaveis de Entrada
  GCS_INPUT  = request.json["gcs_input"]
  GCS_OUTPUT = request.json["gcs_output"]
  FILENAME = request.json["filename"]

  # Variaveis de Input
  INPUT_BUCKET_NAME = GCS_INPUT.split("/")[2]
  PREFIX = GCS_INPUT.split('/',3)[3].replace('*','')

  # Variaveis de Output
  OUTPUT_BUCKET_NAME = GCS_OUTPUT.split("/")[2]
  FILE_PATH = GCS_OUTPUT.split('/',3)[3] if GCS_OUTPUT.endswith("/") else GCS_OUTPUT.split('/',3)[3] + '/'

  print("Connecting to input bucket")
  input_bucket: Blob = Blob(INPUT_BUCKET_NAME)        # Conecta bucket origem
  blob_files: list = input_bucket.lista_blobs(PREFIX) # Lista arquivos bucket
  
  # Verificando se existem arquivos no bucket passado
  if blob_files:
    
    output_bucket: Blob = Blob(OUTPUT_BUCKET_NAME,f"{FILE_PATH}{FILENAME}.zip")  # Conecta ao blob destino

    archive = io.BytesIO()  # Inicializando arquivo em memoria
    
    # Inicializando escrita zip 
    with ZipFile(archive,"w",compression=ZIP_DEFLATED) as zip_file:
      
      # Abrindo arquivo dentro do zip
      with zip_file.open(f"{FILENAME}.csv","w", force_zip64=True) as zip_archive:
        for blob_path in blob_files:

          blob_name= blob_path.split('/')[-1]
          blob_size = input_bucket.get_size(blob_path)
          print(f"[INFO] - Download file {blob_name}")

          # Identifica quantas vezes o arquivo deve ser divido
          split_size = 120 # Tamanho em MB
          split_number = int((blob_size/1024**2)/split_size) if (blob_size/1024**2) > split_size else 1 
          split_list = Blob.split_byte_size(size=blob_size,blob_path=blob_path,split_number=split_number)

          for idx, chunk_blob in enumerate(split_list):
            chunk_downloaded = input_bucket.download_by_parts(input=chunk_blob)
            print(f"[INFO] - Download file {blob_name} parte {idx+1} de {len(split_list)}")

            zip_archive.write(chunk_downloaded) # Escreve no arquivo em memoria

            print(f"[INFO] - Download file {blob_name} {idx+1} of {len(split_list)}")
            time.sleep(0.05)

    archive.seek(0) # Acum
    output_bucket.upload_bytes_to_bucket(file_buffer=archive,content_type="application/zip")
    archive.close() # Apagando arquivo em memoria
  else:
    print('[INFO] - Arquivo(s) não encontrado(s)')
  
  print("[INFO] - Cloud Run concluida em {:.2f} segundos".format(round(time.time() - start_time,2)))
  return "[INFO] - Cloud Function concluida"