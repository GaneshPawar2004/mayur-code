from flask_restx import Namespace, Resource
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_helper import Session
from models import User, Followers

# Create a namespace
follow_ns = Namespace('Follow', description='User follow/unfollow operations')

@follow_ns.route('/follow/<int:user_id>')
class FollowUser(Resource):
    @jwt_required()
    def post(self, user_id):
        """Follow a user"""
        current_user_id = get_jwt_identity()

        if current_user_id == user_id:
            return jsonify({"error": "You cannot follow yourself"}), 400

        with Session() as session:
            current_user = session.get(User, current_user_id)
            user_to_follow = session.get(User, user_id)

            if not current_user or not user_to_follow:
                return jsonify({"error": "User not found"}), 404

            # Check if already following
            existing_follow = session.query(Followers).filter_by(
                follower_id=current_user_id, following_id=user_id).first()

            if existing_follow:
                return jsonify({"message": "Already following"}), 400

            # Add to followers table
            new_follow = Followers(follower_id=current_user_id, following_id=user_id)
            session.add(new_follow)
            session.commit()

            return jsonify({"message": f"You are now following {user_to_follow.username}"}), 200


@follow_ns.route('/unfollow/<int:user_id>')
class UnfollowUser(Resource):
    @jwt_required()
    def post(self, user_id):
        """Unfollow a user"""
        current_user_id = get_jwt_identity()

        with Session() as session:
            current_user = session.get(User, current_user_id)
            user_to_unfollow = session.get(User, user_id)

            if not current_user or not user_to_unfollow:
                return jsonify({"error": "User not found"}), 404

            # Check if actually following
            follow_entry = session.query(Followers).filter_by(
                follower_id=current_user_id, following_id=user_id).first()

            if not follow_entry:
                return jsonify({"message": "Not following this user"}), 400

            session.delete(follow_entry)
            session.commit()

            return jsonify({"message": f"You have unfollowed {user_to_unfollow.username}"}), 200


@follow_ns.route('/followers/<int:user_id>')
class GetFollowers(Resource):
    def get(self, user_id):
        """Get list of followers"""
        with Session() as session:
            user = session.get(User, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            followers_list = [
                {"id": follower.follower_id, "username": follower.follower.username}
                for follower in user.followers
            ]

            return jsonify({"followers": followers_list})


@follow_ns.route('/following/<int:user_id>')
class GetFollowing(Resource):
    def get(self, user_id):
        """Get list of users the current user is following"""
        with Session() as session:
            user = session.get(User, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            following_list = [
                {"id": following.following_id, "username": following.following.username}
                for following in user.following
            ]

            return jsonify({"following": following_list})
