FROM redhat/ubi8 AS pythonbase
WORKDIR /app
RUN dnf install -y python3.12 
RUN dnf install -y python3.12-pip
COPY requirements.txt .
RUN python3.12 -m pip install -r requirements.txt
COPY worker.py .
COPY config.ini .

CMD ["python3.12","worker.py"]