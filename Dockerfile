ROM python:3.11.4

WORKDIR .

COPY requiremets.txt .

RUN pip install -r requiremets.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]