FROM tiangolo/uwsgi-nginx-flask:python3.7

ENV STATIC_PATH /app/static
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
COPY ./app /app

