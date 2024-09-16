ARG PYVER=3.11 DEBVER=slim-bullseye


FROM python:$PYVER-$DEBVER
WORKDIR /app

ARG USER=app
ARG GROUP=$USER
RUN addgroup --system "$GROUP" && adduser --system --ingroup "$GROUP" "$USER"

COPY --chown=$USER:$GROUP requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

USER $USER:$GROUP
COPY --chown=$USER:$GROUP . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
