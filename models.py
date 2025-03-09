"""
This file contains database models/schemas which useful for create tables.
"""
from db_helper import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, backref
#change add UniqueContraint ganesh
from sqlalchemy import JSON, Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, Numeric, UniqueConstraint
from backend.helpers.log_config import get_logger
from sqlalchemy.sql import func

logger = get_logger(name=__name__)


class CommonThings:
    __abstract__ = True
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

#ganesh
# Followers Table (Many-to-Many Relationship)
class Followers(Base, CommonThings):
    __tablename__ = "followers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # Ensure a user cannot follow another user multiple times
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_followers"),)

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

    # Many-to-Many Relationship for Followers ganesh
    followers = relationship(
        "User",
        secondary=Followers.__tablename__,
        primaryjoin=id == Followers.following_id,  # Fix: Correct join condition
        secondaryjoin=id == Followers.follower_id,
        lazy="dynamic",
        backref="following"  # Users this user follows
    )
    
    def __repr__(self):
        return f"<id - {self.id}, email - {self.email}, current_plan_name - {self.current_plan_name}, preferred_language_code - {self.preferred_language_code}, plan_activated_at - {self.plan_activated_at}>"


# class VerificationToken(Base, CommonThings):
#     __tablename__ = 'verification_token'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     token = Column(String(255), nullable=False, unique=True)
#     token_type = Column(String(50), nullable=False)  # 'email_verification' or 'password_reset'
#     expires_at = Column(DateTime, nullable=False)

#     user = relationship("User", backref=backref("verification_tokens", cascade="all, delete-orphan"))

#     def __repr__(self):
#         return f"<VerificationToken user_id={self.user_id}, token={self.token}, token_type={self.token_type}, expires_at={self.expires_at}>"


class BankDetails(Base, CommonThings):
    __tablename__ = 'bank_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    bank_account_name = Column(String(255), nullable=False)
    bank_account_number = Column(String(255), nullable=False)
    bank_account_ifsc = Column(String(255), nullable=False)
    upi_id = Column(String(255), nullable=True)
    phone_number = Column(String(255), nullable=False)
    user = relationship("User", back_populates="bank_details")

    def __repr__(self):
        return f"<BankDetails {self.id} for User {self.user_id}>"


class Supersection(Base, CommonThings):
    __tablename__ = 'supersection'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    overview = Column(Text, nullable=True)
    slug = Column(String(255), nullable=False, unique=True)
    order_number = Column(Integer, nullable=False, unique=False)
    sections = relationship("Section", back_populates="supersection")
    def __repr__(self):
        return f"<Supersection id={self.id}, name={self.name}, slug={self.slug}>"


class Section(Base, CommonThings):
    __tablename__ = 'section'
    id = Column(Integer, primary_key=True, autoincrement=True)
    supersection_id = Column(Integer, ForeignKey('supersection.id'), nullable=False)
    name = Column(String(255), nullable=False)
    overview = Column(Text, nullable=True)
    slug = Column(String(255), nullable=False, unique=True)
    thumbnail = Column(String(255), nullable=True)  # Path to thumbnail image
    order_number = Column(Integer, nullable=False, unique=True)  # Add this line
    accessible_plans = Column(Text, nullable=True)  # Comma-separated plan names for access
    visible_plans = Column(Text, nullable=True)  # Comma-separated plan names for menu visibility
    lessons = relationship("Lesson", back_populates="section")
    supersection = relationship("Supersection", back_populates="sections")
    users_progress = relationship('UserSectionProgress', back_populates='section')
    users = relationship('UserSectionProgress', back_populates='section')

    def __repr__(self):
        return f"<Section id={self.id}, name={self.name}, order_number={self.order_number}, slug={self.slug}, overview={self.overview}, thumbnail={self.thumbnail}>"


