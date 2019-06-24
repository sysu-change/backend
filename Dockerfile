## Dockerfile that generates an instance of www.earn_money.com
FROM ubuntu:16.04
LABEL maintainer="earn_money"
ENV LANG C

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev locales\
  && pip3 install --upgrade pip

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN pip3 install flask-cors --upgrade
ENTRYPOINT ["python3"]
CMD ["app.py"]