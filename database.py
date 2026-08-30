from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Float,
    ForeignKey,
    Text
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker
)
from flask_login import UserMixin
from datetime import datetime


PGUSER = "postgres"
PGPASSWORD = "Mare1987"
DB_NAME = "sakura_house"


engine = create_engine(
    f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@localhost:5432/{DB_NAME}"
)

Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass



class Users(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True
    )

    password: Mapped[str] = mapped_column(
        String(255)
    )




class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100)
    )

    description: Mapped[str] = mapped_column(
        Text
    )

    price: Mapped[float] = mapped_column(
        Float
    )

    image: Mapped[str] = mapped_column(
        String(255)
    )



class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="В корзине"
    )

    product: Mapped["Products"] = relationship()


Base.metadata.create_all(engine)