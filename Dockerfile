FROM python:3.9.1-alpine3.13

ADD aqua-api-tool.py /
RUN pip install requests

ENTRYPOINT ["python", "-u", "/aqua-api-tool.py"]