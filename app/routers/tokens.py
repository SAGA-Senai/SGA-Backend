from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "uma_chave_super_secreta" #TODO criar uma chave mais forte
ALGORITHM = "HS256"
TOKEN_TTL = 60 # dura 60 minutos (1 hora)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_TTL))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload
    except JWTError:
        return None