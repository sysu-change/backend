## Dockerfile that generates an instance of www.earn_money.com
FROM python:3.7-alpine
LABEL maintainer="earn_money"
ENV LANG C.UTF-8d

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN pip3 install flask-cors --upgrade
ENTRYPOINT ["python3"]
CMD ["app.py"]
