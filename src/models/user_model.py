from sqlalchemy import Column, Integer, String
from db.connection import Base
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    def set_pass(self, password):
        self.password_hash = generate_password_hash(password)

    def check_pass(self, password):
        return check_password_hash(self.password_hash, password)

