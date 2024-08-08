import boto3
import json
import logging
import os
import requests
from datetime import datetime

# Configuración del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Obtener el nombre del bucket y la URL desde variables de entorno
    bucket_name = os.environ.get('BUCKET_NAME', 'nombre-unico-del-bucket')
    url_to_fetch = os.environ.get('URL_TO_FETCH', 'https://api.example.com/data')
    
    # Crear un cliente de S3
    s3 = boto3.client('s3')
    
    try:
        # Realizar solicitud GET a la URL
        response = requests.get(url_to_fetch)
        response.raise_for_status()
        data = response.json()
        
        # Crear nombre de archivo único para el log
        log_file_name = f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{context.aws_request_id}.json'
        
        # Crear contenido del log
        log_content = {
            'timestamp': datetime.now().isoformat(),
            'url': url_to_fetch,
            'status_code': response.status_code,
            'data': data
        }
        
        # Convertir contenido del log a JSON
        log_content_json = json.dumps(log_content, indent=4)
        
        # Subir el log al bucket S3
        s3.put_object(
            Bucket=bucket_name,
            Key=log_file_name,
            Body=log_content_json,
            ContentType='application/json'
        )
        logger.info(f'✅ Log almacenado en {bucket_name}/{log_file_name}')
        return {
            'statusCode': 200,
            'body': json.dumps('Log almacenado exitosamente.')
        }
    except requests.exceptions.RequestException as e:
        logger.error(f'⚠️ Error al realizar la solicitud: {e}')
        return {
            'statusCode': 500,
            'body': json.dumps('Error al realizar la solicitud.')
        }
    except Exception as e:
        logger.error(f'⚠️ Error al almacenar el log: {e}')
        return {
            'statusCode': 500,
            'body': json.dumps('Error al almacenar el log.')
        }
