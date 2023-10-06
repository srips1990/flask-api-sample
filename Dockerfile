FROM python:3.11.5-bullseye
WORKDIR /python-docker
COPY . .
RUN pip3 install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

