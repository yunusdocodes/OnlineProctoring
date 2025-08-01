import React, { useEffect, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  CircularProgress,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import PlayCircleFilledIcon from "@mui/icons-material/PlayCircleFilled";

const VideoModal = ({ videoUrl, name, testId }) => {
  const [open, setOpen] = useState(false);
  const [finalUrl, setFinalUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setFinalUrl(null); // Cleanup URL
  };

  useEffect(() => {
    if (open) {
      const fetchVideo = async () => {
        setLoading(true);
        const token = localStorage.getItem("user_token");

        try {
          const response = await fetch(videoUrl, {
            headers: {
              Authorization: `Token ${token}`,
            },
          });

          if (!response.ok) throw new Error("Failed to fetch video");

          const blob = await response.blob();
          const videoBlobUrl = URL.createObjectURL(blob);
          setFinalUrl(videoBlobUrl);
        } catch (err) {
          console.error("Video fetch error:", err);
        } finally {
          setLoading(false);
        }
      };

      fetchVideo();
    }
  }, [open, videoUrl]);

  return (
    <>
      <IconButton onClick={handleOpen} title="View Recording">
        <PlayCircleFilledIcon />
      </IconButton>

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          Recording - {name}
          <IconButton
            onClick={handleClose}
            sx={{ position: "absolute", right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent>
          {loading ? (
            <CircularProgress />
          ) : finalUrl ? (
            <video width="100%" height="auto" controls>
              <source src={finalUrl} type="video/webm" />
              Your browser does not support the video tag.
            </video>
          ) : (
            <p>No video available</p>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default VideoModal;
