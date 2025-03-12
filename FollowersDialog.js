import { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, Button, Box, Typography } from "@mui/material";
import axiosInstance from '../../pages/authentication/axiosSetup';

const FollowersFollowingDialog = ({ open, handleClose, title, users = [], onFollow, onUnfollow }) => {
    const loggedInUserEmail = localStorage.getItem("user_email"); 
    const [followingUsers, setFollowingUsers] = useState({});
    const [followRequests, setFollowRequests] = useState([]); 

    // Fetch follow status for users
    const fetchFollowStatus = async () => {
        const authStateString = localStorage.getItem("authState");  
        if (!authStateString) return;

        const authState = JSON.parse(authStateString);
        if (!authState.access_token) return;

        const token = authState.access_token; 
        const statusMap = {};

        for (const user of users) {
            try {
                const response = await axiosInstance.get(
                    `/api/social/user/${user.username}/is-following`,
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                statusMap[user.username] = response.data.is_following;
            } catch {
                statusMap[user.username] = false;
            }
        }
        setFollowingUsers(statusMap);
    };

    // Fetch pending follow requests
    const fetchPendingRequests = async () => {
        const authStateString = localStorage.getItem("authState");  
        if (!authStateString) return;

        const authState = JSON.parse(authStateString);
        if (!authState.access_token) return;

        try {
            const response = await axiosInstance.get(
                "/api/social/user/follow-requests",
                { headers: { Authorization: `Bearer ${authState.access_token}` } }
            );
            setFollowRequests(response.data.pending_requests || []);
        } catch (error) {
            console.error("Error fetching follow requests:", error);
        }
    };

    // Accept follow request
    const handleAcceptRequest = async (username) => {
        const authStateString = localStorage.getItem("authState");  
        if (!authStateString) return;

        const authState = JSON.parse(authStateString);
        if (!authState.access_token) return;

        try {
            await axiosInstance.post(
                `/api/social/user/${username}/accept-follow`,
                {},
                { headers: { Authorization: `Bearer ${authState.access_token}` } }
            );
            setFollowRequests(followRequests.filter(user => user.username !== username));
        } catch (error) {
            console.error("Error accepting follow request:", error);
        }
    };

    // Reject follow request
    const handleRejectRequest = async (username) => {
        const authStateString = localStorage.getItem("authState");  
        if (!authStateString) return;

        const authState = JSON.parse(authStateString);
        if (!authState.access_token) return;

        try {
            await axiosInstance.post(
                `/api/social/user/${username}/reject-follow`,
                {},
                { headers: { Authorization: `Bearer ${authState.access_token}` } }
            );
            setFollowRequests(followRequests.filter(user => user.username !== username));
        } catch (error) {
            console.error("Error rejecting follow request:", error);
        }
    };

    useEffect(() => {
        if (open) {
            fetchFollowStatus();
            fetchPendingRequests();
        }
    }, [open, users]); 

    return (
        <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>
                {/* Pending Follow Requests Section */}
                <Typography variant="h6">Pending Follow Requests</Typography>
                {followRequests.length === 0 ? (
                    <Typography>No pending follow requests.</Typography>
                ) : (
                    followRequests.map((user) => (
                        <Box key={user.id} sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", p: 1 }}>
                            <Typography>{user.username}</Typography>
                            <Box>
                                <Button variant="contained" color="primary" onClick={() => handleAcceptRequest(user.username)}>
                                    Accept
                                </Button>
                                <Button variant="outlined" color="secondary" onClick={() => handleRejectRequest(user.username)} sx={{ ml: 1 }}>
                                    Reject
                                </Button>
                            </Box>
                        </Box>
                    ))
                )}

                {/* Followers/Following List */}
                <Typography variant="h6" sx={{ mt: 2 }}>{title}</Typography>
                {users.length === 0 ? (
                    <Typography>No {title.toLowerCase()} found.</Typography>
                ) : (
                    users.map((user) => (
                        <Box key={user.id} sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", p: 1 }}>
                            <Typography>{user.username}</Typography>
                            {user.email !== loggedInUserEmail && (
                                followingUsers[user.username] ? (
                                    <Button variant="outlined" onClick={() => onUnfollow(user.username)}>
                                        Unfollow
                                    </Button>
                                ) : (
                                    <Button variant="contained" onClick={() => onFollow(user.username)}>
                                        Follow
                                    </Button>
                                )
                            )}
                        </Box>
                    ))
                )}
            </DialogContent>
        </Dialog>
    );
};

export default FollowersFollowingDialog;
