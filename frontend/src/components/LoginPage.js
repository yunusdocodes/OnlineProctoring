import React, { useState } from 'react';
import axios from 'axios';
import {
    TextField,
    Button,
    Grid,
    Typography,
    Container,
    Alert,
    Link,
    Box,
    Card,
    CardContent,
    InputAdornment,
} from '@mui/material';
import { Lock, AccountCircle } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; // Ensure this matches your backend URL

const LoginPage = () => {
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [errorMessage, setErrorMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const { enqueueSnackbar } = useSnackbar();
    const navigate = useNavigate();

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevState) => ({
            ...prevState,
            [name]: value,
        }));
        setErrorMessage(''); // Clear error message on input change
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/login/`, {
                username: formData.username,
                password: formData.password,
            });

            if (response.data.user_token) {
                const userToken = response.data.user_token;
                const userRole = response.data.role;
                const userId = response.data.user_id;

                console.log("New token generated:", userToken);

                // Clear any old token just to be safe
                localStorage.removeItem("user_token");

                // Store token under a consistent key
                localStorage.setItem("user_token", userToken);
                localStorage.setItem("user_id", userId);
                
                // Set axios default Authorization header for future requests
                axios.defaults.headers.common["Authorization"] = `Token ${userToken}`;

                enqueueSnackbar("Login successful!", { variant: "success" });

                // Redirect based on user role
                if (userRole === "admin") {
                    navigate("/admin-dashboard");
                } else {
                    navigate("/user-dashboard");
                }
            } else {
                setErrorMessage("Login failed. Please check your credentials.");
            }
        } catch (error) {
            setErrorMessage("Invalid credentials or something went wrong.");
            enqueueSnackbar("Login failed. Please check your credentials!", { variant: "error" });
        } finally {
            setLoading(false);
        }
    };

    const handleForgotPassword = () => {
        navigate('/forgot-password');
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
            }}
        >
            <Container maxWidth="xs">
                <Card elevation={3} sx={{ p: 2 }}>
                    <CardContent>
                        <Typography variant="h5" align="center" gutterBottom>
                            Log in to continue
                        </Typography>

                        <Box component="form" onSubmit={handleSubmit} noValidate>
                            <Grid container spacing={2}>
                                <Grid item xs={12}>
                                    <TextField
                                        label="Username or email"
                                        type="text"
                                        name="username"
                                        fullWidth
                                        variant="outlined"
                                        value={formData.username}
                                        onChange={handleInputChange}
                                        required
                                        InputProps={{
                                            startAdornment: (
                                                <InputAdornment position="start">
                                                    <AccountCircle />
                                                </InputAdornment>
                                            ),
                                        }}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        label="Password"
                                        type="password"
                                        name="password"
                                        fullWidth
                                        variant="outlined"
                                        value={formData.password}
                                        onChange={handleInputChange}
                                        required
                                        InputProps={{
                                            startAdornment: (
                                                <InputAdornment position="start">
                                                    <Lock />
                                                </InputAdornment>
                                            ),
                                        }}
                                    />
                                </Grid>
                            </Grid>

                            {errorMessage && (
                                <Box mt={2}>
                                    <Alert severity="error">{errorMessage}</Alert>
                                </Box>
                            )}

                            <Box mt={2}>
                                <Button
                                    type="submit"
                                    variant="contained"
                                    color="primary"
                                    fullWidth
                                    size="medium"
                                    disabled={loading} // Disable button while loading
                                >
                                    {loading ? 'Logging In...' : 'Log In'}
                                </Button>
                            </Box>
                        </Box>

                        <Box textAlign="center" mt={2}>
                            <Link component="button" variant="body2" onClick={handleForgotPassword}>
                                Forgot Password?
                            </Link>
                        </Box>
                    </CardContent>
                </Card>
            </Container>
        </Box>
    );
};

export default LoginPage;
