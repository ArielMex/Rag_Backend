import os
from dotenv import load_dotenv

# Esto obliga a Python a leer tu archivo .env oculto
load_dotenv()

# Aquí capturamos la URL que escribiste y la exportamos
DATABASE_URL = os.getenv("DATABASE_URL")