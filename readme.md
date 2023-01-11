# Cloud function
Esta cloud function tem como objetivo zipar multiplos arquivos csvs em um arquivo zip

Input: 


## Testes
1. Arquivos: (students_1.csv , students_2.csv) 12 Mb => 24MB cada 
   - Resultado: 
     - Cloud Function 128MB -> Ok

2. Arquivo: tabela_dummy.csv 51 MB
  - Resultado: 
    - Cloud Function 128MB -> Nok
    - Cloud Function 256MB -> Nok
    - Cloud Function 512MB -> Ok

3. Arquivos: (tabela_dummy.csv ) 51 MB * 2 => 102 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 512MB -> Ok

4. Arquivos: (tabela_dummy.csv) 51 MB * 4 => 306 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 512MB -> Nok

4. Arquivos: (tabela_dummy.csv) 51 MB * 5 => 306 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 512MB -> Nok

5. Arquivos: (tabela_dummy.csv) 51 MB * 6 => 306 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 512MB -> Nok

6. Arquivos: (tabela_dummy.csv) 51 MB * 7 => 357 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 512MB -> Nok

7. Arquivos: (tabela_dummy.csv) 51 MB * 7 => 357 MB
    - Cloud Function 128MB -> Nok
    - Cloud Function 512MB -> Nok