"""
This file contains database models/schemas which useful for create tables.
"""
from db_helper import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, backref
#change add UniqueContraint ganesh
from sqlalchemy import JSON, Column, Integer, String, DateTime, ForeignKey, Table, Text, Float, Boolean, Numeric, UniqueConstraint
from backend.helpers.log_config import get_logger
from sqlalchemy.sql import func
from datetime import datetime


logger = get_logger(name=__name__)


class CommonThings:
    _abstract_ = True
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # created_at = Column(DateTime, server_default=func.now(), nullable=False)  # Use DB default
    # updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # DB updates automatically
    
    def save(self, session):
        try:
            session.add(self)
            session.commit()
            return self
        except Exception as e:
            logger.error(e)
            session.rollback()
            return None

# Follow table to establish many-to-many relationships between users
followers_table = Table(
    'followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('user.id')),  # Corrected table name
    Column('followed_id', Integer, ForeignKey('user.id'))   # Corrected table name
)

class Follow(Base):
    __tablename__ = 'follows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey('user.id'))  # Fixed table name
    followed_id = Column(Integer, ForeignKey('user.id'))  # Fixed table name
    status = Column(String, default="pending")  # "pending", "accepted", "rejected"

    follower = relationship("User", foreign_keys=[follower_id], backref="sent_requests")
    followed = relationship("User", foreign_keys=[followed_id], backref="received_requests")


class User(Base, CommonThings):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(80), nullable=False, unique=True)
    email_verified_at = Column(DateTime, nullable=True)  # New column to track email verification
    username = Column(String(80), nullable=False, unique=True)
    fullname = Column(String(80), nullable=True)
    avatar_url = Column(String(255), nullable=True)  # Default avatar URL
    avatar_thumbnail_url = Column(String(255), nullable=True)  # Default avatar URL
    bio = Column(Text, nullable=True)
    password = Column(Text, nullable=False)
    preferred_language_code = Column(String(2), default='en', nullable=True)  # Assuming ISO 639-1 language codes
    current_plan_name = Column(Text, nullable=False)
    plan_activated_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    tg_chat_id = Column(String(80), unique=True, nullable=True)
    tg_username = Column(String(80), unique=True, nullable=True)
    credits_available = Column(Numeric, default=20)

    # bank_account_name = Column(String(255), nullable=True)
    # bank_account_number = Column(String(255), nullable=True, unique=True)
    # bank_account_ifsc = Column(String(255), nullable=True)
    # upi_id = Column(String(255), nullable=True, unique=True)
    # phone_number_for_bank = Column(String(255), nullable=True)
    is_contributor = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    last_active_on = Column(DateTime, default=datetime.now(timezone.utc))
    payments = relationship("Payment", backref="user")
    bank_details = relationship('BankDetails', back_populates='user')
    coupons = relationship("Coupon", backref="user")
    referrer_commissions = relationship("Commission", foreign_keys="[Commission.referrer_id]", backref="referrer_user")
    referred_commissions = relationship("Commission", foreign_keys="[Commission.referred_id]", backref="referred_user")
    lessons = relationship('UserLessonProgress', back_populates='user')
    sections = relationship('UserSectionProgress', back_populates='user')
    students = relationship('Student', back_populates='user')
    teachers = relationship('Teacher', back_populates='user')

    # commissions = relationship("Commission", back_populates="user", lazy='dynamic')
    # usages = relationship("Usage", back_populates="user", lazy='dynamic')
    # histories = relationship("History", back_populates="user", lazy='dynamic')
    posts = relationship('Post', back_populates='user', lazy='dynamic')
    post_likes = relationship('PostLike', back_populates='user', lazy='dynamic')
    post_flags = relationship('PostFlag', back_populates='user', lazy='dynamic')
    api_usages = relationship("ApiUsage", back_populates="user", lazy='dynamic')
    rzp_ai_toolbox_payments = relationship("RzpAIToolboxPayment", back_populates="user", lazy='dynamic')
    credit_transactions = relationship("CreditTransaction", back_populates="user", lazy='dynamic')
    # credit_transactions = relationship("CreditTransaction", back_populates="user")
    # rzp_payment_links = relationship("RzpPaymentLinks", back_populates="user")

    # Define the 'followed' relationship
    followed = relationship(
        'User', secondary=followers_table,
        primaryjoin=(followers_table.c.follower_id == id),  # This user's followers
        secondaryjoin=(followers_table.c.followed_id == id),  # This user's followings
        backref=backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def _repr_(self):
        return f"<id - {self.id}, email - {self.email}, current_plan_name - {self.current_plan_name}, preferred_language_code - {self.preferred_language_code}, plan_activated_at - {self.plan_activated_at}>"


