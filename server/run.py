"""
    Script que utiliza uvicorn para hostear o servidor.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="192.168.1.4", port=8000, reload=True)
