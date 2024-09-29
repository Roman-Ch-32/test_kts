cd app && alembic upgrade head
cd ..
pytest
pytest --cov=app
pytest --cov=app > cov.txt
cd app
uvicorn main:app --host 0.0.0.0 --port 8000
