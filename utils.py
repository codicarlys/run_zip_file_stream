from re import match
from zipfile import ZipFile, ZIP_DEFLATED
import io 
from google.cloud import storage

class Blob:
  def __init__(self, bucket_name: str, blob_path: str =None):
    try:
      self.storage_client = storage.Client()
      self.bucket = self.storage_client.bucket(bucket_name)
      self.blob = self.bucket.blob(blob_path) if blob_path else None

    except e:
      print(f'[ERRO] - Erro ao conectar ao bucket: {e}')
  
  def get_size(self, blob_path: str):
    """ Retorna o tamanho do arquivo blob
        Parametro: blob_path (str) - Caminho relativo do blob
    """
    blob = self.bucket.get_blob(blob_path)
    print("[INFO] - Arquivo possui {:.2f} MB".format(round(blob.size/1024**2,2)))
    return blob.size

  def lista_blobs(self, prefix: str) -> list :
    """ Lista arquivos no bucket com o prefixo passado
        Parameter: prefix (str) : Uma string com o caminho para o(s) arquivo(s) a serem listados
        Returns: blob.name (list): Lista dos arquivos no bucket
    """
    files = []
    blobs = self.bucket.list_blobs()

    for blob_file in blobs:
      if prefix in blob_file.name:
        files.append(blob_file.name)
    
    print("[INFO] - Listado arquivos bucket")
    return files

  def upload_bytes_to_bucket(self, file_buffer: io.BytesIO, content_type: str):
    """ Efetua upload do buffer
        Parameters: 
          file_buffer  (BytesIO) - Arquivo em memoria
          content-type     (str) - Metadado do Conteudo Ex: "application/zip" ou "application/octet-stream
        Return: (void)
    """
    self.blob.upload_from_file(file_buffer, content_type=content_type)
    print(f"[INFO] - Efetuado upload por partes do arquivo ")
  
  def download_by_parts(self, input: dict) :
    """Retorna blob em bytes
       Parametro: input (dict) - Dicionario com os parametros de inicio e fim em bytes para download do blob em partes
    """
    blob = self.bucket.blob(input['blob'])
    in_memory_file = io.BytesIO()
    
    print("[INFO] - Download parte efetuado")
    return blob.download_as_string(start=input['start'], end=input['end'])
  
  @staticmethod
  def split_byte_size(size: int, blob_path: str, split_number: int) -> list:
    """ Retorna lista de bytes para leitura do blob
       Parametros:
         size         (str) - Tamanho em bytes do blob
         blob_path    (str) - Caminho relativo blob
         split_number (int) - Quantidade de vezes que o blob sera divido
    """
    byte_list = []

    if split_number == 1:
      byte_list.append({"start":0, "end": size, "blob": blob_path})
      return byte_list

    split = int(size/split_number)
    for i in range(split_number):
      if i == 0:
        byte_list.append({"start":0, "end": split, "blob": blob_path})
      elif i == (split_number-1):
        byte_list.append({"start":(split+1)*i, "end": size, "blob": blob_path})
      else:
        byte_list.append({"start":(split+1)*i, "end": ((split+1)*i)+split, "blob": blob_path})
    
    print(f"[INFO] - Split efetuado em {split_number} partes")
    return byte_list