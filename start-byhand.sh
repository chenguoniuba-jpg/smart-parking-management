# Start By Hand

## 1. Download the repository

## 2. enter ai-parking directory
cd ai-parking/

## 3. install python (from offical website)

## 4. install uv package
pip install uv

## 5. install dependencies
uv sync

## 6. Initialize the demo database
# Option A: let the script generate a one-time password
uv run python -m backend.init_data
# Option B: choose a password before initialization
# ADMIN_PASSWORD='choose-a-strong-password' uv run python -m backend.init_data

## 7. Run the app
uv run python3 -m backend.main

## 8. Open http://127.0.0.1:8000
