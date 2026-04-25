# Backend Virtual Environment Setup Guide

This guide provides step-by-step instructions for setting up the Python virtual environment for the AI Paper Marking backend.

## Why Virtual Environments?

A virtual environment is an isolated Python workspace that prevents dependency conflicts between projects. It ensures:
- Clean dependency management
- Project isolation
- Reproducible setups across different machines

## Prerequisites

- Python 3.10+ installed and available in your PATH
- Terminal access (Command Prompt, PowerShell, or Bash)

## Setup Instructions

### Step 1: Navigate to Backend Directory

From the project root:
```bash
cd backend
```

### Step 2: Create Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv venv
```

**Windows (Command Prompt or PowerShell):**
```bash
python -m venv venv
```

This creates a `venv/` directory containing the isolated Python environment.

### Step 3: Activate Virtual Environment

**macOS / Linux (Bash/Zsh):**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

> **Note:** If you encounter an execution policy error on Windows PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

**Success Indicator:** Your terminal prompt will change to show the venv name:
```
(venv) $ 
(venv) PS>
```

### Step 4: Upgrade pip (Optional but Recommended)

**macOS / Linux:**
```bash
python -m pip install --upgrade pip
```

**Windows:**
```bash
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies

With the virtual environment activated:
```bash
pip install -r requirements.txt
```

This installs all backend dependencies listed in `requirements.txt`:
- `fastapi` — web framework
- `uvicorn` — ASGI server
- `sqlalchemy` — database ORM
- `asyncpg` — async PostgreSQL driver
- `openai` — OpenAI API client
- `opencv-python-headless` — image processing
- And more (see `requirements.txt` for complete list)

### Step 6: Verify Installation

```bash
pip list
```

You should see all installed packages including `fastapi`, `uvicorn`, `sqlalchemy`, etc.

## Running the Backend

With the venv activated:
```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## Deactivating the Virtual Environment

When finished working on the backend:
```bash
deactivate
```

The terminal prompt will return to normal.

## Troubleshooting

### "python: command not found" or "No module named venv"

- **macOS/Linux:** Use `python3` instead of `python`
- **Windows:** Ensure Python is installed and in your PATH. Restart terminal and try again.

### "venv\Scripts\activate" not found

- Ensure you're in the `backend/` directory
- Verify `venv/` folder exists (check with `ls` or `dir`)
- Try using forward slashes: `venv/Scripts/activate`

### "The venv is not activated"

- Check if `(venv)` appears in your terminal prompt
- Try running `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows) again
- Make sure you haven't closed the terminal without deactivating first

### "pip: command not found" after activating venv

- The venv may not have activated correctly
- Try deactivating (`deactivate`) and activating again
- Verify `venv/bin/pip` (Linux/macOS) or `venv\Scripts\pip` (Windows) exists

### "ModuleNotFoundError" when running backend

- Ensure the venv is activated (check prompt for `(venv)`)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check `requirements.txt` hasn't been modified

## Quick Reference

| Task | macOS/Linux | Windows (CMD) | Windows (PS) |
|---|---|---|---|
| Create | `python3 -m venv venv` | `python -m venv venv` | `python -m venv venv` |
| Activate | `source venv/bin/activate` | `venv\Scripts\activate` | `venv\Scripts\Activate.ps1` |
| Install | `pip install -r requirements.txt` | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Deactivate | `deactivate` | `deactivate` | `deactivate` |

## Additional Resources

- [Python venv documentation](https://docs.python.org/3/library/venv.html)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- See `../user_manual.md` for full system setup and running instructions