class Lesson(Base, CommonThings):
    __tablename__ = 'lesson'
    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)  # JSON content
    content_path  = Column(Text, nullable=True)  # Path to JSON content file
    order_number = Column(Integer, nullable=False, unique=False)
    allow_activity_upload = Column(Boolean, default=False)
    allow_feedback_upload = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)  # New column for hiding lessons
    section = relationship("Section", back_populates="lessons")
    users_progress = relationship('UserLessonProgress', back_populates='lesson')
    users = relationship('UserLessonProgress', back_populates='lesson')
    posts = relationship('Post', back_populates='lesson', lazy='dynamic')

    def __repr__(self):
        return f"<Lesson(title={self.title}, slug={self.slug})>"


class Tag(Base, CommonThings):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    slug = Column(String(255), nullable=False, unique=True)
    lessons = relationship('Lesson', secondary='lesson_tag_link', back_populates='tags')

class LessonTagLink(Base, CommonThings):
    __tablename__ = 'lesson_tag_link'
    lesson_id = Column(Integer, ForeignKey('lesson.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
    lesson = relationship(Lesson, backref=backref("lesson_tag_link"))
    tag = relationship(Tag, backref=backref("lesson_tag_link"))

Lesson.tags = relationship('Tag', secondary='lesson_tag_link', back_populates='lessons')
Tag.lessons = relationship('Lesson', secondary='lesson_tag_link', back_populates='tags')


class UserLessonProgress(Base, CommonThings):
    __tablename__ = 'user_lesson_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lesson.id'), nullable=False)
    is_completed = Column(Boolean, default=False)
    feedback = Column(Text)
    activity = Column(Text)  # Path to the activity file
    completed_at = Column(DateTime)
    user = relationship('User', back_populates='lessons')
    lesson = relationship('Lesson', back_populates='users')
    # media = relationship("Media", back_populates="user_lesson_progress", cascade="all, delete-orphan")  # New line

    def __repr__(self):
        return f"<UserLessonProgress(user_id={self.user_id}, lesson_id={self.lesson_id}, is_completed={self.is_completed}, completed_at={self.completed_at}, feedback={self.feedback}, activity={self.activity})>"

class UserSectionProgress(Base, CommonThings):
    __tablename__ = 'user_section_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    is_completed = Column(Boolean, default=False)
    feedback = Column(Text)
    activity = Column(Text)  # Path to the activity file
    completed_at = Column(DateTime)
    user = relationship('User', back_populates='sections')
    section = relationship('Section', back_populates='users')

    def __repr__(self):
        return f"<UserSectionProgress(user_id={self.user_id}, section_id={self.section_id}, is_completed={self.is_completed}, completed_at={self.completed_at}, feedback={self.feedback}, activity={self.activity})>"

class Payment(Base, CommonThings):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    razorpay_payment_id = Column(String(255), nullable=True)
    order_id = Column(String(255), nullable=True)
    invoice_id = Column(String(255), nullable=True)
    original_amt = Column(Integer, nullable=False)
    final_amt = Column(Integer, nullable=False)
    plan_purchased = Column(String(255), nullable=False)
    upi = Column(Text, nullable=True)
    name = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    coupon_code = Column(String(255), nullable=True)  # can be changed to coupon.id and establish relationship
    razorpay_status = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    commissions = relationship("Commission", back_populates="payment")

    def __repr__(self):
        return f"<id - {self.id}, user_id - {self.user_id}, razorpay_payment_id - {self.razorpay_payment_id}, invoice_id - {self.invoice_id}>, plan_purchased= {self.plan_purchased}, notes = {self.notes}, notes = {self.notes}, coupon_code = {self.coupon_code}, name = {self.name}, phone = {self.phone}, razorpay_status = {self.razorpay_status}, email = {self.email}, upi = {self.upi}, created_at - {self.created_at}>"


class Coupon(Base, CommonThings):
    __tablename__ = 'coupon'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(15), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    discount_percent = Column(Integer, nullable=False)
    commission_percent = Column(Integer, nullable=False)
    applicable_plans = Column(Text, nullable=True)  # Comma-separated plan names
    valid_until = Column(DateTime, nullable=True)
    # user = relationship("User")  # Use a different name for backref
    commissions = relationship("Commission", back_populates="coupon", lazy='dynamic')


    def __repr__(self):
        return f"<Coupon id={self.id}, code={self.code}, discount_percent={self.discount_percent}, commission_percent={self.commission_percent}, valid_until={self.valid_until}, user_id={self.user_id}>"

