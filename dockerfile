FROM python:3.12.10

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
