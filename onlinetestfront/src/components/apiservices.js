import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Helper to include token in headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('user_token');
  return {
    Authorization: `Token ${token}`,
    'Content-Type': 'application/json'
  };
};

// Interceptors
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('user_token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  config.headers['Content-Type'] = 'application/json';
  return config;
}, (error) => Promise.reject(error));

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('user_token');
      localStorage.removeItem('user_data');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);


// Registration function
export const register = async (userData) => {
  try {
    const response = await api.post('/register/', userData);
    return { data: response.data, success: true };
  } catch (error) {
    console.error('Registration failed:', error);
    return {
      error: error.response?.data || { message: 'Registration failed' },
      success: false,
    };
  }
};

// Login function
export const login  = async (username, password) => {
  try {
    const response = await api.post('/login/', { username, password });
    return { data: response.data, success: true };
  } catch (error) {
    console.error('Login failed:', error);
    return {
      error: error.response?.data || { message: 'Failed to login' },
      success: false,
    };
  }
};

// API Functions

export const fetchUserData = async () => {
  try {
    const response = await api.get('/api/userss');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching user data:", error);
    return {
      data: {},
      error: error.response?.data || { message: "Failed to fetch user data" },
      success: false
    };
  }
};

export const fetchDashboardOverview = async () => {
  try {
    const response = await api.get('/api/dashboard-overview/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching dashboard overview:", error);
    return {
      data: {
        total_students: 0,
        total_tests: 0,
        average_score: 0,
        completion_rate: 0,
        top_scorers: []
      },
      error: error.response?.data || { message: "Failed to fetch dashboard data" },
      success: false
    };
  }
};

export const fetchUserManagementStats = async () => {
  try {
    const response = await api.get('/api/user-management-stats/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching user management stats:", error);
    return {
      data: {
        total_users: 0,
        active_users: 0,
        admin_users: 0,
        normal_users: 0
      },
      error: error.response?.data || { message: "Failed to fetch user stats" },
      success: false
    };
  }
};

export const fetchTestsData = async () => {
  try {
    const response = await api.get('/api/tests/analytics/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching tests data:", error);
    return {
      data: {
        average_marks: 0,
        max_score: 0,
        total_tests: 0
      },
      error: error.response?.data || { message: "Failed to fetch test analytics" },
      success: false
    };
  }
};

export const fetchFeedbacks = async () => {
  try {
    const response = await api.get('/api/feedbacks/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching feedback:", error);
    return {
      data: [],
      error: error.response?.data || { message: "Failed to fetch feedback" },
      success: false
    };
  }
};

export const fetchTestsManagement = async () => {
  try {
    const response = await api.get('/api/tests/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching tests:", error);
    return {
      data: [],
      error: error.response?.data || { message: "Failed to fetch tests" },
      success: false
    };
  }
};

export const fetchTestCompletionRates = async () => {
  try {
    const response = await api.get('/api/test-completion-rates/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching completion rates:", error);
    return {
      data: {},
      error: error.response?.data || { message: "Failed to fetch completion rates" },
      success: false
    };
  }
};

export const fetchAdminNotifications = async () => {
  try {
    const response = await api.get('/api/admin-notifications/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching notifications:", error);
    return {
      data: [],
      error: error.response?.data || { message: "Failed to fetch notifications" },
      success: false
    };
  }
};

export const markNotificationsAsRead = async () => {
  try {
    await api.post('/api/admin-notifications/mark-read/');
    return { success: true };
  } catch (error) {
    console.error("Error marking notifications as read:", error);
    return {
      success: false,
      error: error.response?.data || { message: "Failed to mark notifications as read" }
    };
  }
};

export const fetchUserProfile = async (userId) => {
  try {
    const response = await api.get(`/api/users/${userId}/`);
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching user profile:", error);
    return {
      data: {},
      error: error.response?.data || { message: "Failed to fetch user profile" },
      success: false
    };
  }
};

export const submitContactForm = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/contact-submissions/`, data, {
      headers: getAuthHeaders()
    });
    return {
      data: response.data,
      success: true,
      message: "Contact form submitted successfully"
    };
  } catch (error) {
    console.error("Error submitting contact form:", error);
    return {
      error: error.response?.data || { message: "Failed to submit contact form" },
      success: false
    };
  }
};

export const uploadProfilePicture = (formData) => {
  return api.post('/api/users/upload_profile_picture/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const updateUserProfile = (userId, data) => {
  return api.put(`/api/users/${userId}/`, data);
};

export const changePassword = (currentPassword, newPassword) => {
  return api.post('/api/users/change_password/', {
    current_password: currentPassword,
    new_password: newPassword
  });
};

// Manage Tests API Functions

export const fetchTests = async () => {
  try {
    const response = await api.get('/api/tests/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching tests:", error);
    return {
      data: [],
      error: error.response?.data || { message: "Failed to fetch tests" },
      success: false
    };
  }
};

export const duplicateTest = async (testId) => {
  try {
    const response = await api.post(`/api/tests/${testId}/duplicate/`);
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Failed to duplicate test", error);
    return {
      success: false,
      error: error.response?.data || { message: "Failed to duplicate test" }
    };
  }
};

export const deleteTest = async (testId) => {
  try {
    await api.delete(`/api/tests/${testId}/`);
    return { success: true };
  } catch (error) {
    console.error("Failed to delete test", error);
    return {
      success: false,
      error: error.response?.data || { message: "Failed to delete test" }
    };
  }
};

// Login function
export const loginUser = async (username, password) => {
  try {
    const response = await api.post('/login/', { username, password });
    return { data: response.data, success: true };
  } catch (error) {
    console.error('Login failed:', error);
    return {
      error: error.response?.data || { message: 'Failed to login' },
      success: false,
    };
  }
};


// Admin Settings API Functions
export const fetchAdminSettings = async () => {
  try {
    const response = await api.get('/api/admin-settings/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching admin settings:", error);
    return {
      data: {},
      error: error.response?.data || { message: "Failed to fetch admin settings" },
      success: false
    };
  }
};

export const createAdminSettings = async (settingsData) => {
  try {
    const response = await api.post('/api/admin-settings/', settingsData);
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error creating admin settings:", error);
    return {
      error: error.response?.data || { message: "Failed to create admin settings" },
      success: false
    };
  }
};

export const updateAdminSettings = async (settingsId, settingsData) => {
  try {
    const response = await api.patch(`/api/admin-settings/${settingsId}/`, settingsData);
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error updating admin settings:", error);
    return {
      error: error.response?.data || { message: "Failed to update admin settings" },
      success: false
    };
  }
};

export const saveOrUpdateAdminSettings = async (settingsId, settingsData) => {
  if (settingsId) {
    return await updateAdminSettings(settingsId, settingsData);
  } else {
    return await createAdminSettings(settingsData);
  }
};
// Announcements API Functions
export const fetchAnnouncements = async () => {
  try {
    const response = await api.get('/announcements/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching announcements:", error);
    return {
      data: [],
      error: error.response?.data || { message: "Failed to fetch announcements" },
      success: false
    };
  }
};

export const createAnnouncement = async (announcementData) => {
  try {
    const response = await api.post('/announcements/', announcementData);
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error creating announcement:", error);
    return {
      error: error.response?.data || { message: "Failed to create announcement" },
      success: false
    };
  }
};

export const deleteAnnouncement = async (announcementId) => {
  try {
    await api.delete(`/announcements/${announcementId}/`);
    return { success: true };
  } catch (error) {
    console.error("Error deleting announcement:", error);
    return {
      success: false,
      error: error.response?.data || { message: "Failed to delete announcement" }
    };
  }
};

// Attempted Tests API Functions
export const fetchAttemptedTests = async () => {
  try {
    const response = await api.get('/attempted-tests/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching attempted tests:", error);
    return {
      data: [],
      error: error.response?.data || { message: "Failed to fetch attempted tests" },
      success: false
    };
  }
};

export const fetchTestStatistics = async () => {
  try {
    const response = await api.get('/test-attempts/statistics/');
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching test statistics:", error);
    return {
      data: {},
      error: error.response?.data || { message: "Failed to fetch test statistics" },
      success: false
    };
  }
};

export const fetchTestReview = async (testId) => {
  try {
    const response = await api.get(`/test-attempts/${testId}/review/`);
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error fetching test review:", error);
    return {
      data: null,
      error: error.response?.data || { message: "Failed to fetch test review" },
      success: false
    };
  }
};

export const exportCertificate = async (testId) => {
  try {
    const response = await api.get(`/test-attempts/${testId}/export_certificate/`, {
      responseType: 'blob'
    });
    return { data: response.data, success: true };
  } catch (error) {
    console.error("Error exporting certificate:", error);
    return {
      error: error.response?.data || { message: "Failed to export certificate" },
      success: false
    };
  }
};

export const logoutUser = () => {
  return api.post('/api/logout/');
};

// Export base api instance
export { api};