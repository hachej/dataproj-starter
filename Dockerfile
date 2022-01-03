FROM selenium/standalone-chrome
USER root
RUN apt-get update && apt-get install -y python3 python3-pip 

RUN python3 -m pip install selenium

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY . /opt/app/

ENV PYTHONPATH=/opt/app/
CMD [ "python3", "src/loader.py"]