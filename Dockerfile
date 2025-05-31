FROM flyio/litefs:latest AS litefs

FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

COPY --from=litefs /usr/local/bin/litefs /usr/local/bin/litefs
COPY litefs.yml /etc/litefs.yml

ENTRYPOINT ["litefs", "mount"]
CMD ["--", "python", "app.py"]
EXPOSE 8080
