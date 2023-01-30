# ===========================================================================================
# Objeto........: fnc_zip_files
# Data Criacao..: 27/01/2023
# Descricao.....: Zipa arquivos e efetua upload para o bucket
# ===========================================================================================
import io 
import datetime, time
from utils import Blob
from google.cloud.storage.blob import BlobWriter
from google.cloud.storage import Client
from threading import Thread
from queue import Queue, Empty
import smart_open
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from google.cloud.storage import Client

import functions_framework

start_time = time.time()

def download_thread(queue, bucket, split_list):
    """Gera um iterador de download bucket
    Args:
        bucket (_type_): _description_
        split_list (_type_): _description_
    Yields:
        stream: stream de dados
    """
    print('[INFO] - Iniciando processo download partes')
    for chunk in split_list:
      blob_name=chunk['blob'].split('/')[-1]
      content = bucket.download_by_parts(chunk)

      #if chunk['start'] == 0:
      #    print('[INFO] - Download arquivo {} efetuado'.format(blob_name))
      queue.put(content)

    queue.put(None) 
    print('[INFO] - Processo download partes concluido')

def upload_thread(queue, ouput_path, filename, total_splits):
    print('[INFO] - Iniciando processo upload partes')
    client = Client()
    ratio = 0
    with smart_open.open(f"{ouput_path}/{filename}.zip", 'wb', transport_params=dict(client=client)) as fout:
      with ZipFile(fout, 'w', compression=ZIP_DEFLATED) as zip:
        with zip.open(name=f"{filename}.csv",mode='w',force_zip64=True) as z:
          while True:
            try:
              content = queue.get(block=False)
              print('[INFO] - {:.2f}% Concluido'.format((ratio/total_splits)*100))
              if content is None:
                break
              z.write(content)
              ratio += 1
            except Empty:
              time.sleep(0.5)
              continue
    print('[INFO] - Processo upload partes concluido')

@functions_framework.http
def main(request):
  print(f'{datetime.datetime.now()}')

  # Variaveis de Entrada
  GCS_INPUT  = request.json["gcs_input"]
  GCS_OUTPUT = request.json["gcs_output"]
  FILENAME = request.json["filename"]
  QUEUE_SIZE = request.json["queue_size"]

  # Variaveis de Input
  INPUT_BUCKET_NAME = GCS_INPUT.split("/")[2]
  PREFIX = GCS_INPUT.split('/',3)[3].replace('*','') 

  SPLIT_SIZE = 100 # MB

  print("[INFO] - Conectando bucket")
  input_bucket: Blob = Blob(INPUT_BUCKET_NAME)        # Conecta bucket origem
  blob_files: list = input_bucket.lista_blobs(PREFIX) # Lista arquivos bucket
  downloads = [] # Fila de downloads

  if blob_files:
    # Definindo divizoes para download
    print('[INFO] - Gerando lista segmentada de downloads')
    for blob_path in blob_files:
      blob_size = input_bucket.get_size(blob_path)

      split_number = int((blob_size/1024**2)/SPLIT_SIZE) if (blob_size/1024**2) > SPLIT_SIZE else 1 
      split_list = Blob.split_byte_size(size=blob_size,blob_path=blob_path,split_number=split_number)
      downloads.extend(split_list)

    print('[INFO] - Gerado lista de {} elementos'.format(len(downloads)))

    total_splits = len(downloads)
    # Definindo Concorrencia
    queue = Queue(maxsize=QUEUE_SIZE)

    try:
        download_process = Thread( target=download_thread, args=(queue, input_bucket, downloads ))
        download_process.start()

        upload_process = Thread( target=upload_thread, args=(queue, GCS_OUTPUT, FILENAME, total_splits ))
        upload_process.start()
    
        download_process.join()
        upload_process.join() 
    except:
        return abort(500)
  else:
    print('[INFO] - Origem informada nada tem arquivos')
  
  print('[INFO] - Job Concluido - em {:.2f} segundos'.format(time.time() - start_time))
  return "[INFO] - Job concluido"