from pydantic import BaseModel


class JarOut(BaseModel):
    id: int
    name: str
    sha256: str
    size_bytes: int

    class Config:
        from_attributes = True
