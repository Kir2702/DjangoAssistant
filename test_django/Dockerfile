# syntax=docker/dockerfile:1

FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /DjangoAssistant


RUN pip install Django
RUN pip install Jinja2
RUN pip install requests

COPY . /DjangoAssistant

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]