import React, { useState, useEffect, useRef } from 'react';
import { Modal, Box, Typography, IconButton, useMediaQuery, useTheme, Avatar, Divider } from '@mui/material';
import {ArrowBackIosNew,ArrowForwardIos,Favorite,FavoriteBorder,VerifiedUser,VolumeOff,VolumeUp,PlayArrow,Pause} from '@mui/icons-material';
// eslint-disable-next-line no-unused-vars
import Wavesurfer from 'wavesurfer.js';
import { useAuth } from 'routes/AuthContext';
import formatDateToLocalTimezone from '../../utils/TimeConversionToLocal';

const isProduction = process.env.REACT_APP_RUNNING_MODE === 'production';

const ModalForSocial = ({open,onClose,posts,currentIndex,handleNext,handlePrev,handleLikeToggle,userInfo,isSoundOn}) => {//ganesh
  const base_api_url = process.env.REACT_APP_BASE_API_URL;
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { isAuthenticated, current_plan_name } = useAuth();

  const audioRef = useRef(null);
  const wavesurferRef = useRef(null);
  const videoRef = useRef(null);

  const [currentMediaIndex, setCurrentMediaIndex] = useState(0);
  const [isAudioReady, setIsAudioReady] = useState(false);
  const [localIsSoundOn, setLocalIsSoundOn] = useState(isSoundOn);
  const [isPlaying, setIsPlaying] = useState(true);//ganesh
  
  const post = posts && posts[currentIndex] ? posts[currentIndex] : null;
  const mediaItems = post && post.media ? post.media : [];
  const currentMedia = mediaItems[currentMediaIndex];

  const resolveMediaSource = (mediaItem) => {
    const fallbackImageUrl = '/assets/images/fallback-image.png';
    if (!mediaItem || !mediaItem.file_path) return fallbackImageUrl;

    if (isProduction && mediaItem.presigned_file_url) {
      return mediaItem.presigned_file_url;
    }
    return `${base_api_url}/api/media/display-user-uploads/${mediaItem.file_path}`;
  };

  // Ensure audio is stopped and resources are cleaned when moving between posts
  const cleanupWavesurfer = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.destroy();
      wavesurferRef.current = null;
    }
    setIsAudioReady(false);
    setIsPlaying(false);
  };

  // Reinitialize the wavesurfer and clean up correctly on media change
  useEffect(() => {
    setCurrentMediaIndex(0);
    cleanupWavesurfer();
  }, [currentIndex]);

  //ganesh
  useEffect(() => {
    if (currentMedia && currentMedia.file_path.endsWith('.mp4') && videoRef.current) {
      const videoElement = videoRef.current;
      
      // Try playing the video after a short delay
      setTimeout(() => {
        console.log('videoRef.current:', videoRef.current);

        videoElement
          .play()
          .catch((error) => console.log('Auto-play blocked or failed:', error));
      }, 100); // Delay ensures the video element is mounted before play is called
    }
  }, [currentMedia]);
  

  //ganesh 
  const handleTogglePlay = () => {
    if (currentMedia && currentMedia.file_path.endsWith('.mp4') && videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    } else if (wavesurferRef.current) {  // Handle audio case
      if (isPlaying) {
        wavesurferRef.current.pause();
      } else {
        wavesurferRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };
  

  const handleToggleSound = (e) => {
    e.stopPropagation();
    setLocalIsSoundOn((prev) => !prev);
  };

  useEffect(() => {
    if (wavesurferRef.current) {
      wavesurferRef.current.setMuted(!localIsSoundOn);
    }
    if (videoRef.current) {
      videoRef.current.muted = !localIsSoundOn;
    }
  }, [localIsSoundOn]);

  const navigateMedia = (direction) => {
    setCurrentMediaIndex((prevIndex) => {
      const newIndex = direction === 'next' ? prevIndex + 1 : prevIndex - 1;
      return (newIndex + mediaItems.length) % mediaItems.length;
    });
  };

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'ArrowRight') {
        handleNext();
      } else if (event.key === 'ArrowLeft') {
        handlePrev();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleNext, handlePrev]);

  // Early return after hooks
  if (!post) {
    return null; // Return null if post doesn't exist
  }

  const modalStyle = {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: isMobile ? '90%' : '80%',
    height: isMobile ? '90%' : '80%',
    display: 'flex',
    flexDirection: isMobile ? 'column' : 'row',
    overflowY: 'auto',
    bgcolor: 'background.paper',
    boxShadow: theme.shadows[5],
    borderRadius: theme.shape.borderRadius,
    outline: 'none'
  };

  const mediaStyle = {
    height: '100%',
    width: isMobile ? '100%' : '60%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    objectFit: 'contain',
    backgroundColor: 'black',
    position: 'relative'
  };

  const infoStyle = {
    width: isMobile ? '100%' : '40%',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'flex-start',
    p: theme.spacing(2),
    bgcolor: 'background.paper'
  };

  const arrowButtonStyleForPost = {
    position: 'absolute',
    top: '50%',
    transform: 'translateY(-50%)',
    color: 'white',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    '&:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.7)'
    },
    borderRadius: '50%',
    padding: theme.spacing(1),
    zIndex: 10
  };

  const arrowButtonStyleForMedia = {
    position: 'absolute',
    top: isMobile ? '90%' : '90%',
    transform: 'translateY(-50%)',
    color: 'white',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    '&:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.7)'
    },
    borderRadius: '50%',
    zIndex: 10
  };

  const handleUserClick = () => {
    window.open(`/social/${post.username}`, '_blank');
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Box sx={modalStyle}>
        <Box sx={mediaStyle}>
          {mediaItems.length > 1 && (
            <>
              <IconButton onClick={() => navigateMedia('prev')} sx={{ ...arrowButtonStyleForMedia, left: isMobile ? '20%' : '10%' }}>
                <ArrowBackIosNew />
              </IconButton>
              <IconButton onClick={() => navigateMedia('next')} sx={{ ...arrowButtonStyleForMedia, right: isMobile ? '20%' : '10%' }}>
                <ArrowForwardIos />
              </IconButton>
            </>
          )}
          {currentMedia && currentMedia.file_path.endsWith('.mp4') ? (
            <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
              <video
                ref={videoRef}
                loop
                muted={!localIsSoundOn}
                playsInline
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              >
                <source src={resolveMediaSource(currentMedia)} type="video/mp4" />
                <track kind="captions" />
              </video>
              <IconButton
                onClick={handleTogglePlay}
                sx={{
                  position: 'absolute',
                  bottom: 16,
                  left: 16,
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  color: 'white',
                  '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.7)' }
                }}
              >
                {isPlaying ? <Pause /> : <PlayArrow />}
              </IconButton>
              <IconButton
                onClick={handleToggleSound}
                sx={{
                  position: 'absolute',
                  bottom: 16,
                  right: 16,
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  color: 'white',
                  '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.7)' }
                }}
              >
                {localIsSoundOn ? <VolumeUp /> : <VolumeOff />}
              </IconButton>
            </Box>
          ) : currentMedia && (currentMedia.file_path.endsWith('.mp3') || currentMedia.file_path.endsWith('.wav')) ? (
            <Box
              sx={{
                position: 'relative',
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#f0f0f0'
              }}
            >
              <div ref={audioRef} style={{ width: '100%', height: '80px' }} />
              {isAudioReady && (
                <>
                  <IconButton
                    onClick={handleTogglePlay}
                    sx={{
                      position: 'absolute',
                      bottom: 16,
                      left: 16,
                      backgroundColor: 'rgba(0, 0, 0, 0.5)',
                      color: 'white',
                      '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.7)' }
                    }}
                  >
                    {isPlaying ? <Pause /> : <PlayArrow />}
                  </IconButton>
                  <IconButton
                    onClick={handleToggleSound}
                    sx={{
                      position: 'absolute',
                      bottom: 16,
                      right: 16,
                      backgroundColor: 'rgba(0, 0, 0, 0.5)',
                      color: 'white',
                      '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.7)' }
                    }}
                  >
                    {localIsSoundOn ? <VolumeUp /> : <VolumeOff />}
                  </IconButton>
                </>
              )}
            </Box>
          ) : (
            <img src={resolveMediaSource(currentMedia)} alt="Media" style={{ maxWidth: '100%', maxHeight: '75vh' }} />
          )}
          <Box sx={{ position: 'absolute', bottom: 20, display: 'flex', justifyContent: 'center', width: '100%' }}>
            {mediaItems.map((_, index) => (
              <Box
                key={index}
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: currentMediaIndex === index ? 'primary.main' : 'grey.400',
                  margin: '0 4px'
                }}
              />
            ))}
          </Box>
        </Box>

        <Box sx={infoStyle}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }} onClick={handleUserClick}>
              <Avatar
                src={`${base_api_url}/api/media/display-user-uploads/${userInfo?.avatarThumbnailUrl}`}
                sx={{ width: 48, height: 48 }}
              />
              <Typography variant="subtitle1" sx={{ ml: 2, cursor: 'pointer', mr: 0.5 }}>
                {post.username}
              </Typography>
              {isAuthenticated && current_plan_name !== 'beginner' && <VerifiedUser sx={{ fontSize: 16, color: '#1DA1F2' }} />}
            </Box>
            <Typography variant="body1" sx={{ cursor: 'default' }}>
              {post.lessonTitle}
            </Typography>
          </Box>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body1" sx={{ my: 2 }}>
            {post.caption}
          </Typography>
          <Box sx={{ mt: 'auto', py: 1 }}>
            <IconButton onClick={() => handleLikeToggle(post?.id, !post?.liked)}>
              {post?.liked ? <Favorite sx={{ color: 'error.main' }} /> : <FavoriteBorder />}
            </IconButton>
            <Typography variant="body2">{post.likesCount} likes</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {formatDateToLocalTimezone(post.created_at)}
            </Typography>
          </Box>
        </Box>

        <IconButton onClick={handlePrev} sx={{ ...arrowButtonStyleForPost, left: theme.spacing(2) }}>
          <ArrowBackIosNew />
        </IconButton>
        <IconButton onClick={handleNext} sx={{ ...arrowButtonStyleForPost, right: theme.spacing(2) }}>
          <ArrowForwardIos />
        </IconButton>
      </Box>
    </Modal>
  );
};

export default ModalForSocial;
