# social.py
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import College, Post, PostLike, Student, Teacher, User,Follow, Media  # Assuming you have these models defined
from sqlalchemy import func
from db_helper import Session  # Ensure you have a session manager for SQLAlchemy
from flask import request, jsonify, url_for
from backend.helpers.file_upload_helper import save_avatar_with_thumbnail
from werkzeug.datastructures import FileStorage
from backend.helpers.utils import Settings
from backend.helpers.repository import generate_presigned_url, extract_s3_key_from_url
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

social_ns = Namespace('social', description='Social features')

# user_model = social_ns.model('User', {
#     'id': fields.Integer(required=True, description='User ID'),
#     'username': fields.String(required=True, description='Username'),
#     # 'name': fields.String(description='Name of the user'),
#     'bio': fields.String(description='User bio'),
#     'avatarUrl': fields.String(description='URL to user avatar'),
#     # 'postsCount': fields.Integer(description='Number of posts by the user'),
#     # 'followersCount': fields.Integer(description='Number of followers'),
#     # 'followingCount': fields.Integer(description='Number of following'),
# })

# post_model = social_ns.model('Post', {
#     'id': fields.Integer(required=True, description='Post ID'),
#     # 'thumbnail': fields.String(required=True, description='URL to post thumbnail'),
#     # 'likeCount': fields.Integer(description='Number of likes'),
#     # Add more fields as needed
# })

@social_ns.route('/user/<string:username>')
class UserProfile(Resource):
    @jwt_required(optional=True)
    def get(self, username):
        with Session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return {"error": "User not found"}, 404
            posts_count = session.query(func.count(Post.id)).filter(Post.user_id == user.id, Post.deleted_at == None).scalar()
            
            avatar_url = user.avatar_url or url_for('static', filename='images/default-avatar.jpg', _external=False)
            avatar_thumbnail_url = user.avatar_thumbnail_url or avatar_url

            return {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'fullname': user.fullname,
                'bio': user.bio,
                # 'avatarUrl': user.avatar_url,
                'avatarThumbnailUrl': avatar_thumbnail_url,
                'postsCount': posts_count,
                'followersCount': 0,  # Implement logic for counting followers
                'followingCount': 0,  # Implement logic for counting following
                'created_at': f"{user.created_at}"
            }, 200


