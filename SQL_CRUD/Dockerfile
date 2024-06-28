FROM python:3.11

COPY . /code

WORKDIR /code
#COPY requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

#COPY main.py /code/main.py
#COPY config.py /code/config.py
#COPY models.py /code/models.py
#COPY schemas.py /code/schemas.py
#COPY utils.py /code/utils.py
#COPY test.db /code/test.dbpip
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
