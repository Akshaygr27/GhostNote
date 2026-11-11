from beanie import Document


class User(Document):

    name: str
    email: str

    class Settings:
        name = "users"