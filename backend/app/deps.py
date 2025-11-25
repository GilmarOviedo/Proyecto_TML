from fastapi import Depends

from .database import get_db


DBSessionDep = Depends(get_db)
