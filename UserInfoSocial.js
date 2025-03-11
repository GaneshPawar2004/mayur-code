import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Stack,
  Button,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
  Avatar,
  Grid,
  Chip,
  Modal,
  IconButton,
  Tooltip
} from '@mui/material';
import { Edit as EditIcon, CameraAlt as CameraIcon, CalendarToday as CalendarIcon, VerifiedUser } from '@mui/icons-material';
import axiosInstance from '../../pages/authentication/axiosSetup';
import getAccessTokenFromLocalStorage from '../../pages/authentication/GetAccessToken';
import defaultAvatar from '../../assets/images/users/default-avatar.jpg';
import { toast } from 'react-toastify';
import ChangeUsernameForm from '../authentication/ChangeUsername';
import { useNavigate,useParams } from 'react-router-dom';
import { format } from 'date-fns';
import { useAuth } from 'routes/AuthContext';
import LinkIcon from '@mui/icons-material/Link';

const base_api_url = process.env.REACT_APP_BASE_API_URL;
const isProduction = process.env.REACT_APP_RUNNING_MODE === 'production';

const UserInfoSocial = ({ userInfo, loggedInUserEmail, setUserInfo, dialogOpen, setDialogOpen }) => {
  const [editInfo, setEditInfo] = useState({
    fullname: userInfo.fullname,
    bio: userInfo.bio
  });
  const [openChangeUsernameModal, setOpenChangeUsernameModal] = useState(false);
  const fileInputRef = useRef();
  const navigate = useNavigate();
  const access_token = getAccessTokenFromLocalStorage();
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const { isAuthenticated, current_plan_name, updateAvatarUrls } = useAuth();

  //change
  const { username } = useParams();
  const [followers,setFollowers]=useState([]);
  const [following,setFollowing]=useState([]);

  useEffect(() => {
    // Fetch both followers and following
    const fetchFollowers = axiosInstance.get(`/api/social/user/${username}/followers`);
    const fetchFollowing = axiosInstance.get(`/api/social/user/${username}/following`);
  
    Promise.all([fetchFollowers, fetchFollowing])
      .then(([followersRes, followingRes]) => {
        setFollowers(Array.isArray(followersRes.data.followers) ? followersRes.data.followers : []);
        setFollowing(Array.isArray(followingRes.data.following) ? followingRes.data.following : []);
  
        console.log("Followers:", followersRes.data.followers.length);
        console.log("Following:", followingRes.data.following.length);
      })
      .catch((error) => {
        console.error("Error fetching social data:", error);
      });
  }, [username]);
  

  const handleOpenChangeUsernameModal = () => setOpenChangeUsernameModal(true);
  const handleCloseChangeUsernameModal = () => setOpenChangeUsernameModal(false);

  const handleChange = (e) => setEditInfo({ ...editInfo, [e.target.name]: e.target.value });

  const handleSave = () => {
    axiosInstance
      .put(`/api/social/user/${userInfo.username}`, editInfo, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${access_token}`
        }
      })
      .then(() => {
        setUserInfo((prev) => ({ ...prev, ...editInfo }));
        setDialogOpen(false);
        toast.success('Profile updated successfully');
      })
      .catch((error) => {
        console.error('Error updating user info:', error);
        toast.error('Failed to update profile');
      });
  };

  const handleAvatarClick = () => {
    if (loggedInUserEmail === userInfo.email) {
      fileInputRef.current.click();
    }
  };

  const handleAvatarChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Please upload a valid image file (jpg or png).');
        return;
      }
      if (file.size > MAX_FILE_SIZE) {
        toast.error('File size should not exceed 10MB.');
        return;
      }

      const formData = new FormData();
      formData.append('avatar', file);

      axiosInstance
        .put(`/api/social/user/${userInfo.username}/avatar`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${access_token}`
          }
        })
        .then((response) => {
          const { avatar_url, avatar_thumbnail_url } = response.data;
          setUserInfo((prev) => ({ ...prev, avatar_url, avatar_thumbnail_url }));
          updateAvatarUrls(avatar_url, avatar_thumbnail_url); // Update the auth context
          toast.success('Avatar updated successfully.');

          // setUserInfo(prev => ({ ...prev, avatarUrl: response.data.avatarUrl, avatarThumbnailUrl: response.data.avatarThumbnailUrl }));
          // toast.success('Avatar updated successfully.');
        })
        .catch((error) => {
          console.error('Error updating avatar:', error);
          toast.error('Failed to update avatar');
        });
    }
  };

  const handleUsernameChangeSuccess = (newUsername) => {
    handleCloseChangeUsernameModal();
    navigate(`/social/${newUsername}`);
  };

  const resolveAvatarSource = (avatar) => {
    // const fallbackImageUrl = base_api_url+'/assets/images/fallback-image.png';
    if (!avatar) return defaultAvatar;
    else if (isProduction && avatar) {
      return avatar;
    } else if (!isProduction && avatar) {
      return `${base_api_url}/api/media/display-user-uploads/${avatar}`;
    } else {
      return defaultAvatar;
    }
  };

  return (
    <Box sx={{ py: 4 }}>
      <Grid container spacing={4} alignItems="center">
        <Grid item xs={12} sm={4} md={3} sx={{ textAlign: 'center' }}>
          <Box sx={{ position: 'relative', display: 'inline-block' }}>
            <Avatar
              src={resolveAvatarSource(userInfo.avatarThumbnailUrl)}
              alt={userInfo.username}
              sx={{ width: 150, height: 150, cursor: loggedInUserEmail === userInfo.email ? 'pointer' : 'default' }}
              onClick={handleAvatarClick}
            />
            {loggedInUserEmail === userInfo.email && (
              <IconButton
                sx={{
                  position: 'absolute',
                  bottom: 0,
                  right: 0,
                  backgroundColor: 'rgba(0, 0, 0, 0.6)',
                  '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.8)' }
                }}
                onClick={handleAvatarClick}
              >
                <CameraIcon sx={{ color: 'white' }} />
              </IconButton>
            )}
          </Box>
          <input ref={fileInputRef} type="file" hidden onChange={handleAvatarChange} />
        </Grid>
        <Grid item xs={12} sm={8} md={9}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1" sx={{ mr: 0.5 }}>
              {userInfo.username}
            </Typography>
            {isAuthenticated && current_plan_name != 'beginner' && <VerifiedUser sx={{ fontSize: 16, color: '#1DA1F2' }} />}

            {
              loggedInUserEmail === userInfo.email ?? (
                <>
                  <Button variant="outlined" onClick={() => setDialogOpen(true)} startIcon={<EditIcon />} sx={{ ml: 2, mr: 1 }}>
                    Edit Profile
                  </Button>
                  <Button variant="outlined" onClick={handleOpenChangeUsernameModal}>
                    Edit Username
                  </Button>
                </>
              )
              // : (
              //     <Button variant="contained" color="primary" sx={{ ml: 2, mr: 1 }}>Follow</Button>
              // )
            }
          </Box>
          <Stack direction="row" spacing={4} sx={{ mb: 2 }}>
            <Typography>
              <strong>{userInfo.postsCount}</strong> posts
            </Typography>
            <Typography> {followers.length} followers</Typography>
            <Typography>{following.length} following</Typography>
          </Stack>
          <Typography variant="h6" gutterBottom>
            {userInfo.fullname}
          </Typography>
          <Typography variant="body1" sx={{ mb: 1, whiteSpace: 'pre-wrap' }}>
            {userInfo.bio}
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            <Tooltip title="Joined date">
              <Chip
                icon={<CalendarIcon />}
                label={`Joined ${format(new Date(userInfo.created_at), 'MMMM yyyy')}`}
                // label={`Joined ${userInfo.created_at}`}
                variant="outlined"
                size="small"
              />
            </Tooltip>
            {/* {userInfo.website && (
                            <Tooltip title="Website">
                                <Chip 
                                    icon={<LinkIcon />} 
                                    label={userInfo.website}
                                    variant="outlined"
                                    size="small"
                                    component="a"
                                    href={userInfo.website}
                                    target="_blank"
                                    clickable
                                />
                            </Tooltip>
                        )} */}
            <Tooltip title="Participate in College Development Program and get full access for free">
              <Chip
                icon={<LinkIcon />}
                label="Get Verified"
                variant=""
                sx={{ color: 'primary' }}
                color="primary"
                size="small"
                component="a"
                href="/cdp"
                target="_blank"
                clickable
              />
            </Tooltip>
          </Stack>
        </Grid>
      </Grid>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="fullname"
            label="Full Name"
            type="text"
            fullWidth
            value={editInfo.fullname || ''}
            onChange={handleChange}
            inputProps={{ maxLength: 30 }}
            helperText={`${editInfo.fullname?.length || 0}/30`}
          />
          <TextField
            margin="dense"
            name="bio"
            label="Bio"
            type="text"
            fullWidth
            multiline
            rows={4}
            value={editInfo.bio || ''}
            onChange={handleChange}
            inputProps={{ maxLength: 255 }}
            helperText={`${editInfo.bio?.length || 0}/255`}
          />
          {/* <TextField
                        margin="dense"
                        name="website"
                        label="Website"
                        type="url"
                        fullWidth
                        value={editInfo.website || ''}
                        onChange={handleChange}
                    /> */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSave}>Save</Button>
        </DialogActions>
      </Dialog>

      <Modal open={openChangeUsernameModal} onClose={handleCloseChangeUsernameModal} aria-labelledby="change-username-modal-title">
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 400,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2
          }}
        >
          <ChangeUsernameForm onSuccess={handleUsernameChangeSuccess} />
        </Box>
      </Modal>
    </Box>
  );
};

export default UserInfoSocial;
