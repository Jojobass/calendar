FROM python:3-slim
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py ./
CMD python main.py 0.0.0.0:5000
EXPOSE 5000