FROM python:3.9-alpine

WORKDIR /opt/app

COPY ./bot.py ./
COPY ./requirements.txt ./

ENV TOKEN=6471999417:AAHCEYXi81vqPi_zLoH7ndURBvOQNY4U5sQ

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]