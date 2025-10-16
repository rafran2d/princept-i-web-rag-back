from App.Schema.UserShcema import UserOutput
from pydantic import BaseModel

class Sign_upoutput(BaseModel) :
    status_code : int
    data : UserOutput
    message : str

