FROM python:3.6

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY . /app
RUN chmod +x /app/feeder.py
CMD /app/feeder.py

