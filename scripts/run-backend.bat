@echo off
set PYTHONPATH=.
set DEMO_MODE=true
set USE_MOCK_RETRIEVAL=true
py -3.11 -m uvicorn backend.main:app --reload --port 8000
