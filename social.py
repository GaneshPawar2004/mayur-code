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

@social_ns.route('/user/<string:username>/is-following')
class IsFollowingUser(Resource):
    @jwt_required()  # Make sure this is correctly verifying tokens
    def get(self, username):
        """Check if the authenticated user is following the given username"""
        current_user_email = get_jwt_identity()
        with Session() as session:
            current_user = session.query(User).filter_by(email=current_user_email).first()
            target_user = session.query(User).filter_by(username=username).first()

            if not target_user:
                return {"error": "User not found"}, 404

            # Check if the follow relationship exists
            follow = session.query(Follow).filter_by(
                follower_id=current_user.id,
                followed_id=target_user.id,
                status="accepted"  # Ensure only accepted follow relationships are checked
            ).first()

            return {"is_following": bool(follow)}, 200