@social_ns.route('/user/<string:username>/posts')
class UserPosts(Resource):
    @jwt_required(optional=True)
    def get(self, username):
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Define your default items per page
        offset = (page - 1) * per_page

        with Session() as session:
            passed_user = session.query(User).filter_by(username=username).first()
            if not passed_user:
                return {"message": "Passed user not found"}, 404
            # print(passed_user)
            # Fetch the total number of posts to calculate total pages later
            total_posts = session.query(func.count(Post.id)).filter(Post.user_id == passed_user.id).scalar()
            total_pages = (total_posts + per_page - 1) // per_page  # Calculate total pages
            
            # Fetch the posts for the current page
            # posts = session.query(Post).filter(Post.user_id == passed_user.id).offset(offset).limit(per_page).all()
            posts = session.query(Post).options(joinedload(Post.media)).filter(Post.user_id == passed_user.id, Post.is_deleted==False).order_by(Post.created_at.desc()).offset(offset).limit(per_page).all()

            if not posts and page ==1:
                return {"message": "No posts found for this user. User activities uploaded for the lessons appear here automatically."}, 200

            post_ids = [post.id for post in posts]
            like_counts = session.query(
                PostLike.post_id,
                func.count(PostLike.id).label('like_count')
            ).filter(
                PostLike.post_id.in_(post_ids)
            ).group_by(
                PostLike.post_id
            ).all()
            like_counts_dict = {like.post_id: like.like_count for like in like_counts}

            loggedin_user_email = get_jwt_identity()  # Get the ID of the currently authenticated user
            loggedin_user = session.query(User).filter_by(email=loggedin_user_email).first()
            
            posts_data = []
            for post in posts:
                media_items = []
                for media in post.media:
                    one_media = {
                        'id': media.id, 
                        'file_path': media.file_path, 
                        'thumbnail_path': media.thumbnail_path, 
                        'is_video': media.is_video, 
                        'is_gif': media.is_gif
                        }
                    if Settings.environment == 'production':
                        object_name_file = extract_s3_key_from_url(one_media.get('file_path')) 
                        # print('object_name_file', object_name_file)
                        object_name_thumbnail = extract_s3_key_from_url(one_media.get('thumbnail_path'))
                        # print('object_name_thumbnail', object_name_thumbnail)
                        presigned_file_url = generate_presigned_url(bucket_name=Settings.s3_bucket_name, object_name=object_name_file)
                        # print('presigned_file_url', presigned_file_url)
                        presigned_thumbnail_url = generate_presigned_url(bucket_name=Settings.s3_bucket_name, object_name=object_name_thumbnail)
                        # print('presigned_thumbnail_url', presigned_thumbnail_url)
                        # print('presigned file and thumbnail urls')

                        if presigned_file_url:
                            one_media.update({
                                'presigned_file_url': presigned_file_url if presigned_file_url else '',
                                'presigned_thumbnail_url': presigned_thumbnail_url if presigned_thumbnail_url else ''
                            })
                        # print('one_media', one_media)
                    # print('one_media', one_media)
                    media_items.append(one_media)
                # like_count = session.query(func.count(PostLike.id)).filter(PostLike.post_id == post.id).scalar()
                liked_by_loggedin_user = False

                if loggedin_user:
                    liked_by_loggedin_user = session.query(PostLike).filter_by(post_id=post.id, user_id=loggedin_user.id).count() > 0
                    print('indside')

                # print('like_count --->', like_count)
                print('likedByCurrentUser --->', liked_by_loggedin_user)

                thumbnail_media = media_items[0] if media_items else None
                thumbnail_path = thumbnail_media['thumbnail_path'] if thumbnail_media else None
                
                post_item = {
                    'id': post.id,
                    'caption': post.caption,
                    'thumbnail_path': thumbnail_path.replace('\\', '/') if thumbnail_path else None,
                    'media': media_items,  # Include all media items associated with the post
                    # 'likesCount': like_count,
                    'likesCount': like_counts_dict.get(post.id, 0),
                    'likedByCurrentUser': liked_by_loggedin_user,
                    'username': post.user.username,
                    'is_video': True if media.is_video else False, 
                    'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'lessonTitle': post.lesson.title if post.lesson else None  # Fetch the lesson title
                }
                posts_data.append(post_item)
            return {
                'posts': posts_data,
                'total': total_posts,
                'pages': total_pages,
                'current_page': page
            }, 200
            

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@social_ns.route('/user/<string:username>/avatar', methods=['PUT'])
class UpdateUserAvatar(Resource):
    @jwt_required()
    def put(self, username):
        current_user_email = get_jwt_identity()
        if 'avatar' not in request.files:
            return {"error": "No file uploaded"}, 400
        
        file = request.files['avatar']
        if file.filename == '':
            return {"error": "No file selected"}, 400

        if not allowed_file(file.filename):
            return {"error": "File type not allowed"}, 400

        file_url, avatar_thumbnail_url = save_avatar_with_thumbnail(file, subfolder='avatar')
        # if error:
        #     return {"error": error}, 500

        # Optional: Generate a thumbnail from the avatar
        # avatar_thumbnail_url = generate_square_thumbnail_avatar(file_url, subfolder='avatar')
        # if thumbnail_error:
            # return {"error": thumbnail_error}, 500

        # Update user's avatar URL in the database
        with Session() as session:
            user = session.query(User).filter_by(email=current_user_email).first()
            if user.username != username:
                return {"error": "Unauthorized"}, 403
            user.avatar_url = file_url
            user.avatar_thumbnail_url = avatar_thumbnail_url if avatar_thumbnail_url else file_url
            user.updated_at=datetime.now(timezone.utc)
            session.commit()
        
        return {"avatarUrl": file_url, "avatarThumbnailUrl": avatar_thumbnail_url}, 200


