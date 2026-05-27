#!/usr/bin/env bash
export PYTHONPATH=.
export DEMO_MODE=true
export USE_MOCK_RETRIEVAL=true
python3.11 -m uvicorn backend.main:app --reload --port 8000
