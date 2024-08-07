# Anexo: Acceso Programático a la Consola de AWS

## Introducción
Acceder a la consola de AWS programáticamente permite interactuar con los servicios de AWS usando líneas de comando o scripts automatizados. Esto es esencial para DevOps, automatización de tareas y gestión de recursos de manera eficiente. 

## Requisitos
1. **Cuenta de AWS:** Necesitas una cuenta activa en AWS.
2. **Credenciales de AWS:** Debes tener un usuario IAM con permisos adecuados y credenciales de acceso configuradas.

## Configuración de las Credenciales de AWS

1. **Crear un usuario IAM:**
    - Accede a la [Consola de Gestión de AWS](https://aws.amazon.com/es/console/).
    - Ve a `IAM > Usuarios` y crea un nuevo usuario con acceso programático.
    - Adjunta las políticas necesarias (por ejemplo, `AmazonEC2FullAccess`).

2. **Obtener las credenciales:**
    - Después de crear el usuario, descarga el archivo CSV que contiene el `Access Key ID` y `Secret Access Key`.

3. **Configurar las credenciales en tu máquina:**
    - **Windows:**
        ```sh
        aws configure
        ```
        Ingresa tu `Access Key ID`, `Secret Access Key`, región predeterminada (por ejemplo, `us-east-1`) y formato de salida (por ejemplo, `json`).

    - **macOS/Linux:**
        ```sh
        aws configure
        ```
        El proceso es el mismo, solo sigue las instrucciones en pantalla.

## Ejemplo de Uso con Boto3 en Python

Boto3 es la biblioteca de AWS para Python que facilita la interacción con los servicios de AWS.

1. **Instalar Boto3:**
    ```sh
    pip install boto3
    ```

2. **Código de ejemplo:**
    ```python
    import boto3

    # Inicializar un cliente EC2
    ec2 = boto3.client('ec2')

    # Listar todas las instancias EC2
    def list_ec2_instances():
        instances = ec2.describe_instances()
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                print(f"ID de la instancia: {instance['InstanceId']} - Estado: {instance['State']['Name']}")

    if __name__ == "__main__":
        list_ec2_instances()
    ```

    Este script listará todas las instancias EC2 en tu cuenta de AWS.

## Recursos Adicionales
- [Documentación de Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) 📚
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) 🖥️
- [Guía de IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) 🔐

## Consejos de Seguridad
1. **No compartas tus credenciales:** Mantén tus `Access Key ID` y `Secret Access Key` seguras y no las compartas.
2. **Utiliza IAM Roles:** Para aplicaciones que corren en AWS, utiliza roles de IAM en lugar de credenciales de acceso.
3. **Rotación de credenciales:** Cambia tus credenciales regularmente y elimina las que ya no usas.

## Resumen
Acceder programáticamente a la consola de AWS permite automatizar y gestionar eficientemente los recursos de AWS. Siguiendo estos pasos, puedes configurar tus credenciales y empezar a usar scripts para interactuar con los servicios de AWS.

¡Buena suerte en tu viaje de automatización con AWS! 🚀
