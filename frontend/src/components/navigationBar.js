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
  Box
} from "@mui/material";
import logo from "../assets/Image20250320122406.png";
import MenuIcon from "@mui/icons-material/Menu";
import TwitterIcon from '@mui/icons-material/Twitter';
import FacebookIcon from '@mui/icons-material/Facebook';
import InstagramIcon from '@mui/icons-material/Instagram';

function Navbar() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
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
          <Button color="inherit" onClick={() => navigate("/")}>
            Home
          </Button>
          <Button color="inherit" onClick={() => navigate("/aboutus")}>
            About Us
          </Button>
          <Button color="inherit" onClick={() => navigate("/contact")}>
            Contact Us
          </Button>
          <Button color="inherit" onClick={() => navigate("/register")}>
            Sign Up
          </Button>
          <Button color="inherit" onClick={() => navigate("/login")}>
            Login
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
                marginBottom: "16px",
                borderRadius: "8px",
              }}
            />
          )}
          <List>
            {[
              { label: "Home", path: "/" },
              { label: "About Us", path: "/aboutus" },
              { label: "Contact Us", path: "/contact" },
              { label: "Sign Up", path: "/register" },
              { label: "Login", path: "/login" },
            ].map((item) => (
              <ListItem key={item.label} sx={{ justifyContent: "flex-start" }}>
                <Button
                  onClick={() => {
                    navigate(item.path);
                    toggleSidebar(); // Close drawer on navigation
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

export default Navbar;

export function Footer(){
  return(



      <Box
          sx={{
            position: "relative",
            bottom: 0,
            left: 0,
            right: 0,
            backgroundColor: "#003366",
            color: "white",
            padding: "4px",
            textAlign: "center",
          }}
        >
          <Typography variant="body2" sx={{ color: "white", marginBottom: "2px" }}>
            © {new Date().getFullYear()} Skill Bridge Online Test Platform. All rights reserved.
          </Typography>
          <Box sx={{ display: "flex", justifyContent: "center", gap: "2px", marginTop: "2px" }}>
            <IconButton color="inherit" onClick={() => window.open("https://twitter.com", "_blank")}><TwitterIcon /></IconButton>
            <IconButton color="inherit" onClick={() => window.open("https://facebook.com", "_blank")}><FacebookIcon /></IconButton>
            <IconButton color="inherit" onClick={() => window.open("https://instagram.com", "_blank")}><InstagramIcon /></IconButton>
          </Box>
          </Box>
        
  );
}

