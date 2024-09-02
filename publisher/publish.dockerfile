FROM redhat/ubi8 AS pythonbase
WORKDIR /app
RUN dnf install -y python3.12 
RUN dnf install -y python3.12-pip
COPY requirements.txt .
RUN python3.12 -m pip install -r requirements.txt
COPY publish.py .
COPY config.ini .

CMD ["python3.12","publish.py"]