<<<<<<< HEAD
ROM python:3.11.4

WORKDIR .

COPY requiremets.txt .

RUN pip install -r requiremets.txt
=======
FROM python:3.11.4

WORKDIR .

COPY requirements.txt .

RUN pip install -r requirements.txt
>>>>>>> 363feb8d0a4d3b2b2fc2e61e50be1aa5f9e024b3

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]