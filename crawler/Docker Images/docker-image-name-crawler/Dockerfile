FROM python:3.7.3-stretch
RUN apt-get update && apt-get install -y chromedriver
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY name_crawler.py /
CMD ["python3","-u","name_crawler.py"]
# CMD tail -f /dev/null