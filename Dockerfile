FROM python:3.10

WORKDIR /app

RUN apt update
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential

COPY requirements.txt .
COPY app.py .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
