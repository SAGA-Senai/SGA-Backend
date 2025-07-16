from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "uma_chave_super_secreta" #TODO criar uma chave mais forte
ALGORITHM = "HS256"
TOKEN_TTL = 60 # dura 60 minutos (1 hora)

# cria o token com tempo personalizado caso desejado
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_TTL)) # define o tempo que o token vai expirar
    to_encode.update({"exp": expire}) # atualiza o tempo de expiração do token

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload
    except JWTError:
        return None