FROM public.ecr.aws/lambda/python:3.12

# Copiar el código de la función
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Instalar las dependencias de la función
COPY requirements.txt .
RUN pip install -r requirements.txt

# Establecer el CMD para tu handler
CMD [ "lambda_function.lambda_handler" ]
