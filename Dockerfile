FROM python:3.12.6

RUN mkdir /testing_docker
WORKDIR /testing_docker

COPY ./PMI_Model ./PMI_Model

RUN pip install requests

CMD ["python", "PMI_Model/test_docker.py"]

#  docker build -t testing_docker .
#  docker run --name testing_container testing_docker