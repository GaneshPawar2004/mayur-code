"""
This is the main file for run our flask application.
"""
from app import app, jwt, db
from models import ApiList, ApiUsage, BankDetails, CreditTransaction, LessonTagLink, Media, PostFlag, PostLike, Post, RechargePackage, RzpAIToolboxPayment, State, Supersection, User, Payment, BlacklistedToken, Coupon, Commission, DailyLearning, Tag, LearningTaggLink, Lesson, Section, UserLessonProgress, Tagg, UserSectionProgress, City, College, Student, Teacher, Followers
from db_helper import engine, Session, Base
import razorpay
from flask import request, render_template, jsonify
from helpers.seed import seed_states, seed_tags, seed_coupons, seed_sections, seed_lessons, seed_supersections, seed_taggs, seed_ai_toolbox_apis, seed_recharge_packs



@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = BlacklistedToken.query.filter_by(jti=jti).first()
    return token is not None


# razorpay_client = razorpay.Client(auth=("RAZORPAY_KEY", "RAZORPAY_SECRET"))

"""
@app.route('/get_plan', methods=['GET'])
def get_plan():
    email = request.args.get('email')
    
    # No email provided in the request
    if not email:
        return jsonify({"error": "Email parameter is required!"}), 400

    session = Session()
    try:
        user = session.query(User).filter_by(email=email).first()
        
        # User not found in the database
        if not user:
            return jsonify({"error": "User not found!"}), 404

        # Check if the user has made any payment
        payment = session.query(Payment).filter_by(user_id=user.id).first()

        if user.plan_name == 'basic' and not payment:
            return jsonify({"plan": "basic", "message": "Upgrade to Advance"})
        elif user.plan_name == 'advance' and payment:
            return jsonify({"plan": "advance", "message": "Selected"})
        else:
            return jsonify({"error": "Invalid plan or payment status!"}), 400
    finally:
        session.close()
"""

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # # Create tables in the DB if not already exists.
    User.__table__.create(engine, checkfirst=True)
    #ganesh
    Followers.__table__.create(engine, checkfirst=True)

    BankDetails.__table__.create(engine, checkfirst=True)
    Payment.__table__.create(engine, checkfirst=True)
    Coupon.__table__.create(engine, checkfirst=True)
    Commission.__table__.create(engine, checkfirst=True)
    Tagg.__table__.create(engine, checkfirst=True)
    DailyLearning.__table__.create(engine, checkfirst=True)
    LearningTaggLink.__table__.create(engine, checkfirst=True)
    # # Usage.__table__.create(engine, checkfirst=True)
    # # Api.__table__.create(engine, checkfirst=True)
    # # History.__table__.create(engine, checkfirst=True)
    BlacklistedToken.__table__.create(engine, checkfirst=True)
    Tag.__table__.create(engine, checkfirst=True)
    Supersection.__table__.create(engine, checkfirst=True)
    Section.__table__.create(engine, checkfirst=True)
    Lesson.__table__.create(engine, checkfirst=True)
    LessonTagLink.__table__.create(engine, checkfirst=True)
    Media.__table__.create(engine, checkfirst=True)
    Post.__table__.create(engine, checkfirst=True)
    PostLike.__table__.create(engine, checkfirst=True)
    PostFlag.__table__.create(engine, checkfirst=True)
    UserLessonProgress.__table__.create(engine, checkfirst=True)
    UserSectionProgress.__table__.create(engine, checkfirst=True)
    ApiList.__table__.create(engine, checkfirst=True)
    ApiUsage.__table__.create(engine, checkfirst=True)
    CreditTransaction.__table__.create(engine, checkfirst=True)
    RechargePackage.__table__.create(engine, checkfirst=True)
    RzpAIToolboxPayment.__table__.create(engine, checkfirst=True)
    State.__table__.create(engine, checkfirst=True)
    City.__table__.create(engine, checkfirst=True)
    College.__table__.create(engine, checkfirst=True)
    Student.__table__.create(engine, checkfirst=True)
    Teacher.__table__.create(engine, checkfirst=True)
    


    seed_tags()
    seed_taggs()
    seed_coupons()
    seed_supersections()
    seed_sections()
    seed_lessons()
    seed_ai_toolbox_apis()
    seed_recharge_packs()
    seed_states()
    # seed_users()
    # delete_unwanted_lessons_sections_supersections()


    # Run flask application.
    app.run()
 
