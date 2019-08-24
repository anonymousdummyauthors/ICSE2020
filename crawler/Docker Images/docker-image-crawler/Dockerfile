FROM python:3.7.3-stretch
RUN apt-get update && apt-get install -y chromedriver
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY docker_image_crawler.py /
CMD ["python3","-u","docker_image_crawler.py"]
#CMD tail -f /dev/null