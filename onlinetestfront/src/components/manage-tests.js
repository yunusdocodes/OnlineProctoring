import React, { useState, useEffect } from "react";
import axios from "axios";
import { Button, Snackbar, Alert } from "@mui/material";
import {
  Box,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Paper,
  Tooltip,
  IconButton,
  Menu,
  MenuItem,
  CircularProgress,
  Modal,
} from "@mui/material";
import {
  MoreVert,
  Edit,
  ContentCopy,
  Delete,
  Menu as MenuIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import AdminNavbar from "./adminNavbar";

const API_BASE_URL = "http://127.0.0.1:8000";

const ManageTestsPage = () => {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [testLink, setTestLink] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [selectedTest, setSelectedTest] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const token = () => localStorage.getItem("user_token");

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/tests/`, {
          headers: { Authorization: `Token ${token()}` },
        });
        setTests(response.data);
      } catch (error) {
        console.error("Error fetching tests:", error);
        setSnackbarMessage("Failed to fetch tests.");
        setSnackbarOpen(true);
      } finally {
        setLoading(false);
      }
    };
    fetchTests();
  }, []);

  const handleMenuOpen = (event, test) => {
    setMenuAnchor(event.currentTarget);
    setSelectedTest(test);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const handleDuplicateTest = async () => {
    try {
      const userToken = token();
      const response = await axios.post(
        `${API_BASE_URL}/api/tests/${selectedTest.id}/duplicate/`,
        {},
        {
          headers: {
            Authorization: `Token ${userToken}`,
          },
        }
      );

      if (response.data.test_link) {
        setTestLink(response.data.test_link);
        setModalOpen(true);
      }
    } catch (error) {
      console.error("Failed to duplicate test", error);
    }
  };

  const handleEditTest = () => {
    if (selectedTest?.id) {
      navigate(`/edit-test/${selectedTest.id}`);
      handleMenuClose();
    } else {
      console.error("No test selected or test ID is missing");
    }
  };

  const handleDeleteTest = async () => {
    if (selectedTest) {
      try {
        await axios.delete(`${API_BASE_URL}/api/tests/${selectedTest.id}/`, {
          headers: { Authorization: `Token ${token()}` },
        });
        setTests(tests.filter((test) => test.id !== selectedTest.id));
        setSnackbarMessage("Test deleted successfully!");
      } catch (error) {
        setSnackbarMessage("Failed to delete test.");
      }
      setSnackbarOpen(true);
      handleMenuClose();
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <>
      <AdminNavbar />
      <Box sx={{ display: "flex" }}>
        <Box component="main" sx={{ flexGrow: 1, p: 3, pt: 10 }}>
          <Typography variant="h6" sx={{ fontWeight: "bold" }}>
            Test Management Hub
          </Typography>

          {loading ? (
            <CircularProgress />
          ) : (
            <TableContainer component={Paper} sx={{ borderRadius: 2, boxShadow: 3 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: "#003366" }}>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Serial No</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Test No</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Test Name</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Status</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Time Limit (Minutes)</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Duration Date</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Duration Time</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Created At</TableCell>
                    <TableCell sx={{ color: "white", fontWeight: "bold" }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tests.map((test, index) => (
                    <TableRow key={test.id} hover>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>{test.id}</TableCell>
                      <TableCell>{test.title}</TableCell>
                      <TableCell>{test.status ? test.status : "Unknown"}</TableCell>
                      <TableCell>{test.total_time_limit}</TableCell>
                      <TableCell>
                        {test.end_date ? new Date(test.end_date).toLocaleDateString() : "N/A"}
                      </TableCell>
                      <TableCell>{test.due_time || "N/A"}</TableCell>
                      <TableCell>{new Date(test.created_at).toLocaleString()}</TableCell>
                      <TableCell>
                        <Tooltip title="More Actions">
                          <IconButton onClick={(e) => handleMenuOpen(e, test)} sx={{ color: "#003366" }}>
                            <MoreVert />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={handleMenuClose}>
            <MenuItem onClick={handleEditTest}>
              <Edit fontSize="small" sx={{ mr: 1 }} /> Edit
            </MenuItem>
            <MenuItem onClick={handleDuplicateTest}>
              <ContentCopy fontSize="small" sx={{ mr: 1 }} /> Duplicate Test
            </MenuItem>
            <MenuItem onClick={handleDeleteTest}>
              <Delete fontSize="small" sx={{ mr: 1 }} /> Delete
            </MenuItem>
          </Menu>

          <Snackbar
            open={snackbarOpen}
            autoHideDuration={3000}
            onClose={() => setSnackbarOpen(false)}
            message={snackbarMessage}
          />
        <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
            <Box
              sx={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: 400,
                bgcolor: "background.paper",
                boxShadow: 24,
                p: 4,
                borderRadius: 2,
                textAlign: "center",
              }}
            >
              <Typography variant="h6" sx={{ fontSize: 20, mb: 3 }}>
                Test Duplicated Successfully!
              </Typography>
              <Button
                onClick={() => setModalOpen(false)}
                variant="contained"
                color="primary"
              >
                Close
              </Button>
            </Box>
          </Modal>
        </Box>
      </Box>
    </>
  );
};

export default ManageTestsPage;
