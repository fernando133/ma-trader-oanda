# trading-service

Microserviso que é parte da implementação do Trabalho de Conclusao de Curso com o tema: Criação de um Agente Autônomo para Operações no Mecado de Câmbio Internacional.

## Pacotes necessários

```
pip install -U -r requirements.txt 
```

## script_conf.json

Para que o microservico se conecte com a API de Negocições da OANDA, deve-se criar o arquivo ```script_conf.json``` no diretório ```/conf``` com a ```API Key``` e o id ```ACCOUNT_ID``` de uma conta válida na plataforma OANDA.


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
