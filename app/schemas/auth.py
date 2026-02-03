from pydantic import BaseModel

class LoginSyncRequest(BaseModel):
    user_id: str
    username: str
    is_admin: bool