@social_ns.route('/user/<string:username>', methods=['PUT'])
class UpdateUserProfile(Resource):
    @jwt_required()
    def put(self, username):  # Use 'put' to match the HTTP PUT method
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()
            if not current_user:
                return {"error": "User not found"}, 404

            if current_user.username != username:
                return jsonify({"error": "Unauthorized"}), 403

            data = request.get_json()
            current_user.fullname = data.get('fullname', current_user.fullname)
            current_user.bio = data.get('bio', current_user.bio)
            current_user.updated_at=datetime.now(timezone.utc)
            session.commit()
            
            return {"message": "Profile updated successfully"}, 200


@social_ns.route('/public_feed')
class PublicFeed(Resource):
    @jwt_required(optional=True)
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Default items per page
        offset = (page - 1) * per_page

        # Extract user_id from headers (sent from frontend)
        user_id = request.headers.get("user-id")#ganesh

        with Session() as session:
            # Get logged-in user details (fallback to JWT if user_id is not provided) ganesh
            loggedin_user = None
            if user_id:
                loggedin_user = session.query(User).filter_by(id=user_id).first()
            else:
                loggedin_user_email = get_jwt_identity()
                if loggedin_user_email:
                    loggedin_user = session.query(User).filter_by(email=loggedin_user_email).first()

            # Fetch posts
            subquery = (
                session.query(Post.id)
                .filter(Post.is_deleted == False)
                .order_by(Post.created_at.desc())
                # .limit(20)  # Limit to 2 posts per user for diversity
                .subquery()
            )
            posts = (
                session.query(Post)
                .filter(Post.id.in_(subquery))
                .order_by(Post.created_at.desc())
                .offset(offset)
                .limit(per_page)
                .all()
            )

            # Fetching like counts and checking if the current user liked the posts
            post_ids = [post.id for post in posts]
            like_counts = session.query(
                PostLike.post_id,
                func.count(PostLike.id).label('like_count')
            ).filter(
                PostLike.post_id.in_(post_ids)
            ).group_by(
                PostLike.post_id
            ).all()

            like_counts_dict = {like.post_id: like.like_count for like in like_counts}

            # Check if the logged-in user liked the posts ganesh
            user_liked_posts = set()
            if loggedin_user:
                liked_posts = session.query(PostLike.post_id).filter(
                    PostLike.post_id.in_(post_ids),
                    PostLike.user_id == loggedin_user.id
                ).all()
                user_liked_posts = {lp.post_id for lp in liked_posts}

            posts_data = []
            for post in posts:
                media_items = [
                    {
                        'id': media.id,
                        'file_path': media.file_path,
                        'thumbnail_path': media.thumbnail_path,
                        'is_video': media.is_video,
                        'is_gif': media.is_gif
                    } for media in post.media
                ]

                # Determine college name
                college_name = None
                student = session.query(Student).filter_by(user_id=post.user_id).first()
                if student:
                    college = session.query(College).filter_by(id=student.college_id).first()
                    college_name = college.name if college else None
                else:
                    teacher = session.query(Teacher).filter_by(user_id=post.user_id).first()
                    if teacher:
                        college = session.query(College).filter_by(id=teacher.college_id).first()
                        college_name = college.name if college else None

                post_item = {
                    'id': post.id,
                    'caption': post.caption,
                    'avatar': post.user.avatar_url,
                    'media': media_items,
                    'likesCount': like_counts_dict.get(post.id, 0),
                    'likedByCurrentUser': post.id in user_liked_posts,
                    'username': post.user.username,
                    'isCreatorVerified': post.user.current_plan_name != 'beginner',
                    'collegeName': college_name,
                    'is_video': any(media.is_video for media in post.media),
                    'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'lessonTitle': post.lesson.title if post.lesson else None,
                    'lessonLink': f"/lesson/{post.lesson.slug}" if post.lesson else None
                }
                posts_data.append(post_item)

            return {
                'posts': posts_data,
                'total': len(posts_data),
                'current_page': page
            }, 200


