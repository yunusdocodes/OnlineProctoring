import React, { useState, useEffect } from 'react';
import { FaUser , FaUpload, FaEdit, FaPen } from 'react-icons/fa';
import {
  
  Toolbar,
  Typography,
  Button,
  IconButton,
 
  Box,
  List,
  ListItem,
  ListItemText,
  Snackbar,
  Alert,
  Card,
  CardContent,
  Grid,
  TextField,
} from "@mui/material";
import AdminNavbar from './adminNavbar';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const [userData, setUserData] = useState(null);
  const [image, setImage] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const token = localStorage.getItem('user_token');
  const user_id = localStorage.getItem('user_id');
console.log(token)
console.log(user_id)
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
  const Media_Base_URL = process.env.REACT_APP_API_BASE_URL_Media;
  const USER_PROFILE_URL = `${API_BASE_URL}/users/${user_id}`;
  const UPLOAD_PROFILE_PICTURE_URL = `${API_BASE_URL}/users/upload_profile_picture/`;
  const CHANGE_PASSWORD_URL = `${API_BASE_URL}/users/change_password/`;
  const LOGOUT_URL = `${API_BASE_URL}/logout/`;

  useEffect(() => {
    const storedUserData = localStorage.getItem('user_data');
    if (storedUserData) {
      setUserData(JSON.parse(storedUserData));
      if (JSON.parse(storedUserData).profile_picture) {
        setImage(`${JSON.parse(storedUserData).profile_picture}`);
      }
    } else {
      fetchUserData();
    }
  }, [token]);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const response = await fetch(USER_PROFILE_URL, {
        headers: {
          'Authorization': `Token ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setUserData(data);
      if (data.profile_picture) {
        setImage(`${data.profile_picture}`);
      }
      localStorage.setItem('user_data', JSON.stringify(data));
    } catch (error) {
      console.error('Error fetching user data:', error);
      setErrorMessage('Failed to fetch user data. Please try again.');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('profile_picture', file);

      try {
        const response = await fetch(UPLOAD_PROFILE_PICTURE_URL, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
          },
          body: formData,
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setImage(`${data.profile_picture}`);
        setUserData((prevData) => ({ ...prevData, profile_picture: data.profile_picture }));
        localStorage.setItem('user_data', JSON.stringify({ ...userData, profile_picture: data.profile_picture }));
      } catch (error) {
        console.error('Error uploading profile picture:', error);
        setErrorMessage('Failed to upload profile picture. Please try again.');
        setSnackbarOpen(true);
      }
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData();
    formData.append("full_name", userData.full_name);
    formData.append("phone", userData.phone);
    formData.append("email", userData.email);
    formData.append("status", userData.status);
    formData.append("linkedin", userData.linkedin);

    try {
      const response = await fetch(`${USER_PROFILE_URL }${userData.id}/`, {
        method: "PUT",
        headers: {
          "Authorization": `Token ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setUserData(data);
      localStorage.setItem('user_data', JSON.stringify(data));
      setIsEditing(false);
    } catch (error) {
      console.error("Error updating profile:", error);
      setErrorMessage("Failed to update profile. Please try again.");
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword === confirmPassword) {
      setLoading(true);
      try {
        const response = await fetch(CHANGE_PASSWORD_URL, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ currentPassword, newPassword }),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setIsChangingPassword(false);
      } catch (error) {
        console.error('Error changing password:', error);
        setErrorMessage('Failed to change password. Please try again.');
        setSnackbarOpen(true);
      } finally {
        setLoading(false);
      }
    } else {
      setErrorMessage('New password and confirm password do not match.');
      setSnackbarOpen(true);
    }
  };

  const handleLogout = async () => {
    try {
      const response = await fetch(LOGOUT_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      localStorage.removeItem('user_token');
      localStorage.removeItem('user_data');
      navigate('/login');
    } catch (error) {
      console.error('Error logging out:', error);
      setErrorMessage('Failed to logout. Please try again.');
      setSnackbarOpen(true);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
  

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
    
     <AdminNavbar/>


      <Box
        sx={{
          flex: 1,
          p: 3,
          marginTop: "64px",
          display: "flex",
          alignItems: "stretch",
        }}
      >
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                borderRadius: 2,
                boxShadow: 3,
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <Typography
                variant="h5"
                sx={{ mb: 2, fontWeight: "bold", color: "#003366" }}
              >
                <center>Admin Profile</center>
              </Typography>
              <CardContent sx={{ textAlign: "center" }}>
  <Box sx={{ position: "relative", display: "inline-block" }}>
    {image ? (
      <img
        src={image}
        alt="Profile"
        style={{
          width: "120px",
          height: "120px",
          borderRadius: "50%",
          objectFit: "cover",
          border: "4px solid #003366",
        }}
      />
    ) : (
      <Box
        sx={{
          width: 120,
          height: 120,
          borderRadius: "50%",
          backgroundColor: "#abb6b8",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontSize: 40,
          fontWeight: "bold",
        }}
      >
        {(userData?.full_name?.[0] || "NA").toUpperCase()}
      </Box>
    )}

    {isEditing && (
      <label htmlFor="upload-image" style={{ cursor: "pointer" }}>
        <FaPen
          style={{
            position: "absolute",
            bottom: "5px",
            right: "5px",
            backgroundColor: "#abb6b8",
            color: "#000000",
            padding: "6px",
            borderRadius: "50%",
            fontSize: "25px",
          }}

        />
      </label>
    )}

    <input
      type="file"
      id="upload-image"
      accept="image/*"
      onChange={handleImageUpload}
      style={{ display: "none" }}
    />
  </Box>


              <Typography variant="h6" sx={{ mt: 2, fontWeight: "bold" }}>
  {userData ? `${userData.full_name}` : 'Guest User'}
</Typography>

                <Typography variant="body2" sx={{ color: "text.secondary" }}>
                  {userData ? userData.role : "N/A"}
                </Typography>
                {!isEditing && (
                  <Button
                    variant="contained"
                    startIcon={<FaEdit />}
                    onClick={() => setIsEditing(true)}
                    sx={{
                      mt: 2,
                      backgroundColor: "#003366",
                      "&:hover": { backgroundColor: "#002244" },
                    }}
                  >
                    Edit Profile
                  </Button>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Card sx={{ borderRadius: 2, boxShadow: 3, flexGrow: 1 }}>
                  <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
  Profile Information
</Typography>
<form onSubmit={handleProfileSubmit}>
  
  <Grid container spacing={2}>
    <Grid item xs={12} md={6}>
      <TextField
        fullWidth
        label="Full Name"
        value={userData ? userData.full_name : ""}
        onChange={(e) => setUserData({ ...userData, full_name: e.target.value })}
        required
      />
    </Grid>
    <Grid item xs={12} md={6}>
      <TextField
        fullWidth
        label="Phone"
        value={userData ? userData.phone : ""}
        onChange={(e) => setUserData({ ...userData, phone: e.target.value })}
        required
      />
    </Grid>
    <Grid item xs={12} md={6}>
      <TextField
        fullWidth
        label="Email"
        type="email"
        value={userData ? userData.email : ""}
        onChange={(e) => setUserData({ ...userData, email: e.target.value })}
        required
      />
    </Grid>
    <Grid item xs={12} md={6}>
      <TextField
        fullWidth
        label="Status"
        value={userData ? userData.status : ""}
        onChange={(e) => setUserData({ ...userData, status: e.target.value })}
        required
      />
    </Grid>
    <Grid item xs={12} md={6}>
      <TextField fullWidth
        label="Role"
        value={userData?.role || ""}
        InputProps={{ readOnly: true }}
      />
    </Grid>
    <Grid item xs={12} md={6}>
      <TextField
        fullWidth
        label="LinkedIn"
        value={userData ? userData.linkedin : ""}
        onChange={(e) => setUserData({ ...userData, linkedin: e.target.value })}
        required
      />
    </Grid>
    <Grid item xs={12}>
      <Button
        type="submit"
        variant="contained"
        sx={{
          backgroundColor: "#003366",
          "&:hover": { backgroundColor: "#002244" },
        }}
      >
        Save Profile
      </Button>
    </Grid>
  </Grid>
</form>

                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12}>
              <Card sx={{ borderRadius: 2, boxShadow: 3, flexGrow: 1, mt: 2 }}>

                  <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
  Security Settings
</Typography>
<form onSubmit={handleChangePassword}>
  <TextField
    fullWidth
    label="Current Password"
    type="password"
    required
    onChange={(e) => setCurrentPassword(e.target.value)}
    sx={{ mb: 2 }}
  />
  <TextField
    fullWidth
    label="New Password"
    type="password"
    required
    onChange={(e) => setNewPassword(e.target.value)}
    sx={{ mb: 2 }}
  />
  <TextField
    fullWidth
    label="Confirm New Password"
    type="password"
    required
    onChange={(e) => setConfirmPassword(e.target.value)}
    sx={{ mb: 2 }}
  />
  <Button type="submit" variant="contained">
    Submit
  </Button>
</form>

   
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Box>
     
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
      >
        <Alert onClose={() => setSnackbarOpen(false)} severity="error" sx={{ width: '100%' }}>
          {errorMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Profile;