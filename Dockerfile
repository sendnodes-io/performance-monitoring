FROM python:3.11.0
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "./main.py"]
