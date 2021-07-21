FROM python:3.9-slim-buster

COPY manifests /home/smoke-test/manifests/
COPY .kube /home/smoke-test/.kube/
COPY requirements.txt /home/smoke-test/requirements.txt
COPY smoke_test.py /home/smoke-test/smoke_test.py

WORKDIR /home/smoke-test/

ENV KUBECONFIG=.kube/config


RUN pip3 install -r requirements.txt

CMD [ "pytest", "-v", "-s"]