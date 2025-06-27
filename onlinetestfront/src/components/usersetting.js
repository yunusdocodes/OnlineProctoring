import React, { useState, useEffect } from "react";
import {
  Container,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControl,
  Select,
  MenuItem,
  Button,
  FormControlLabel,
  Box,
  Snackbar,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import {
  Brightness4,
  Brightness7,
  Public,
  Settings,
  AccessTime,
  Save,
  Notifications,
  Menu as MenuIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import logo from "../assets/Image20250320122406.png";
import TwitterIcon from '@mui/icons-material/Twitter'; // Import Twitter icon
import FacebookIcon from '@mui/icons-material/Facebook'; // Import Facebook icon
import InstagramIcon from '@mui/icons-material/Instagram'; // Import Instagram icon
import axios from 'axios'; // Import axios for API calls
import UserNavbar from "./userNavbar";
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const SettingsCustomizationPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [testAccess, setTestAccess] = useState("public");
  const [integration, setIntegration] = useState("none");
  const [autoSave, setAutoSave] = useState(true);
  const [timeReminder, setTimeReminder] = useState(5);
  const [notifications, setNotifications] = useState(true);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // State for sidebar
  const navigate = useNavigate(); // Initialize navigate

  useEffect(() => {
    document.body.style.backgroundColor = darkMode ? "#121212" : "#f8f9fa";
  }, [darkMode]);

  useEffect(() => {
    const fetchSettings = async () => {
      const token = localStorage.getItem('user_token'); // Get the token from local storage
      const headers = { Authorization: `Token ${token}` };

      try {
        const response = await axios.get(`${API_BASE_URL}/user-settings/`, { headers });
        const settings = response.data;
        setDarkMode(settings.dark_mode);
        setTestAccess(settings.test_access);
        setIntegration(settings.integration);
        setAutoSave(settings.auto_save);
        setTimeReminder(settings.time_reminder);
        setNotifications(settings.notifications);
      } catch (error) {
        console.error("Error fetching settings:", error);
      }
    };

    fetchSettings();
  }, []);

  const handleReset = async () => {
    const token = localStorage.getItem('user_token'); // Get the token from local storage
    const headers = { Authorization: `Token ${token}` };

    try {
      await axios.post(`${API_BASE_URL}/user-settings/reset/`, {}, { headers });
      // Reset local state to default values
      setDarkMode(false);
      setTestAccess("public");
      setIntegration("none");
      setAutoSave(true);
      setTimeReminder(5);
      setNotifications(true);
      setSnackbarMessage("Settings reset to default.");
      setSnackbarOpen(true);
    } catch (error) {
      console.error("Error resetting settings:", error);
      setSnackbarMessage("Failed to reset settings.");
      setSnackbarOpen(true);
    }
  };

  const handleSave = async () => {
    const token = localStorage.getItem('user_token'); // Get the token from local storage
    const headers = { Authorization: `Token ${token}` };

    try {
      await axios.put(`${API_BASE_URL}/user-settings/`, {
        dark_mode: darkMode,
        test_access: testAccess,
        integration: integration,
        auto_save: autoSave,
        time_reminder: timeReminder,
        notifications: notifications,
      }, { headers });

      setSnackbarMessage("Settings saved successfully!");
      setSnackbarOpen(true);
    } catch (error) {
      console.error("Error saving settings:", error.response.data); // Log the error response
      setSnackbarMessage("Failed to save settings.");
      setSnackbarOpen(true);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <>
    <UserNavbar/>
    <Box sx={{ display: "flex" }}>
     
     
     <Container
              maxWidth="sm"
              sx={{
                position: "fixed", // Set position to fixed
                top: "64px", // Set top to the height of the AppBar
                bottom: "0", // Adjust for footer height
                left: 0,
                right: 0,
                display: "flex",
                justifyContent: "center",
                alignItems: "flex-start", // Align items to the start
                overflowY: "auto", // Enable vertical scrolling
                padding: "16px", // Add padding as needed
                "&::-webkit-scrollbar": { // Hide scrollbar for Chrome, Safari, and Opera
                  display: "none",
                },
                scrollbarWidth: "none", // Hide scrollbar for Firefox
                msOverflowStyle: "none", // Hide scrollbar for IE and Edge
              }}
            >

        <Card
          sx={{
            width: "90%", // Reduced width
            p: 2, // Reduced padding
            borderRadius: 3,
            boxShadow: 4,
            backgroundColor: darkMode ? "#1e1e1e" : "#ffffff",
            color: darkMode ? "#f1f1f1" : "#212529",
          }}
        >
          <CardContent>
            <Typography
              variant="h4"
              align="center"
              gutterBottom
              sx={{ color: darkMode ? "#ffffff" : "#212529", fontWeight: "bold", fontSize: '1.5rem' }} // Reduced font size for title
            >
              <Settings /> User Settings
            </Typography>

            {/* Theme Settings */}
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                my: 2,
              }}
            >
              <Box sx={{ display: "flex",
                alignItems: "center",
              }}>
                {darkMode ? <Brightness4 /> : <Brightness7 />}
                <Typography variant="h6" sx={{ ml: 1, color: darkMode ? "#e0e0e0" : "#212529", fontSize: '1rem' }}>
                  Theme Mode
                </Typography>
              </Box>
              <FormControlLabel
                control={<Switch checked={darkMode} onChange={() => setDarkMode(!darkMode)} />}
                label={darkMode ? "Dark Mode" : "Light Mode"}
                sx={{ color: darkMode ? "#e0e0e0" : "#212529" }}
              />
            </Box>

            {/* Test Access Settings */}
            <Box sx={{ my: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Public />
                <Typography variant="h6" sx={{ ml: 1, color: darkMode ? "#e0e0e0" : "#212529", fontSize: '1rem' }}>
                  Test Access
                </Typography>
              </Box>
              <FormControl fullWidth sx={{ mt: 1 }}>
                <Select
                  value={testAccess}
                  onChange={(e) => setTestAccess(e.target.value)}
                  sx={{
                    color: darkMode ? "#e0e0e0" : "#212529",
                    backgroundColor: darkMode ? "#2e2e2e" : "#ffffff",
                  }}
                >
                  <MenuItem value="public">Public</MenuItem>
                  <MenuItem value="private">Private</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Integration Options */}
            <Box sx={{ my: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Settings />
                <Typography variant="h6" sx={{ ml: 1, color: darkMode ? "#e0e0e0" : "#212529", fontSize: '1rem' }}>
                  Integration
                </Typography>
              </Box>
              <FormControl fullWidth sx={{ mt: 1 }}>
                <Select
                  value={integration}
                  onChange={(e) => setIntegration(e.target.value)}
                  sx={{
                    color: darkMode ? "#e0e0e0" : "#212529",
                    backgroundColor: darkMode ? "#2e2e2e" : "#ffffff",
                  }}
                >
                  <MenuItem value="none">None</MenuItem>
                  <MenuItem value="google">Google Forms</MenuItem>
                  <MenuItem value="lms">LMS Platform</MenuItem>
                  <MenuItem value="custom">Custom API</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Time Limit Reminder */}
            <Box sx={{ my: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <AccessTime />
                <Typography variant="h6" sx={{ ml: 1, color: darkMode ? "#e0e0e0" : "#212529", fontSize: '1rem' }}>
                  Time Reminder
                </Typography>
              </Box>
              <FormControl fullWidth sx={{ mt: 1 }}>
                <Select
                  value={timeReminder}
                  onChange={(e) => setTimeReminder(e.target.value)}
                  sx={{
                    color: darkMode ? "#e0e0e0" : "#212529",
                    backgroundColor: darkMode ? "#2e2e2e" : "#ffffff",
                  }}
                >
                  <MenuItem value={1}>1 Minute</MenuItem>
                  <MenuItem value={5}>5 Minutes</MenuItem>
                  <MenuItem value={10}>10 Minutes</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Auto-Save Progress Toggle */}
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", my: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Save />
                <Typography variant="h6" sx={{ ml: 1, color: darkMode ? "#e0e0e0" : "#212529", fontSize: '1rem' }}>
                  Auto-Save Progress
                </Typography>
              </Box>
              <FormControlLabel
                control={<Switch checked={autoSave} onChange={() => setAutoSave(!autoSave)} />}
                label={autoSave ? "Enabled" : "Disabled"}
                sx={{ color: darkMode ? "#e0e0e0" : "#212529" }}
              />
            </Box>

            {/* Notifications Toggle */}
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", my: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Notifications />
                <Typography variant="h6" sx={{ ml: 1, color: darkMode ? "#e0e0e0" : "#212529", fontSize: '1rem' }}>
                  Email Notifications
                </Typography>
              </Box>
              <FormControlLabel
                control={<Switch checked={notifications} onChange={() => setNotifications(!notifications)} />}
                label={notifications ? "Enabled" : "Disabled"}
                sx={{ color: darkMode ? "#e0e0e0" : "#212529" }}
              />
            </Box>

            {/* Save & Reset Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSave}
                sx={{ flex: 1, marginRight: 1 }}
              >
                Save
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                onClick={handleReset}
                sx={{ flex: 1, marginLeft: 1 }}
              >
                Reset
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
      />

    </Box>
    </>
  );
};

export default SettingsCustomizationPage;