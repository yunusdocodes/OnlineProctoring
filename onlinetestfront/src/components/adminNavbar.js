import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Drawer,
  List,
  ListItem,
  IconButton,
  Box,
} from "@mui/material";
import logo from "../assets/Image20250320122406.png";
import MenuIcon from "@mui/icons-material/Menu";

function AdminNavbar() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleLogout = () => {
    // Example logout logic
    localStorage.clear();
    navigate("/login");
  };

  return (
    <>
      <AppBar position="fixed" sx={{ backgroundColor: "#003366" }}>
        <Toolbar>
          <IconButton
            color="inherit"
            onClick={toggleSidebar}
            edge="start"
            sx={{ marginRight: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Skill Bridge Online Test Platform
          </Typography>
          <Button color="inherit" onClick={() => navigate("/admin-dashboard")}>
            Home
          </Button>
          <Button color="inherit" onClick={() => navigate("/admin-profile")}>
            Profile
          </Button>
          <Button color="inherit" onClick={() => navigate("/manage-tests")}>
            Test list
          </Button>
          <Button color="inherit" onClick={() => navigate("/adminsettings")}>
            Settings
          </Button>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Drawer open={isSidebarOpen} onClose={toggleSidebar}>
        <Box sx={{ width: 250, textAlign: "center", padding: "16px" }}>
          {isSidebarOpen && (
            <img
              src={logo}
              alt="Logo"
              style={{
                maxWidth: "100%",
                height: "auto",
                // marginBottom: "16px",
                borderRadius: "8px",
              }}
            />
          )}
          <List>
            {[
              { label: "Dashboard", path: "/admin-dashboard" },
              { label: "Test Creation", path: "/testcreation" },
              { label: "Question Creation", path: "/questioncreation" },
              { label: "Manage Test", path: "/manage-tests" },
              { label: "Announcement", path: "/announcement" },
              { label: "Settings", path: "/adminsettings" },
              { label: "Logout", path: "/login" },
            ].map((item) => (
              <ListItem key={item.label} sx={{ justifyContent: "flex-start" }}>
                <Button
                  onClick={() => {
                    if (item.label === "Logout") handleLogout();
                    else navigate(item.path);
                    toggleSidebar();
                  }}
                  sx={{
                    color: "#003366",
                    fontWeight: "bold",
                    fontSize: "16px",
                    width: "100%",
                    justifyContent: "flex-start",
                  }}
                >
                  {item.label}
                </Button>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
    </>
  );
}

export default AdminNavbar;
