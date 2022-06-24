FROM python:3.8-buster

WORKDIR /root
COPY . /root/
RUN sh setup.sh

CMD ["python3", "-u", "main.py"]
