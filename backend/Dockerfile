FROM python:3.7-slim
WORKDIR /app
COPY ./backend /app
RUN pip3 install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
