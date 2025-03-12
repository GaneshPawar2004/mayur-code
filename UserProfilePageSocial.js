// UserProfilePage.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import UserInfoSocial from './UserInfoSocial';
import UserPostsSocial from './UserPostsSocial';
import axiosInstance from '../../pages/authentication/axiosSetup';
import getAccessTokenFromLocalStorage from '../../pages/authentication/GetAccessToken';
import { useAuth } from 'routes/AuthContext';
import { Typography, Box, Container } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useMediaQuery } from '@mui/material';

const UserProfilePageSocial = () => {
  const { username } = useParams();
  const [userInfo, setUserInfo] = useState(false);
  const [userNotFound, setUserNotFound] = useState(false);
  const access_token = getAccessTokenFromLocalStorage();
  const [dialogOpen, setDialogOpen] = useState(false);
  const { email } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const headers = {
    'Content-Type': 'application/json',
    ...(access_token ? { Authorization: `Bearer ${access_token}` } : {})
  };

  useEffect(() => {
    if (!username) {
      setUserNotFound(true);
      navigate('/social/not-found');
    }

    axiosInstance
      .get(`/api/social/user/${username}`, { headers })
      .then((response) => {
        setUserInfo(response.data);
        setUserNotFound(false);
      })
      .catch((error) => {
        if (error.response && error.response.status === 404) {
          console.log('error on 40', error.response.data);
          setUserNotFound(true);
        } else {
          console.error('Error fetching user info:', error);
        }
      });
  }, [username, access_token]);

  if (userNotFound) {
    return (
      <Container>
        <Box sx={{ textAlign: 'center', marginTop: 8 }}>
          <Typography variant="h5" gutterBottom>
            Sorry, this page isn&#39;t available.
          </Typography>
          <Typography variant="body1">The link you followed may be broken, or the page may have been removed.</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container sx={{ px: isMobile ? 2 : 16 }}>
      {/* <a href="/social-public" target='_blank' rel='noopener noreferrer'>
                Check Public Feed
            </a> */}
      {/* <br /> */}
      {userInfo ? (
        <>
          <UserInfoSocial
            userInfo={userInfo}
            setUserInfo={setUserInfo}
            loggedInUserEmail={email}
            dialogOpen={dialogOpen}
            setDialogOpen={setDialogOpen}
          />
          <br />
          <UserPostsSocial userInfo={userInfo} username={username} isDialogOpen={dialogOpen} />
        </>
      ) : (
        <Typography variant="h6" align="center">
          Loading...
        </Typography>
      )}
    </Container>
  );
};

export default UserProfilePageSocial;
