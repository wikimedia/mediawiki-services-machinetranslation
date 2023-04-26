# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget unzip

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /app/
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 8989
