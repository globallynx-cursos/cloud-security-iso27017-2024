import boto3
import json
import uuid
from botocore.exceptions import ClientError

class KMSS3Manager:
    def __init__(self, region_name='us-east-1'):
        self.kms_client = boto3.client('kms', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.key_id = None
        self.bucket_name = None

    def create_kms_key(self, description="🔐 Clave para cifrado S3 alineado con ISO 27017"):
        try:
            response = self.kms_client.create_key(
                Description=description,
                KeyUsage='ENCRYPT_DECRYPT',
                Origin='AWS_KMS'
            )
            self.key_id = response['KeyMetadata']['KeyId']
            print(f"🔑 Nueva clave KMS creada. ID: {self.key_id}")
            return self.key_id
        except ClientError as e:
            print(f"❌ Error al crear la clave KMS: {e}")
            return None

    def create_s3_bucket(self, bucket_name_prefix):
        bucket_name = f"{bucket_name_prefix}-{uuid.uuid4()}"
        try:
            self.s3_client.create_bucket(Bucket=bucket_name)
            self.bucket_name = bucket_name
            print(f"🪣 Bucket S3 creado: {bucket_name}")
            return True
        except ClientError as e:
            print(f"❌ Error al crear el bucket S3: {e}")
            return False

    def configure_s3_encryption(self):
        if not self.key_id or not self.bucket_name:
            print("⚠️ Error: Se requiere una clave KMS y un bucket S3.")
            return False
        try:
            self.s3_client.put_bucket_encryption(
                Bucket=self.bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'aws:kms',
                            'KMSMasterKeyID': self.key_id
                        }
                    }]
                }
            )
            print(f"🔒 Cifrado configurado para el bucket {self.bucket_name}")
            return True
        except ClientError as e:
            print(f"❌ Error al configurar el cifrado del bucket: {e}")
            return False

    def upload_file(self, file_name, object_name=None):
        if object_name is None:
            object_name = file_name
        try:
            self.s3_client.upload_file(file_name, self.bucket_name, object_name)
            print(f"📤 Archivo {file_name} subido como {object_name}")
            return True
        except ClientError as e:
            print(f"❌ Error al subir el archivo: {e}")
            return False

    def download_file(self, object_name, file_name):
        try:
            self.s3_client.download_file(self.bucket_name, object_name, file_name)
            print(f"📥 Archivo {object_name} descargado como {file_name}")
            return True
        except ClientError as e:
            print(f"❌ Error al descargar el archivo: {e}")
            return False

    def verify_bucket_encryption(self):
        try:
            response = self.s3_client.get_bucket_encryption(Bucket=self.bucket_name)
            rules = response['ServerSideEncryptionConfiguration']['Rules']
            for rule in rules:
                if rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'aws:kms' and rule['ApplyServerSideEncryptionByDefault']['KMSMasterKeyID'] == self.key_id:
                    print("✅ El bucket está correctamente configurado para usar KMS.")
                    return True
            print("❌ El bucket no está configurado correctamente para usar KMS.")
            return False
        except ClientError as e:
            print(f"❌ Error al verificar el cifrado del bucket: {e}")
            return False

    def verify_object_encryption(self, object_name):
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)
            if 'ServerSideEncryption' in response and response['ServerSideEncryption'] == 'aws:kms':
                print(f"✅ El objeto {object_name} está cifrado con KMS.")
                return True
            print(f"❌ El objeto {object_name} no está cifrado con KMS.")
            return False
        except ClientError as e:
            print(f"❌ Error al verificar el cifrado del objeto: {e}")
            return False

# 🌟 Ejemplo de uso
manager = KMSS3Manager()

# Crear clave KMS
key_id = manager.create_kms_key()

# Crear bucket S3 con un prefijo y UUID único
bucket_prefix = "bucket-sfe-test"
manager.create_s3_bucket(bucket_prefix)

# Configurar cifrado del bucket
manager.configure_s3_encryption()

# Verificar la configuración de cifrado del bucket
manager.verify_bucket_encryption()

# Subir un archivo (asumiendo que existe un archivo 'documento_secreto.txt')
manager.upload_file('assets/documento_secreto.txt')

# Verificar el cifrado del objeto
manager.verify_object_encryption('assets/documento_secreto.txt')

# Descargar el archivo (asegúrate de usar el mismo nombre de objeto que el nombre usado al subir)
manager.download_file('assets/documento_secreto.txt', 'documento_descargado.txt')

print("🚀 Flujo completado.")
