# Cloud function
Esta cloud function tem como objetivo zipar multiplos arquivos csvs em um arquivo zip

## Indice
[Deploy Function](#deploy)
[Build Image](#build-docker)
[Http Call](#http-call)
[Utilidade](#util)

Input: 
pytest - Covarage

## Deploy
gcloud functions deploy fnc_zip_file_128mb \
--region=us-central1 \
--memory=128 \
--runtime=python310 \
--timeout=540 \
--source=. \
--entry-point=main \
--trigger-http

## Util
<!-- ===============================
----------UTIL COMMANDS
=============================== -->
functions-framework --target main --debug
https://poc-bv-zip-file-7uo5gkxb3a-uc.a.run.app

## Cloud Function Call
{
  "gcs_input": "gs://banco-bv-sandbox/test/input/sample",
  "gcs_output": "gs://banco-bv-sandbox/test/output",
  "filename" : "arquivo20gb",
  "workers" : 8
}

## Curl Call
*Non Authenticated*
curl --data '{  "gcs_input": "gs://banco-bv-sandbox/test/input/sample",  "gcs_output": "gs://banco-bv-sandbox/test/output",  "filename" : "sample",  "queue_size" : 30}'  \
  --header "Content-Type: application/json" \
  --header "Accept: application/json" \
   https://poc-zip-file-stream-7uo5gkxb3a-uc.a.run.app
   localhost:8080
   https://poc-zip-file-stream-7uo5gkxb3a-uc.a.run.app
  https://poc-zip-file-stream-ai-7uo5gkxb3a-uc.a.run.app

*Authenticated* - fnc_zip_file_stream
curl -m 550 -X POST https://us-central1-banco-bv-sandbox.cloudfunctions.net/fnc_zip_file_128mb \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
    "gcs_input": "gs://banco-bv-sandbox/test/input/40gb/",  
    "gcs_output": "gs://banco-bv-sandbox/test/output",  
    "filename" : "arquivo40gb",  "queue_size" : 30
}
'
curl --data '{"gcs_input": "gs://banco-bv-sandbox/test/input/sample","gcs_output": "gs://banco-bv-sandbox/test/output", "filename":"sample"}'  \
  --header "Content-Type: application/json" \
  --header "Accept: application/json" localhost:8080

### Build Docker
[Indice](#indice)
Este comando é responsável por gerar uma imagem docker para cloud function
```shell
gcloud builds submit --pack image=us-central1-docker.pkg.dev/banco-bv-sandbox/bv-repo/poc-zip-file-stream,env=GOOGLE_FUNCTION_TARGET=main
gcloud builds submit --pack image=us-central1-docker.pkg.dev/banco-bv-sandbox/bv-repo/poc-zip-file-stream-ai,env=GOOGLE_FUNCTION_TARGET=main
```

## Testes
Testes abaixo foram feitos executando o seguinte processo. Baixar os arquivos acumulá-los e subir para núvem

1. Arquivos: (students_1.csv , students_2.csv) 12 Mb => 24MB cada 
   - Resultado: 
     - Cloud Function 128MB -> Ok

2. Arquivo: students.csv 51 MB
  - Resultado: 
    - Cloud Function 128MB -> Nok
    - Cloud Function 256MB -> Ok
    - Cloud Function 512MB -> Ok

3. Arquivos: (students_1.csv, students_2.csv ) 51 MB * 2 => 102 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 256MB -> Ok
    - Cloud Function 512MB -> Ok

...
7. Arquivos: (tabela_dummy.csv) 51 MB * 7 => 357 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 512MB -> Nok

### Stream Test
Estes testes foram feitos baixando o arquivo em partes e em seguida subindo essa parte para um único destino

8. Arquivo arquivo6gb => 6gb
  - Cloud Function 1gb -> Ok

### Testes
[Indice](#indice)
Arquivos utilizados para efetuar o stream 