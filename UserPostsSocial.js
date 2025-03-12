import React, { useState, useEffect } from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import Box from '@mui/material/Box';
import ButtonBase from '@mui/material/ButtonBase';
import Typography from '@mui/material/Typography';
import axiosInstance from '../../pages/authentication/axiosSetup';
import IconButton from '@mui/material/IconButton';
import { PlayCircleOutline, Favorite } from '@mui/icons-material';
import CircularProgress from '@mui/material/CircularProgress';
import ModalForSocial from './ModalForSocial';
import getAccessTokenFromLocalStorage from '../../pages/authentication/GetAccessToken';
import { useAuth } from '../../routes/AuthContext'; // Adjust path as necessary
import LoginModal from '../../pages/components-overview/LoginModal'; // Adjust the import path as necessary
import { useTheme } from '@mui/material/styles';
import { useMediaQuery } from '@mui/material';
import { Layers } from '@mui/icons-material';

const base_api_url = process.env.REACT_APP_BASE_API_URL;
const isProduction = process.env.REACT_APP_RUNNING_MODE === 'production';

const UserPostsSocial = ({ username, userInfo }) => {// Removed isDialogOpen as it's unused
  const [posts, setPosts] = useState([]);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false); // Keep isLoading if used for conditional rendering
  const [modalPostIndex, setModalPostIndex] = useState(null);
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [hoverIndex, setHoverIndex] = useState(-1); // New state to track hover
  const { isAuthenticated } = useAuth();
  const accessToken = getAccessTokenFromLocalStorage();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  // const imageSrc = (postItem) => isProduction && postItem.presigned_file_url
  //                  ? postItem.presigned_file_url
  //                  : `${base_api_url}/api/media/display-user-uploads/${postItem.thumbnail_path}`;

  
  const resolveMediaSource = (postItem) => {
    const fallbackImageUrl = '/assets/images/fallback-image.png'; // Define a fallback image URL
    //    console.log('isProduction', isProduction)
    //    console.log('POSTiTEM', postItem);
    if (!postItem) return fallbackImageUrl;

    if (isProduction && postItem.presigned_thumbnail_url) {
      return postItem.presigned_thumbnail_url;
    }
    // console.log('hi')
    // return `${base_api_url}/api/media/display-user-uploads/${postItem.file_path}`;
    return postItem.thumbnail_path ? `${base_api_url}/api/media/display-user-uploads/${postItem.thumbnail_path}` : fallbackImageUrl;
  };

  const fetchPosts = async () => {
    // if (isLoading || !hasMore) return;
    setIsLoading(true);
    try {
      const response = await axiosInstance.get(`/api/social/user/${username}/posts?page=${page}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(isAuthenticated && { Authorization: `Bearer ${accessToken}` })
        }
      });
      const fetchedPosts = response.data.posts;

      if (fetchedPosts.length > 0) {
        setPosts((prevPosts) => [...prevPosts, ...fetchedPosts.map((p) => ({ ...p, liked: p.likedByCurrentUser }))]);
        setPage((prevPage) => prevPage + 1);
        setHasMore(fetchedPosts.length === 10); // Assuming 10 posts per page
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!isLoading && hasMore) {
      fetchPosts();
    }
    // The empty dependency array ensures this effect runs once after the first render
    // Removing 'isLoading' and 'hasMore' to prevent re-triggering fetch when those values change
  }, [username, page]); // Only re-run the effect if username changes

  const handleOpenModal = (index) => {
    if (isAuthenticated) {
      setModalPostIndex(index);
      console.log("Clicked post index:", index, "Post data:", posts[index]);
    } else {
      setLoginModalOpen(true);
      console.log("Login required, opening login modal");
    }
  };
  

  const handleCloseModal = () => {
    setModalPostIndex(null);
  };

  const handleNextPrevModal = (direction) => {
    setModalPostIndex((prevIndex) => {
      const newIndex = direction === 'next' ? prevIndex + 1 : prevIndex - 1;
      return (newIndex + posts.length) % posts.length;
    });
  };

  // Assuming the rest of the UserPostsSocial component remains unchanged

  const handleLikeToggle = async (postId, liked) => {
    try {
      const response = await axiosInstance.post(
        `${base_api_url}/api/media/like-toggle/${postId}`,
        { liked },
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`
          }
        }
      );
      console.log(response);
      const index = posts.findIndex((item) => item.id === postId);

      if (index !== -1) {
        const updatedItem = {
          ...posts[index],
          liked: response.data.liked,
          likesCount: response.data.likesCount
        };
        const updatedCurrentPosts = [...posts.slice(0, index), updatedItem, ...posts.slice(index + 1)];
        setPosts(updatedCurrentPosts);
      }
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  };

  const renderPosts = () => {
    return (
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: isMobile ? 'repeat(3, 1fr)' : 'repeat(3, 1fr)',
          gap: isMobile ? theme.spacing(1) : theme.spacing(2)
        }}
      >
        {/* {posts.filter(post => post.thumbnail_path && post.thumbnail_path !== 'null').map((post, index) => ( */}
        {posts.map((post, index) => (
          <Box
            key={post.id}
            onMouseEnter={() => setHoverIndex(index)}
            onMouseLeave={() => setHoverIndex(-1)}
            sx={{
              position: 'relative',
              marginBottom: 1,
              '&:hover': {
                opacity: isMobile ? 1 : 0.8
              }
            }}
          >
            {post.media.length > 1 && (
              <IconButton
                sx={{
                  position: 'absolute',
                  right: 8,
                  top: 8,
                  color: 'white',
                  backgroundColor: 'rgba(0, 0, 0, 0.7)',
                  zIndex: 2, // Ensure it's above other elements
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)'
                  },
                  boxShadow: '0 2px 4px rgba(0,0,0,0.5)', // Adding shadow for pop effect
                  padding: '6px' // Adjust padding
                }}
              >
                <Layers sx={{ fontSize: '1.5rem' }} />
              </IconButton>
            )}
            <ButtonBase
              onClick={() => handleOpenModal(index)}
              sx={{
                display: 'block',
                width: '100%',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <Box sx={{ width: '100%', height: 0, paddingBottom: '100%', overflow: 'hidden', position: 'relative' }}>
                {hoverIndex === index && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      backgroundColor: 'rgba(0, 0, 0, 0.5)',
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      gap: 1,
                      zIndex: 1
                    }}
                  >
                    <Favorite sx={{ color: 'error.main', fontSize: 28 }} />
                    <Typography color="common.white" fontSize="16px">
                      {post.likesCount}
                    </Typography>

                    {post.is_video && (
                      <>
                        <PlayCircleOutline sx={{ color: 'yellow', fontSize: 32 }} />
                        {/* <Typography color="common.white" fontSize="16px">{post.likesCount}</Typography> */}
                        {/* <IconButton
                                                sx={{
                                                    position: 'relative',
                                                    top: 0,
                                                    right: 0,
                                                    color: 'yellow',
                                                    padding: '4px',
                                                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                                                }}
                                                >
                                                <PlayCircleOutline />
                                            </IconButton> */}
                      </>
                    )}
                  </Box>
                )}

                <img
                  // src={`${base_api_url}/api/media/display-user-uploads/${post.thumbnail_path}`}
                  src={resolveMediaSource(post.media[0])}
                  alt="Post"
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </Box>
            </ButtonBase>
            <Typography variant="subtitle1" align="center" sx={{ mt: 1 }}>
              {post.lessonTitle}
            </Typography>
          </Box>
        ))}
      </Box>
    );
  };

  return (
    <>
      <InfiniteScroll
        dataLength={posts.length}
        next={() => setPage((prevPage) => prevPage + 1)}
        hasMore={hasMore}
        loader={isLoading && <CircularProgress />}
        endMessage={<Typography textAlign="center">You have seen it all</Typography>}
      >
        {renderPosts()}
      </InfiniteScroll>

      {modalPostIndex !== null && (
        <ModalForSocial
          open={modalPostIndex !== null}
          posts={posts}
          currentIndex={modalPostIndex}
          onClose={handleCloseModal}
          handleNext={handleNextPrevModal.bind(null, 'next')}
          handlePrev={handleNextPrevModal.bind(null, 'prev')}
          handleLikeToggle={handleLikeToggle}
          userInfo={userInfo}
        />
      )}

      <LoginModal open={loginModalOpen} handleClose={() => setLoginModalOpen(false)} />
    </>
  );
};

export default UserPostsSocial;