class Commission(Base, CommonThings):
    __tablename__ = 'commission'
    id = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    referred_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    coupon_id = Column(Integer, ForeignKey('coupon.id'), nullable=False)
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=False)
    commission_amount = Column(Integer, nullable=False)
    commission_percent = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default='Pending')
    referrer = relationship("User", foreign_keys=[referrer_id], overlaps="referrer_commissions")
    referred = relationship("User", foreign_keys=[referred_id], overlaps="referred_commissions")
    coupon = relationship("Coupon")
    payment = relationship("Payment", back_populates="commissions")

    def __repr__(self):
        return f"<Commission id={self.id}, user_id={self.user_id}, coupon_id={self.coupon_id}, payment_id={self.payment_id}, commission_amount={self.commission_amount}, status={self.status}>"

class DailyLearning(Base, CommonThings):
    __tablename__ = 'daily_learning'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String(255), nullable=True, unique=True)
    information = Column(Text, nullable=True)
    platform = Column(String(50), nullable=True)
    taggs = relationship("Tagg", secondary="learning_tagg_link", back_populates="learnings")
    def __repr__(self):
        return f"<DailyLearning id={self.id}, link={self.link}, platform={self.platform}, information={self.information}>"


class Tagg(Base, CommonThings):
    __tablename__ = 'tagg'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    learnings = relationship("DailyLearning", secondary="learning_tagg_link", back_populates="taggs")
    def __repr__(self):
        return f"<Tagg id={self.id}, name={self.name}, created_at={self.created_at}>"
    
class LearningTaggLink(Base, CommonThings):
    __tablename__ = 'learning_tagg_link'
    learning_id = Column(Integer, ForeignKey('daily_learning.id'), primary_key=True)
    tagg_id = Column(Integer, ForeignKey('tagg.id'), primary_key=True)


class BlacklistedToken(Base, CommonThings):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False, unique=True)

    @classmethod
    def is_token_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class Post(Base, CommonThings):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lesson.id'), nullable=True)
    caption = Column(Text, nullable=True)
    is_private = Column(Boolean, default=False)
    is_handpicked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="posts")
    lesson = relationship("Lesson", back_populates="posts")
    media = relationship("Media", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    flags = relationship("PostFlag", back_populates="post", cascade="all, delete-orphan")

    def delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, lesson_id={self.lesson_id}, caption='{self.caption}', is_private={self.is_private}, created_at={self.created_at})>"



class Media(Base, CommonThings):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    original_filename = Column(String(255), nullable=False)  # Store the original filename
    file_path = Column(String(255), nullable=False)
    thumbnail_path = Column(String(255), nullable=True)  # For storing thumbnail path
    is_approved = Column(Boolean, default=False)
    is_video = Column(Boolean, default=False)
    is_gif = Column(Boolean, default=False)
    is_audio = Column(Boolean, default=True)
    post = relationship("Post", back_populates="media")

    # user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    # lesson_id = Column(Integer, ForeignKey('lesson.id'), nullable=True)
    # caption = Column(Text, nullable=True)
    # user_lesson_progress_id = Column(Integer, ForeignKey('user_lesson_progress.id'), nullable=True)  # New line
    # is_handpicked = Column(Boolean, default=False)
    # is_flagged = Column(Boolean, default=False)
    # user = relationship("User", back_populates="media")
    # lesson = relationship("Lesson", back_populates="media", uselist=False)
    # user_lesson_progress = relationship("UserLessonProgress", back_populates="media")
    # likes = relationship("PostLike", back_populates="media")
    # flags = relationship("PostFlag", back_populates="media")


class PostLike(Base, CommonThings):
    __tablename__ = 'post_like'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    # media_id = Column(Integer, ForeignKey('media.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="likes")


class PostFlag(Base, CommonThings):
    __tablename__ = 'post_flag'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    # media_id = Column(Integer, ForeignKey('media.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    user = relationship("User", back_populates="post_flags")
    post = relationship("Post", back_populates="flags")

