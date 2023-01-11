# ===========================================================================================
# Objeto........: fnc_zip_files
# Data Criacao..: 09/01/2023
# Descricao.....: Zipa arquivos e efetua upload para o bucket
# ===========================================================================================
from io import BytesIO
from utils import Blob, zip_file, merge_files
from tempfile import mkdtemp
from shutil import rmtree
import functions_framework

@functions_framework.http
def main(request):

  # Variaveis
  # GCS_INPUT  = "gs://banco-bv-sandbox/test/input/students"
  # GCS_OUTPUT = "gs://banco-bv-sandbox/test/output/"
  GCS_INPUT  = request.json["gcs_input"]
  GCS_OUTPUT = request.json["gcs_output"]

  INPUT_BUCKET_NAME = GCS_INPUT.split("/")[2]
  PREFIX = GCS_INPUT.split('/',3)[3].replace('*','')

  OUTPUT_BUCKET_NAME = GCS_OUTPUT.split("/")[2]
  FILE_PATH = GCS_OUTPUT.split('/',3)[3]
  FILENAME = PREFIX.split('/')[-1]

  LOCALPATH = mkdtemp(dir='/tmp/') # Cria diretorio temporario

  # Fluxo Principal
  input_bucket: Blob = Blob(INPUT_BUCKET_NAME)        # Conecta bucket origem
  output_bucket: Blob = Blob(OUTPUT_BUCKET_NAME)      # Conecta bucket destino
  blob_files: list = input_bucket.lista_blobs(PREFIX) # Lista arquivos bucket
  
  if blob_files:
    for blob in blob_files:
      blob_buffer = BytesIO(input_bucket.download_blob(LOCALPATH, blob)) # Baixa arquivos diretorio temporario
      # merge_files(LOCALPATH, blob)                         # Merge dos arquivos csv em um 
    
      zip_buffer = zip_file(LOCALPATH,FILENAME,blob_buffer)     # Gera buffer arquivos zipados
      output_bucket.upload_blob(FILENAME,FILE_PATH,zip_buffer)  # Efetua upload arquivos zipados

  else:
    print('[INFO] - Arquivo(s) não encontrado(s)')
  
  rmtree(LOCALPATH)                                              # Remove Diretorio temporario

  print("[INFO] - Cloud Function concluida")
  return "[INFO] - Cloud Function concluida"