@social_ns.route('/post/<int:post_id>')
class IndividualPost(Resource):
    @jwt_required(optional=True)
    def get(self, post_id):
        with Session() as session:
            post = session.query(Post).filter_by(id=post_id).first()
            if not post:
                return {'message': 'Post not found'}, 404

            loggedin_user_email = get_jwt_identity()
            loggedin_user = session.query(User).filter_by(email=loggedin_user_email).first() if loggedin_user_email else None

            liked_by_loggedin_user = False
            if loggedin_user:
                liked_by_loggedin_user = session.query(PostLike).filter_by(post_id=post.id, user_id=loggedin_user.id).count() > 0

            # Fetch college name
            college_name = None
            student = session.query(Student).filter_by(user_id=post.user_id).first()
            if student:
                college = session.query(College).filter_by(id=student.college_id).first()
                college_name = college.name if college else None
            else:
                teacher = session.query(Teacher).filter_by(user_id=post.user_id).first()
                if teacher:
                    college = session.query(College).filter_by(id=teacher.college_id).first()
                    college_name = college.name if college else None

            media_items = [
                {
                    'id': media.id,
                    'file_path': media.file_path,
                    'thumbnail_path': media.thumbnail_path,
                    'is_video': media.is_video,
                    'is_gif': media.is_gif
                } for media in post.media
            ]

            if Settings.environment == 'production':
                for item in media_items:
                    item['presigned_file_url'] = generate_presigned_url(bucket_name=Settings.s3_bucket_name, object_name=extract_s3_key_from_url(item['file_path']))
                    item['presigned_thumbnail_url'] = generate_presigned_url(bucket_name=Settings.s3_bucket_name, object_name=extract_s3_key_from_url(item['thumbnail_path']))

            post_data = {
                'id': post.id,
                'caption': post.caption,
                'avatar': post.user.avatar_url,
                'media': media_items,
                'likesCount': session.query(func.count(PostLike.id)).filter_by(post_id=post.id).scalar(),
                'liked': liked_by_loggedin_user,
                'username': post.user.username,
                'collegeName': college_name,
                'is_video': any(media.is_video for media in post.media),
                'isCreatorVerified': False if post.user.current_plan_name == 'beginner' else True,
                'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'lessonTitle': post.lesson.title if post.lesson else None,
                'lessonLink': f"/lesson/{post.lesson.slug}" if post.lesson else None,
                # 'commentCount': session.query(func.count(Comment.id)).filter_by(post_id=post.id).scalar()
            }

            return post_data, 200


@social_ns.route('/top_contributors')
class TopContributors(Resource):
    def get(self):
        with Session() as session:
            # This is a simple example. You might want to implement more sophisticated
            # logic to determine top contributors based on your specific criteria.
            top_users = session.query(User)\
                .join(Post)\
                .group_by(User.id)\
                .order_by(func.count(Post.id).desc())\
                .limit(5)\
                .all()

            contributors = [
                {
                    'username': user.username,
                    'avatar': user.avatar_thumbnail_url or user.avatar_url or url_for('static', filename='images/default-avatar.jpg', _external=False)
                }
                for user in top_users
            ]
            # print(contributors)

            return {'contributors': contributors}, 200
        

@social_ns.route('/user/<string:username>/follow')
class FollowUser(Resource):
    @jwt_required()
    def post(self, username):
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()
            target_user = session.query(User).filter_by(username=username).first()

            if not target_user:
                return {"error": "User not found"}, 404

            if target_user.id == current_user.id:
                return {"error": "You cannot follow yourself"}, 400

            # Check if already following
            follow_exists = session.query(Follow).filter_by(follower_id=current_user.id, followed_id=target_user.id).first()
            if follow_exists:
                return {"message": "Already following this user"}, 200

            # Create new follow relationship
            new_follow = Follow(follower_id=current_user.id, followed_id=target_user.id)
            session.add(new_follow)
            session.commit()

            return {"message": f"Started following {username}"}, 200