class ApiList(Base, CommonThings):
    __tablename__ = 'api_list'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    welcome_text = Column(Text)
    command_description = Column(Text)
    credit_cost = Column(Integer)
    params = Column(Text)  # JSON-encoded string of parameters
    success_message = Column(Text)
    error_message = Column(Text)

class ApiUsage(Base, CommonThings):
    __tablename__ = 'api_usage'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    api_id = Column(Integer, ForeignKey('api_list.id'))
    parameters = Column(Text)  # JSON string of parameters
    response = Column(Text)  # JSON string of response
    prompt_token_count = Column(Integer)
    response_token_count = Column(Integer)
    status = Column(String(50))
    credits_charged = Column(Integer)
    user = relationship("User", back_populates="api_usages")
    api = relationship("ApiList")

class CreditTransaction(Base, CommonThings):
    __tablename__ = 'credit_transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    credits_changed = Column(Numeric)
    reason = Column(String(255))
    user = relationship("User", back_populates="credit_transactions")

class RechargePackage(Base):
    __tablename__ = 'recharge_packages'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    credits = Column(Numeric, nullable=False)
    description = Column(String(255))
    prices = Column(JSON)  # This column will store prices in JSON format for different regions
    rzp_ai_toolbox_payments = relationship("RzpAIToolboxPayment", back_populates="package")
    def __repr__(self):
        return f"<RechargePackage(id={self.id}, credits={self.credits}, description={self.description})>"

class State(Base, CommonThings):
    __tablename__ = 'state'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False, default="India")
    cities = relationship('City', back_populates='state')

    def __repr__(self):
        return f"<State id={self.id}, name={self.name}, country={self.country}>"


class City(Base, CommonThings):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    state_id = Column(Integer, ForeignKey('state.id'), nullable=False)
    # country = Column(String(255), nullable=False)
    state = relationship('State', back_populates='cities')
    colleges = relationship('College', back_populates='city')

    def __repr__(self):
        return f"<City id={self.id}, name={self.name}, state_id={self.state_id}>"


class College(Base, CommonThings):
    __tablename__ = 'college'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    city_id = Column(Integer, ForeignKey('city.id'), nullable=False)
    address = Column(Text, nullable=True)
    discipline = Column(String(255), nullable=True)
    principal_name = Column(String(255), nullable=True)
    principal_email = Column(String(255), nullable=True)
    principal_phone = Column(String(20), nullable=True)
    tpo_name = Column(String(255), nullable=True)
    tpo_email = Column(String(255), nullable=True)
    tpo_phone = Column(String(20), nullable=True)
    teachers_info = Column(Text, nullable=True)  # Can store JSON or serialized info about teachers
    notes = Column(Text, nullable=True)
    whatsapp_groups = Column(Text, nullable=True)  # Can store group names or URLs
    telegram_group = Column(String(255), nullable=True)
    flyer_path = Column(String(255), nullable=True)  # Add this line
    flyer_generated_at = Column(DateTime, nullable=True)  # New column to store the flyer generation time

    city = relationship('City', back_populates='colleges')
    students = relationship('Student', back_populates='college')
    teachers = relationship('Teacher', back_populates='college')

    def __repr__(self):
        return f"<College id={self.id}, name={self.name}, full_name={self.full_name}>"

