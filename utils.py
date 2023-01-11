from re import match
from zipfile import ZipFile, ZIP_DEFLATED
import io 
from os import system, listdir, unlink
import subprocess
from google.cloud import storage
from pathlib import Path

class Blob:
  def __init__(self, bucket_name: str):
    self.storage_client = storage.Client()
    self.bucket = self.storage_client.bucket(bucket_name)
  
  def lista_blobs(self, prefix: str) -> list :
    """ Lista arquivos no bucket com o prefixo passado
        Parameter: prefix (str) : Uma string com o caminho para o(s) arquivo(s) a serem listados
        Returns: blob.name (list): Lista dos arquivos no bucket
    """
    files = []
    blobs = self.bucket.list_blobs()

    for blob in blobs:
      if match(f"{prefix}.*",blob.name):
        files.append(blob.name)
    
    print("[INFO] - Listado arquivos bucket")
    return files
  
  def download_blob(self, filepath: str, csv_file: str):
    """ Baixa arquivos csv do bucket
        Parameters: csv_file (str) - Arquivos csv
        Return: (void)
    """
    # for idx, csv_file in enumerate(csv_files):
    blob = self.bucket.blob(csv_file)
    blob_name = csv_file.split('/')[-1]
    
    # blob.download_to_filename(f"{Path(filepath,blob_name)}")
    return blob.download_as_string()
    print(f"[INFO] - Download arquivo {blob_name}")
    # print(f"[INFO] - Download(s) Concludo(s)")

  def upload_blob(self, filename: str, filepath: str, zip_buffer: io.BytesIO):
    """ Efetua upload do arquivo zip
        Parameters: 
          filename   (str)     - Nome do arquivo zip
          filepath   (str)     - Caminho destino arquivo zip
          zip_buffer (BytesIO) - Arquivos zipados em memoria
        Return: (void)
    """
    print(f"[INFO] - Iniciando upload arquivo(s)")
    blob = self.bucket.blob(f"{filepath}{filename}.zip")
    # blob.upload_from_file(zip_buffer, content_type="application/zip")
    blob.upload_from_file(zip_buffer, content_type=="application/zip")
    print(f"[INFO] - Efetuado upload arquivo {filename}")
  
def merge_files(filepath: str, blob: str):
  """ Efetua o merge dos arquivos csv em um 
      Parameters:
        filepath (str) - Caminho origem csv
        blob     (str) - Nome arquivo csv
      Return: (void)
  """
  filename = blob.split('/')[-1]

  with open( f"{filepath}/output.csv", "w") as output_file:
      with open(f"{filepath}/{filename}") as f:
        output_file.write(f.read())
        print(f"[INFO] - Efetuado merge arquivo {filename}")
      system(f"rm {filepath}/{filename}")

  print(f"[INFO] - Concluido merge arquivos")

def zip_file(csv_path: str, filename: str, blob_buffer: str) -> io.BytesIO:
  """ Zipa arquivo passado como parametro
      Parameters: 
        blob_output (Blob) - Objeto bucket destino
        input_path (str)   - Caminho origem arquivos
      Return: (void)
  """
  print(f"[INFO] - Iniciando Zip arquivo(s)")
  zip_buffer = io.BytesIO()

  with ZipFile(zip_buffer,"w", compression=ZIP_DEFLATED) as zipF:
    with open(f"{csv_path}/output.csv") as f:
      zipF.writestr(f"{filename}.csv",data=f.read())
  zip_buffer.seek(0)

  print(f"[INFO] - Gerado arquivo zip em memoria")
  return zip_buffer