@social_ns.route('/user/<string:username>/unfollow')
class UnfollowUser(Resource):
    @jwt_required()
    def post(self, username):
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()
            target_user = session.query(User).filter_by(username=username).first()

            if not target_user:
                return {"error": "User not found"}, 404

            # Check if the follow relationship exists
            follow = session.query(Follow).filter_by(follower_id=current_user.id, followed_id=target_user.id).first()
            if not follow:
                return {"message": "You are not following this user"}, 400

            session.delete(follow)
            session.commit()

            return {"message": f"Stopped following {username}"}, 200


@social_ns.route('/user/<string:username>/followers')
class UserFollowers(Resource):
    @jwt_required(optional=True)
    def get(self, username):
        with Session() as session:
            target_user = session.query(User).filter_by(username=username).first()

            if not target_user:
                return {"error": "User not found"}, 404

            followers = (
                session.query(User)
                .join(Follow, Follow.follower_id == User.id)
                .filter(Follow.followed_id == target_user.id)
                .all()
            )

            follower_list = [{'id': follower.id, 'username': follower.username} for follower in followers]

            return {"followers": follower_list}, 200


@social_ns.route('/user/<string:username>/following')
class UserFollowing(Resource):
    @jwt_required(optional=True)
    def get(self, username):
        with Session() as session:
            target_user = session.query(User).filter_by(username=username).first()

            if not target_user:
                return {"error": "User not found"}, 404

            following = (
                session.query(User)
                .join(Follow, Follow.followed_id == User.id)
                .filter(Follow.follower_id == target_user.id)
                .all()
            )

            following_list = [{'id': followed_user.id, 'username': followed_user.username} for followed_user in following]

            return {"following": following_list}, 200


@social_ns.route('/user/<string:username>/follow-request')
class FollowRequest(Resource):
    @jwt_required()
    def post(self, username):
        """Send a follow request to a user"""
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()
            target_user = session.query(User).filter_by(username=username).first()

            if not target_user:
                return {"error": "User not found"}, 404

            if target_user.id == current_user.id:
                return {"error": "You cannot follow yourself"}, 400

            existing_request = session.query(Follow).filter_by(
                follower_id=current_user.id, followed_id=target_user.id
            ).first()

            if existing_request:
                return {"message": "Follow request already sent"}, 200

            follow_request = Follow(follower_id=current_user.id, followed_id=target_user.id, status="pending")
            session.add(follow_request)
            session.commit()

            return {"message": "Follow request sent"}, 200


@social_ns.route('/user/<string:username>/accept-follow')
class AcceptFollowRequest(Resource):
    @jwt_required()
    def post(self, username):
        """Accept a follow request"""
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()
            requester = session.query(User).filter_by(username=username).first()

            if not requester:
                return {"error": "User not found"}, 404

            follow_request = session.query(Follow).filter_by(
                follower_id=requester.id, followed_id=current_user.id, status="pending"
            ).first()

            if not follow_request:
                return {"error": "No pending follow request from this user"}, 400

            follow_request.status = "accepted"
            session.commit()

            return {"message": f"You are now following {username}"}, 200


@social_ns.route('/user/<string:username>/reject-follow')
class RejectFollowRequest(Resource):
    @jwt_required()
    def post(self, username):
        """Reject a follow request"""
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()
            requester = session.query(User).filter_by(username=username).first()

            if not requester:
                return {"error": "User not found"}, 404

            follow_request = session.query(Follow).filter_by(
                follower_id=requester.id, followed_id=current_user.id, status="pending"
            ).first()

            if not follow_request:
                return {"error": "No pending follow request from this user"}, 400

            session.delete(follow_request)
            session.commit()

            return {"message": f"Follow request from {username} rejected"}, 200


@social_ns.route('/user/follow-requests')
class PendingFollowRequests(Resource):
    @jwt_required()
    def get(self):
        """Get list of follow requests received"""
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()

            requests = (
                session.query(User)
                .join(Follow, Follow.follower_id == User.id)
                .filter(Follow.followed_id == current_user.id, Follow.status == "pending")
                .all()
            )

            request_list = [{'id': user.id, 'username': user.username} for user in requests]

            return {"pending_requests": request_list}, 200