class Student(Base, CommonThings):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    college_id = Column(Integer, ForeignKey('college.id'), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    official_email = Column(String(255), unique=False, nullable=True) #TODO - check unique and nullable later
    course_name = Column(String(255), nullable=True)
    branch = Column(String(255), nullable=True)
    year_of_study = Column(Integer, nullable=False)
    batch_year = Column(Integer, nullable=False)

    college = relationship('College', back_populates='students')
    user = relationship('User', back_populates='students')

    def __repr__(self):
        return f"<Student id={self.id}, name={self.name}, college_id={self.college_id}, year_of_study={self.year_of_study}, batch_year={self.batch_year}>"

class Teacher(Base, CommonThings):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    college_id = Column(Integer, ForeignKey('college.id'), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    official_email = Column(String(255), unique=False, nullable=True) #TODO - check unique and nullable later
    discipline = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    designation = Column(String(255), nullable=True)
    experience_years = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    college = relationship('College', back_populates='teachers')
    user = relationship('User', back_populates='teachers')

    def __repr__(self):
        return f"<Teacher id={self.id}, name={self.name}, email={self.email}, department={self.department}, designation={self.designation}>"

# class RzpPaymentLinks(Base, CommonThings):
#     __tablename__ = 'rzp_payment_links'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     link = Column(String(255))
#     amount = Column(Numeric)
#     description = Column(String(255))
#     reference_id = Column(String(255))
#     plink_id = Column(String(255))
#     webhook_event_id = Column(Integer, ForeignKey('payment_webhook_events.id'))
#     pack_name = Column(String(255))
#     user = relationship("User", back_populates="rzp_payment_links")
#     rzp_webhook_event = relationship("RzpPaymentWebhookEvent", back_populates="rzp_payment_link")

# class RzpPaymentWebhookEvent(Base, CommonThings):
#     __tablename__ = 'payment_webhook_events'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     payment_id = Column(String(255))
#     event_type = Column(String(255))
#     order_id = Column(String(255))
#     method = Column(String(50))
#     captured = Column(Boolean)
#     vpa = Column(String(255))
#     email = Column(String(255))
#     contact = Column(String(255))
#     notes = Column(Text)
#     fee = Column(String(255))
#     tax = Column(String(255))
#     amount = Column(Numeric)
#     status = Column(String(50))
#     description = Column(String(255))
#     user = relationship("User")
#     rzp_payment_link = relationship("RzpPaymentLinks", back_populates='rzp_webhook_event')

class RzpAIToolboxPayment(Base, CommonThings):
    __tablename__ = 'ai_toolbox_payment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    package_id = Column(Integer, ForeignKey('recharge_packages.id'))
    razorpay_payment_id = Column(String(255))
    razorpay_order_id = Column(String(255))
    amount_paid = Column(Numeric)
    status = Column(String(50))  # Could be 'paid', 'failed', etc.
    notes = Column(Text, nullable=True)
    complete_output = Column(Text, nullable=True)
    user = relationship("User", back_populates="rzp_ai_toolbox_payments")
    package = relationship("RechargePackage", back_populates="rzp_ai_toolbox_payments")


# class Usage(Base, CommonThings):
#     __tablename__ = 'usage'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
#     api_id = Column(Integer, ForeignKey('api.id'), nullable=False)
#     api_name = Column(String(255), nullable=True)
#     api_route = Column(String(255), nullable=False)
#     input_query = Column(String(255), nullable=True)
#     product_name = Column(String(255), nullable=True)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     last_updated_on = Column(DateTime, default=datetime.now(timezone.utc))
#     user = relationship("User")
#     api = relationship("Api")

#     def __repr__(self):
#         return f"<id - {self.id}, user_id - {self.user_id}, api_name - {self.api_name}, api_route - {self.api_route}, created_at - {self.created_at}, last_updated_on - {self.last_updated_on} >"


# class Api(Base, CommonThings):
#     __tablename__ = 'api'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     api_name = Column(String(255), nullable=False)
#     api_route = Column(String(255), nullable=True)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     last_updated_on = Column(DateTime, default=datetime.now(timezone.utc))
#     usages = relationship("Usage", back_populates="api", lazy='dynamic')
#     history = relationship("History", back_populates="api", lazy='dynamic')

#     def __repr__(self):
#         return f"<id - {self.id}, api_name - {self.api_name}, api_route - {self.api_route}, created_at - {self.created_at}, last_updated_on - {self.last_updated_on} >"


# class History(Base, CommonThings):
#     __tablename__ = 'history'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(String(255), ForeignKey('user.id'), nullable=False)
#     user_email = Column(String(255), nullable=False)
#     api_id = Column(String(255), ForeignKey('api.id'), nullable=False)
#     input = Column(Text, nullable=False)
#     output   = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#     last_updated_on = Column(DateTime, default=datetime.now(timezone.utc))
#     user = relationship("User")
#     api = relationship("Api")

#     def __repr__(self):
#         return f"<id - {self.id}, api_name - {self.api_name}, api_route - {self.api_route}, created_at - {self.created_at}, last_updated_on - {self.last_updated_on} >"

