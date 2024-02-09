FROM python:3.12.1
COPY . /app
WORKDIR /app 
RUN pip install -r requirements.txt
EXPOSE $PORT
CMD gunicorn --workers=4 --timeout 200 --bind 0.0.0.0:$PORT app:app 