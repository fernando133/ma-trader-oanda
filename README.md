# trading-service

Microserviço parte da implementação do Trabalho de Conclusão de Curso, para obtenção do título de Bacharel em Engenharia da Computação do Centro Universitário UniEvangélica de Anápolis-GO, com o tema: Criação de um Agente Autônomo para Operações no Mecado de Câmbio Internacional.

Autor: Fernando Gualberto M. Pereira

## OANDA API

Para se utilizar a implementação/desenvolver é necessário criar um conta Pratice na corretora oanda, afim de se obter o ```account_id``` e a ```API Key```

Site da corretora: https://www.oanda.com/lang/pt/

API Docs: 
    - https://oanda-api-v20.readthedocs.io/en/latest/
    - http://developer.oanda.com/rest-live-v20/introduction/        


## Pacotes necessários
É recomendado que se utilizar o virtualenv para o desenvolvimento a fim de se isolar as dependêcias do projeto.

Este artigo descreve o uso do virtualenv de forma simples e objetiva:
https://pythonacademy.com.br/blog/python-e-virtualenv-como-programar-em-ambientes-virtuais

```
pip install -U -r requirements.txt 
```

## script_conf.json

Para que o microserviço se conecte com a API de Negocições da OANDA, deve-se criar o arquivo ```script_conf.json``` no diretório ```/conf``` com a ```API Key``` e o id ```ACCOUNT_ID``` de uma conta válida na plataforma OANDA.


```json
{
    "script-conf":{
        "oanda":{
            "api_key"       : "API_KEY", 
            "account_id"   : "ACCOUNT_ID",
            "environment"  : "practice"
         }
    }
}
```

Também é necessário criar o arquivo ```config.ini``` no diretório ```/config``` com o seguinte conteúdo: 


```json
[oanda]
account_id = ID_SUA_CONTA
api_key = CHAVE_DA_API_DE_SUA_CONTA
```
