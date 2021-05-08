from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from courseapp.utils import get_or_create
from courseapp.server import enums
from courseapp.server.utils import find_competence_assessment


Base = declarative_base()
engine = create_engine("sqlite:///data.db", echo=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    login = Column(String(20), nullable=False, unique=True)
    password = Column(String(40), nullable=False)
    permissions = Column(String(20), nullable=False)
    orders = relationship("Order", cascade="all, delete, delete-orphan")
    problems_created = relationship("Problem", cascade="all, delete, delete-orphan")
    votes = relationship("Vote", cascade="all, delete, delete-orphan")
    left_to_vote = relationship("LeftToVote", cascade="all, delete, delete-orphan")

    position = Column(String(30))
    academic_degree = Column(String(30))

    def get_relative_competence(self, competence_sum):
        return find_competence_assessment(self) / competence_sum

    def __str__(self):
        return self.login


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(32), nullable=True, unique=True)
    description = Column(String(10000), nullable=True)
    price = Column(Float)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship(
        "Company",
        back_populates="services",
    )
    orders = relationship("Order", cascade="all, delete, delete-orphan")

    def __str__(self):
        return self.name


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(32), nullable=False)
    services = relationship("Service", back_populates="company")

    def __str__(self):
        return self.name


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)

    quantity = Column(Integer, default=1)
    service_id = Column(Integer, ForeignKey("services.id"))
    service = relationship("Service", back_populates="orders")
    customer_id = Column(Integer, ForeignKey("users.id"))
    customer = relationship("User", back_populates="orders")

    def __repr__(self):
        return (
            f"<Sale(service={self.service}, "
            f"customer={self.customer}, "
            f"quantity={self.quantity})>"
        )


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    voter_id = Column(Integer, ForeignKey("users.id"))
    voter = relationship("User", back_populates="votes")

    decision_id = Column(Integer, ForeignKey("decisions.id"))
    decision = relationship("Decision", back_populates="votes")
    decision_assessment = Column(Integer)
    decision_weigth = Column(Integer)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(50), nullable=False)
    votes = relationship("Vote", back_populates="decision")

    problem_id = Column(Integer, ForeignKey("problems.id"))
    problem = relationship("Problem", back_populates="decisions")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(50), nullable=False)
    status = Column(String(20), default=enums.Status.waiting.value)

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="problems_created")
    left_to_vote = relationship("LeftToVote", cascade="all, delete, delete-orphan")
    decisions = relationship("Decision", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return (
            f"<Problem(description={self.description}, "
            f"status={self.status}, "
            f"creator={self.creator.login})"
        )


class LeftToVote(Base):
    __tablename__ = "left_to_vote"
    id = Column(Integer, primary_key=True, autoincrement=True)

    voter_id = Column(Integer, ForeignKey("users.id"))
    voter = relationship("User", back_populates="left_to_vote")

    problem_id = Column(Integer, ForeignKey("problems.id"))
    problem = relationship("Problem", back_populates="left_to_vote")

    def __repr__(self):
        return f"<LeftToVote(voter={self.voter.login}, problem={self.problem})>"


Base.metadata.create_all(bind=engine)
Session_maker = sessionmaker(bind=engine)
session = Session_maker()
get_or_create(
    session_=session,
    model=User,
    login="admin",
    password="d033e22ae348aeb5660fc2140aec35850c4da997",
    permissions="admin",
)
