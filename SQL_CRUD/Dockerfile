FROM python:3.12

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY main.py /code/main.py
COPY config.py /code/config.py
COPY models.py /code/models.py
COPY schemas.py /code/schemas.py
COPY utils.py /code/utils.py
COPY test.db /code/test.dbpip

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
