FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
# ENV DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
# ENV DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}

CMD python manage.py makemigrations --check || python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py createsuperuser --noinput || true && \
    daphne -b 0.0.0.0 -p 8000 django_app.asgi:application
    

# ENTRYPOINT [ "/entrypoint.sh" ]