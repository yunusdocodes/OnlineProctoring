import React, { useState, useEffect } from "react";
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import {  Typography, Stepper,CardContent,Card,Fade,Alert,Input,Stack,Switch, Step,StepLabel, Button, TextField, Checkbox, FormControlLabel, Paper, Box, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress, IconButton, Drawer, Toolbar, List, ListItem, ListItemText, AppBar, Tooltip } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { Form, useNavigate } from "react-router-dom";
import DeleteIcon from "@mui/icons-material/Delete";
import axios from "axios";
import Papa from "papaparse";
import ImportQuestionsModal from './ImportQuestionModal';
import ContentCopy from '@mui/icons-material/ContentCopy';
import { useParams } from "react-router-dom";
import AdminNavbar from "./adminNavbar";
const steps = ["Test Name & Description", "Question Creation", "Question Bank", "Set Time Limit & Marks", "Set Pass/Fail Criteria", "Settings", "Publish & Share"];
const BASE_URL = "http://localhost:3000/smartbridge/online-test-assessment"; // Replace with your actual base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const EditTestPage = () => {
        const [option, setOption] = useState(null);
        const [file, setFile] = useState(null);
        const [allowRetakes, setAllowRetakes] = useState(false); // Default: false
        const [numberOfRetakes, setNumberOfRetakes] = useState(0); // Default: 0
        const [startDate, setStartDate] = useState("");  // Default empty
        const [modalOpen, setModalOpen] = useState(false);
        const [IsPublic, setIsPublic] = useState(false);
        const [endDate, setEndDate] = useState("");  // Default empty
        const [dueTime, setDueTime] = useState("");  // Default empty
        const [timeLimitPerQuestion, setTimeLimitPerQuestion] = useState(0); // Add this line
        const [fetchedQuestions, setFetchedQuestions] = useState([]); // State to hold fetched questions
        const [testId, setTestId] = useState(null);
        const [category,setCategory] = useState(1);// Unique Test Id
        const [activeStep, setActiveStep] = useState(0);
        const [openCSVModal, setOpenCSVModal] = useState(false);
        const [emailList, setEmailList] = useState([]);
        const [importTestId, setImportTestId] = useState(null);
        const [uploadType, setUploadType] = useState('');
        const [uploading, setUploading] = useState(false);
        const [success, setSuccess] = useState(null);
        const [error, setError] = useState(null);
        const [selectedQuestions, setSelectedQuestions] = useState([]);
        const [instructions, setInstructions] = useState("1. This is an online test.\n 2. Please make sure that you are using the latest version of the browser. We recommend using Google Chrome.\n 3. It's mandatory to disable all the browser extensions and enabled Add-ons or open the assessment in incognito mode.\n 4.If you are solving a coding problem, you will either be required to choose a programming language from the options that have been enabled by the administrator or choose your preferred programming language in case no options have been enabled by the administrator. Note: In case you're solving coding problems: All inputs are from STDIN and output to STDOUT.\n5. If test mandates you to use the webcam, please provide the required permissions and access.\n 6. To know the results, please contact the administrator.\n 7. To refer to the FAQ document, you can click on the HELP button which is present in the top right corner of the test environment.\n Best wishes from Vdart Digital Private Limited!"); // For the introduction text
        const [conclusion, setConclusion] = useState(""); // For the conclusion text
        const [testName, setTestName] = useState("");
        const [randomizeOrder, setRandomizeOrder] = useState(false);
        const [allowBlankAnswers, setAllowBlankAnswers] = useState(false);
        const [penalizeIncorrectAnswers, setPenalizeIncorrectAnswers] = useState(false);
        const [allowJumpAround, setAllowJumpAround] = useState(false);
        const [onlyMoveForward, setOnlyMoveForward] = useState(false);
        const [disableRightClick, setDisableRightClick] = useState(false);
        const [disableCopyPaste, setDisableCopyPaste] = useState(false);
        const [disableTranslate, setDisableTranslate] = useState(false);
        const [disableAutocomplete, setDisableAutocomplete] = useState(false);
        const [disableSpellcheck, setDisableSpellcheck] = useState(false);
        const [disablePrinting, setDisablePrinting] = useState(false);
        const [receiveEmailNotifications, setReceiveEmailNotifications] = useState(false);
        const [notificationEmails, setNotificationEmails] = useState('');
        const [subject, setSubject] = useState(""); // Assuming you have a way to select subjects
        const [difficulty, setDifficulty] = useState(""); // Assuming you have a way to select difficulty
        // Hardcoded owner name for testing
        const [testDescription, setTestDescription] = useState("");
        const [marksPerQuestion, setMarksPerQuestion] = useState(1); // Marks per question
        const [totalQuestions, setTotalQuestions] = useState(0); // Total questions
        const [totalMarks, setTotalMarks] = useState(0); // Total marks
        const [passCriteria, setPassCriteria] = useState();
        const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
        const [loading, setLoading] = useState(false);
        const [isSidebarOpen, setIsSidebarOpen] = useState(false);
        const [questions, setQuestions] = useState([]);
        const [testLink, setTestLink] = useState("");
        const [newOption, setNewOption] = useState("");
        const navigate = useNavigate();
        const { testId: testIdFromParams } = useParams();
        const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
useEffect(() => {
  const fetchTestData = async () => {
    const userToken = localStorage.getItem("user_token");
    try {
      const response = await axios.get(`${API_BASE_URL}/tests/${testIdFromParams}/`, {
        headers: { Authorization: `Token ${userToken}` }
      });

      const data = response.data;
      console.log("Fetched test data:", data);

      // Prefill form fields
      setTestName(data.title);
      setTestDescription(data.description);
      setCategory(data.category);
      setSubject(data.subject);
      setDifficulty(data.difficulty);
      setMarksPerQuestion(data.marks_per_question);
      setPassCriteria(data.pass_criteria);
      setInstructions(data.instructions);
      setConclusion(data.conclusion);
      setTimeLimitPerQuestion(data.time_limit_per_question);
      setStartDate(data.start_date);
      setEndDate(data.end_date);
      setDueTime(data.due_time);
      setIsPublic(data.is_public);
      setAllowRetakes(data.allow_retakes);
      setNumberOfRetakes(data.number_of_retakes);
      setReceiveEmailNotifications(data.receive_email_notifications);
      setNotificationEmails(data.notification_emails || []);
      setTestId(data.id);

      // 🔄 Transform questions to support frontend form logic
      const transformedQuestions = (data.questions || []).map((q) => {
          if (q.type === "multiplechoice") {
            return {
              ...q,
              correctAnswer: typeof q.correct_answer === "number" ? q.correct_answer : -1
            };
          }

          if (q.type === "multipleresponse") {
            return {
              ...q,
              correctAnswers: Array.isArray(q.correct_answer) ? q.correct_answer : []
            };
          }

          if (q.type === "truefalse") {
            return {
              ...q,
              correctAnswer: q.correct_answer === true || q.correct_answer === "true"
            };
          }

          if (q.type === "fillintheblank") {
            return {
              ...q,
              correctAnswer: typeof q.correct_answer === "string" ? q.correct_answer : ""
            };
          }

          return q;
        });


      setQuestions(transformedQuestions);
      setTotalQuestions(transformedQuestions.length);
      setTotalMarks(transformedQuestions.length * data.marks_per_question);
    } catch (error) {
      console.error("Failed to fetch test for editing:", error);
    }
  };

  if (testIdFromParams) {
    fetchTestData();
  }
}, [testIdFromParams]);


  useEffect(() => {
    if (openSuccessDialog && testId) {
        axios.get(`${API_BASE_URL}/get-secure-uuid/${testId}/`)

        .then((res) => {
          const encodedUuid = res.data.encoded_uuid;
          setTestLink(`${BASE_URL}/${encodedUuid}`);
        })
        .catch((err) => {
          console.error("Failed to fetch secure test UUID", err);
        });
    }
  }, [openSuccessDialog, testId]);
  useEffect(() => {
    const fetchQuestions = async () => {
      const userToken = localStorage.getItem("user_token");
      if (!userToken) {
        console.error("No user token found");
        return;
      }

      try {
        const response = await axios.get(`${API_BASE_URL}/questions/`, {
          headers: {
            "Authorization": `Token ${userToken}`
          }
        });
        setFetchedQuestions(response.data);
      } catch (error) {
        console.error("Error fetching questions:", error);
      }
    };

    fetchQuestions();
  }, []);

  const handleCloseImportModal = () => setModalOpen(false);
  const handleCorrectAnswersChange = (qIndex, optionIndex) => {
    const updatedQuestions = [...questions];
    let correctAnswers = updatedQuestions[qIndex].correctAnswers || [];

    const optionValue = updatedQuestions[qIndex].options[optionIndex]; // Get the actual option text

    if (correctAnswers.includes(optionValue)) {
        // Remove answer if already selected
        correctAnswers = correctAnswers.filter(answer => answer !== optionValue);
    } else {
        // Add the answer text
        correctAnswers.push(optionValue);
    }

    updatedQuestions[qIndex].correctAnswers = correctAnswers; // Store values, not indexes
    setQuestions(updatedQuestions);
};
  const handleNext = async () => {
    // Check if all required fields are filled in case 0
    if (activeStep === 0) {
      if (!testName || !testDescription || !category || !subject || !difficulty) {
        alert("Please fill in all fields before proceeding.");
        return;
      }
    }

    // Check if there are questions before moving to the next step
    if (activeStep === 1) {
      if (questions.length === 0) {
        alert("Please create at least one question before proceeding.");
        return;
      }
    }

    // Proceed to the next step
    if (activeStep === steps.length - 1) {
      setLoading(true);
      await handleSubmit();
      setOpenSuccessDialog(true);
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("Test link copied!");
  };
  const handleCSVUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      Papa.parse(file, {
        complete: (results) => {
          const emails = results.data
            .map((row) => row[0]?.trim())
            .filter((email) => email && /\S+@\S+\.\S+/.test(email)); // Basic email check
          setEmailList(emails);
        },
      });
    }
  };

  const handleSaveAndSendEmails = async () => {
    if (!testId || emailList.length === 0) {
      alert("Please upload a valid CSV and ensure test ID is set.");
      return;
    }
    const userToken = localStorage.getItem("user_token");
    try {
      setLoading(true);
 
      const response = await fetch(`${API_BASE_URL}/upload-allowed-emails/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Token ${userToken}` // ✅ If you’re using token-based auth
        },
        body: JSON.stringify({
          test_id: testId,
          emails: emailList
        })
      });
 
      const data = await response.json();
      console.log("✅ Email upload response:", data);
 
      if (response.ok) {
        alert("Emails uploaded and invitations sent!");
      } else {
        console.error("❌ Upload failed:", data);
        alert(data.error || "Failed to send emails.");
      }
    } catch (error) {
      console.error("❌ Error sending emails:", error);
      alert("An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };
 
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

const addTrueFalseQuestion = () => {
  setQuestions(prevQuestions => [
    ...prevQuestions,
    { type: "truefalse", text: "Is this statement true or false?", correctAnswer: null },
  ]);
  setTotalQuestions(prevTotal => prevTotal + 1);
  setTotalMarks(prevMarks => prevMarks + marksPerQuestion);
};

const addMultipleChoiceQuestion = () => {
  setQuestions(prevQuestions => [
    ...prevQuestions,
    { type: "multiplechoice", text: "", options: ["", "", "", ""], correctAnswer: "" },
  ]);
  setTotalQuestions(prevTotal => prevTotal + 1);
  setTotalMarks(prevMarks => prevMarks + marksPerQuestion);
};

const addFillInTheBlankQuestion = () => {
  setQuestions(prevQuestions => [
    ...prevQuestions,
    { type: "fillintheblank", text: "____ is the capital of France.", correctAnswer: "" },
  ]);
  setTotalQuestions(prevTotal => prevTotal + 1);
  setTotalMarks(prevMarks => prevMarks + marksPerQuestion);
};

const addMultipleResponseQuestion = () => {
  setQuestions(prevQuestions => [
    ...prevQuestions,
    { type: "multipleresponse", text: "", options: ["", "", "", ""], correctAnswers: [] },
  ]);
  setTotalQuestions(prevTotal => prevTotal + 1);
  setTotalMarks(prevMarks => prevMarks + marksPerQuestion);
};
  const handleQuestionTextChange = (index, value) => {
    const newQuestions = [...questions];
    newQuestions[index].text = value;
    setQuestions(newQuestions);
  };
    const handleLogout = () => { // Clear any stored authentication data, tokens, etc.
    localStorage.removeItem("user_token"); // Example: Remove an auth token
    alert("You have been logged out.");
    navigate("/login");
  };
  const handleOptionChange = (qIndex, optionIndex, value) => {
    const newQuestions = [...questions];
    if (value === "") {
      newQuestions[qIndex].options = newQuestions[qIndex].options.filter((_, index) => index !== optionIndex);
    } else {
      newQuestions[qIndex].options[optionIndex] = value;
    }
    setQuestions(newQuestions);
  };
  const handleCorrectAnswerChange = (qIndex, value) => {
    // Create a copy of the current questions state
    const updatedQuestions = [...questions];

    // Check if the question exists
    if (updatedQuestions[qIndex]) {
        const questionType = updatedQuestions[qIndex].type;

        if (questionType === "multiplechoice") {
            // For multiple choice, value should be the index of the selected option
            updatedQuestions[qIndex].correctAnswer = value; // Store the index of the selected option
        } else if (questionType === "truefalse") {
            // For true/false, value should be a boolean
            updatedQuestions[qIndex].correctAnswer = value; // Store the boolean value
        }

        setQuestions(updatedQuestions); // Update the state with the new questions array
        console.log(`Question ${qIndex}, Selected Answer: ${updatedQuestions[qIndex].correctAnswer}`); // Log the selected answer
    } else {
        console.error(`Question at index ${qIndex} does not exist.`);
    }
};
const handleCorrectAnswerChanges = (qIndex, optionIndex) => {
  console.log(`Question ${qIndex}, Selected Option: ${optionIndex}`);
  const updatedQuestions = [...questions];
  let correctAnswers = updatedQuestions[qIndex].correctAnswers || []; // Ensure correctAnswers is initialized

  const optionValue = updatedQuestions[qIndex].options[optionIndex];  // Get answer text

  if (correctAnswers.includes(optionValue)) {
      // Remove answer if already selected
      correctAnswers = correctAnswers.filter(answer => answer !== optionValue);
  } else {
      // Add the answer text
      correctAnswers.push(optionValue);
  }

  updatedQuestions[qIndex].correctAnswers = correctAnswers;  // Store values, not indexes
  setQuestions(updatedQuestions);
};

const handleQuestionSelect = (question) => {
    setSelectedQuestions((prevQuestions) => {
        const isAlreadySelected = prevQuestions.some(q => q.id === question.id);
        if (isAlreadySelected) {
            return prevQuestions.filter(q => q.id !== question.id);
        } else {
            return [...prevQuestions, question];
        }
    });
};
  const handleFillInTheBlankAnswerChange = (qIndex, value) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].correctAnswer = value;
    setQuestions(newQuestions);
  };
   const handleAddOption = (qIndex) => {
    const updatedQuestions = [...questions];
    updatedQuestions[qIndex].options.push(newOption);
    setQuestions(updatedQuestions);
    setNewOption(""); // Reset input field
  };

  const handleRemoveQuestion = (qIndex) => {
    const updatedQuestions = questions.filter((_, index) => index !== qIndex);
    setQuestions(updatedQuestions);
    setTotalQuestions(totalQuestions - 1);
    setTotalMarks(totalQuestions - 1 * marksPerQuestion);
  };
const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setSuccess(null);
    setError(null);
};

const handleSubmit = async () => {
    const userToken = localStorage.getItem("user_token");
    setLoading(true);

    try {
        const totalQuestionsCount = questions.length + selectedQuestions.length;
        const totalTimeLimit = totalQuestionsCount * timeLimitPerQuestion;

        const testData = {
            title: testName,
            description: testDescription,
            category,
            max_score: totalQuestionsCount * marksPerQuestion,
            total_marks: totalQuestionsCount * marksPerQuestion,
            subject,
            difficulty,
            time_limit_per_question: timeLimitPerQuestion,
            total_time_limit: totalTimeLimit / 60,
            marks_per_question: marksPerQuestion,
            pass_criteria: passCriteria,
            instructions,
            conclusion,
            scheduled_date: null,
            is_public: IsPublic,
            allow_retakes: allowRetakes,
            number_of_retakes: numberOfRetakes,
            randomize_order: false,
            allow_blank_answers: false,
            penalize_incorrect_answers: false,
            allow_jump_around: false,
            only_move_forward: false,
            indicate_correctness: false,
            display_correct_answer: false,
            show_explanation: false,
            move_on_without_feedback: false,
            show_score: false,
            show_test_outline: false,
            disable_right_click: false,
            disable_copy_paste: false,
            disable_translate: false,
            disable_autocomplete: false,
            disable_spellcheck: false,
            disable_printing: false,
            receive_email_notifications: receiveEmailNotifications,
            notification_emails: notificationEmails,
            start_date: startDate || null,
            end_date: endDate || null,
            due_time: dueTime || null,
            status: "published",
            rank: 1,
            questions: [
                ...questions.map((question) => ({
                    text: question.text,
                    type: question.type,
                    options: question.options ?? [],
                    correct_answer:
                        question.type === "multipleresponse"
                            ? question.correctAnswers
                            : question.correctAnswer ?? "N/A",
                })),
                ...selectedQuestions.map((question) => ({
                    text: question.text,
                    type: question.type,
                    options: question.options ?? [],
                    correct_answer:
                        question.type === "multipleresponse"
                            ? question.correctAnswers
                            : question.correctAnswer ?? "N/A",
                })),
            ],
        };

        // Step 1: Update the test instead of creating a new one
        console.log("Updating test with ID:", testId);
        const response = await axios.put(
            `${API_BASE_URL}/tests/${testId}/`,
            testData,
            {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Token ${userToken}`,
                },
            }
        );

        // Optional Step 2: Upload file if needed
        if (file) {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("test_id", testId);

            await axios.post(
                `${API_BASE_URL}/questions/upload/`,
                formData,
                {
                    headers: {
                        Authorization: `Token ${userToken}`,
                    },
                }
            );
        }

        setSuccess("Test updated successfully!");
        setOpenSuccessDialog(true);
        setFile(null);

    } catch (error) {
        console.error("Error updating test:", error);
        setError(error.response?.data?.error || "Something went wrong.");
    } finally {
        setLoading(false);
    }
};


    const saveQuestions = async (createdTestId) => {
        const userToken = localStorage.getItem("user_token");
   
        try {
            for (const question of questions) {
                // Ensure options are provided and not empty
                const questionData = {
                    text: question.text,
                    type: question.type,
                    options: question.options, // Ensure options is an array
                    correct_answer: question.type === "multipleresponse" ? question.correctAnswers : question.correctAnswer,
                    test: createdTestId // Associate the question with the test
                };
   
                // Check if the question type requires options
                if ((question.type === "multiplechoice" || question.type === "multipleresponse") && questionData.options.length === 0) {
                    alert("Please provide options for the question.");
                    return; // Prevent saving if options are missing
                }
   
                // Make the API call to save the question
                const response = await axios.post(
                    `${API_BASE_URL}/questions/`,
                    questionData,
                    {
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Token ${userToken}` // Include the token in the header
                        },
                    }
                );
   
                console.log("Question saved:", response.data); // Debugging log
            }
            alert("Questions saved successfully!"); // Feedback to the user
        } catch (error) {
            if (error.response) {
                console.error("Submission failed:", error.response.data);
                alert(`Error: ${JSON.stringify(error.response.data)}`); // Log the error response
            } else {
                console.error("Submission failed:", error.message);
                alert("Error: Unable to connect to the server.");
            }
        }
    };

  const renderStepContent = (step) => {
    const totalQuestionsCount = questions.length + selectedQuestions.length;
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <TextField
              label="Test Name"
              fullWidth
              value={testName}
              onChange={(e) => setTestName(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              label="Test Description"
              fullWidth
              rows={2}
              value={testDescription}
              onChange={(e) => setTestDescription(e.target.value)}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }} required>
              <InputLabel id="category-label">Category</InputLabel>
              <Select
                labelId="category-label"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                label="Category"
              >
                <MenuItem value="math">Math</MenuItem>
                <MenuItem value="science">Science</MenuItem>
                <MenuItem value="history">History</MenuItem>
                <MenuItem value="literature">Literature</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Subject"
              fullWidth
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }} required>
              <InputLabel id="difficulty-label">Difficulty</InputLabel>
              <Select
                labelId="difficulty-label"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                label="Difficulty"
              >
                <MenuItem value="easy">Easy</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="hard">Hard</MenuItem>
              </Select>
            </FormControl>
          </Box>
        );
        case 1:
            return (
                <Box sx={{
                    mt: 4,
                    maxWidth: 800,
                    mx: "auto",
                    p: 3,
                    backgroundColor: "#fff",
                    borderRadius: 4,
                    boxShadow: "0 8px 20px rgba(0,0,0,0.15)",
                    transition: "transform 0.3s ease, box-shadow 0.3s ease",
                    "&:hover": {
                        transform: "translateY(-5px)",
                        boxShadow: "0 12px 24px rgba(0,0,0,0.2)"
                    }
                }}>
                    <Typography variant="h4" sx={{
                        mb: 3,
                        textAlign: "center",
                        fontWeight: "bold",
                        color: "#333",
                        background: "linear-gradient(45deg, #00796b, #004d40)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent"
                    }}>
                        Create Questions
                    </Typography>
                    <form onSubmit={saveQuestions}> {/* Change here */}
                        {questions.map((question, qIndex) => (
                            <div key={qIndex} className="question-group" sx={{
                                mb: 3,
                                backgroundColor: "#f9f9f9",
                                padding: 3,
                                borderRadius: 2,
                                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                                transition: "all 0.3s ease",
                                "&:hover": {
                                    boxShadow: "0 6px 16px rgba(0,0,0,0.2)",
                                    transform: "scale(1.02)"
                                }
                            }}>
                         <div
                          style={{
                            display: "flex",
                            alignItems: "flex-start",
                            marginBottom: "0",
                            gap: "10px"
                        }}
                        >
                        <div
                            style={{
                            fontWeight: "bold",
                            color: "#00796b",
                            fontSize: "16px",
                            paddingTop: "12px"
                            }}
                        >
                            {qIndex + 1}.
                        </div>

                        <textarea
                            value={question.text}
                            onChange={(e) => handleQuestionTextChange(qIndex, e.target.value)}
                            placeholder={`Enter question ${qIndex + 1} here`}
                            required
                            rows="2"
                            style={{
                            width: "100%",
                            padding: "12px",
                            fontSize: "16px",
                            borderRadius: "8px",
                            border: "1px solid #ddd",
                            backgroundColor: "#fafafa",
                            resize: "vertical",
                            transition: "border-color 0.3s, box-shadow 0.3s"
                            }}
                            onFocus={(e) => (e.target.style.borderColor = "#00796b")}
                            onBlur={(e) => (e.target.style.borderColor = "#ddd")}
                        />
                        </div>

                                {question.type === "multiplechoice" && (
    <>
        {question.options.map((option, optionIndex) => (
            <div key={optionIndex} className="option-group" sx={{
                mb: 2,
                padding: 2,
                backgroundColor: "#fff",
                borderRadius: 1,
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                transition: "all 0.3s ease",
                "&:hover": {
                    boxShadow: "0 4px 10px rgba(0,0,0,0.2)"
                }
            }}>
                <label style={{ display: "flex", alignItems: "center", fontSize: "14px" }}>
                    <input
                        type="radio"
                        name={`correct_answer-${qIndex}`}
                        checked={question.correctAnswer === optionIndex}
                        onChange={() => handleCorrectAnswerChange(qIndex, optionIndex)}
                        style={{
                            marginRight: "12px",
                            transform: "scale(1.2)",
                            transition: "transform 0.2s",
                            cursor: "pointer"
                        }}
                        onMouseOver={(e) => (e.target.style.transform = "scale(1.3)")}
                        onMouseOut={(e) => (e.target.style.transform = "scale(1.2)")}
                    />
                    <input
                        type="text"
                        value={option || ""}
                        onChange={(e) => handleOptionChange(qIndex, optionIndex, e.target.value)}
                        placeholder={`Option ${optionIndex + 1}`}
                        required
                        style={{
                            padding: "10px",
                            width: "80%",
                            fontSize: "14px",
                            marginLeft: "12px",
                            borderRadius: "8px",
                            border: "1px solid #ccc",
                            backgroundColor: "#fafafa",
                            transition: "border 0.3s, box-shadow 0.3s",
                        }}
                        onFocus={(e) => (e.target.style.borderColor = "#00796b")}
                        onBlur={(e) => (e.target.style.borderColor = "#ccc")}
                    />
                </label>
            </div>
        ))}

<div className="add-option-group" style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
            <input
                type="text"
                className="custom-input"
                value={newOption}
                placeholder="Add another option"
                onChange={(e) => setNewOption(e.target.value)}
                style={{
                    fontSize: "14px",
                    padding: "6px 12px",
                    border: "1px solid #ccc",
                    borderRadius: "20px",
                    cursor: "pointer",
                    width: "100%",
                    maxWidth: "200px",
                }}
            />
            <Button onClick={() => handleAddOption(qIndex)}>Add</Button>
            <IconButton
                onClick={() => handleRemoveQuestion(qIndex)}
                sx={{
                    color: "#d32f2f",
                    "&:hover": {
                        backgroundColor: "#f8d7da",
                    },
                    borderRadius: "50%",
                    padding: "8px",
                }}
                title="Remove question"
            >
                <DeleteIcon />
            </IconButton>
        </div>

        {/* Correct Answer Input */}
        <div style={{ marginTop: "16px" }}>
            <label style={{ fontSize: "14px", fontWeight: "bold" }}>Correct Answer:</label>
            <input
                type="text"
                value={question.options[question.correctAnswer] || ""}
                onChange={(e) => {
                    const selectedOption = e.target.value;
                    const selectedIndex = question.options.indexOf(selectedOption);
                    handleCorrectAnswerChange(qIndex, selectedIndex);
                }}
                placeholder="Type the correct answer here"
                style={{
                    padding: "10px",
                    width: "100%",
                    fontSize: "14px",
                    borderRadius: "8px",
                    border: "1px solid #ccc",
                    backgroundColor: "#fafafa",
                    transition: "border 0.3s, box-shadow 0.3s",
                    marginTop: "8px"
                }}
            />
        </div>
    </>
)}

{question.type === "multipleresponse" && (
    <>
        {question.options.map((option, optionIndex) => (
    <div key={optionIndex} className="form-group" sx={{ mb: 2 }}>
        <label style={{ display: "flex", alignItems: "center", fontSize: "14px" }}>
            <input
                type="checkbox"
                checked={(question.correctAnswers || []).includes(option)}
                onChange={() => handleCorrectAnswersChange(qIndex, optionIndex)}
                style={{ marginRight: "12px", transform: "scale(1.2)" }}
            />
                    <input
                        type="text"
                        value={option || ""}
                        onChange={(e) => handleOptionChange(qIndex, optionIndex, e.target.value)}
                        placeholder={`Option ${optionIndex + 1}`}
                        style={{ fontSize: "14px", padding: "6px", width: "100%", maxWidth: "300px" }}
                        required
                    />
                </label>
            </div>
        ))}

        <div className="add-option-group" style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
            <input
                type="text"
                className="custom-input"
                value={newOption}
                placeholder="Add another option"
                onChange={(e) => setNewOption(e.target.value)}
                style={{
                    fontSize: "14px",
                    padding: "6px 12px",
                    border: "1px solid #ccc",
                    borderRadius: "20px",
                    cursor: "pointer",
                    width: "100%",
                    maxWidth: "200px",
                }}
            />
            <Button onClick={() => handleAddOption(qIndex)}>Add</Button>
            <IconButton
                onClick={() => handleRemoveQuestion(qIndex)}
                sx={{
                    color: "#d32f2f",
                    "&:hover": {
                        backgroundColor: "#f8d7da",
                    },
                    borderRadius: "50%",
                    padding: "8px",
                }}
                title="Remove question"
            >
                <DeleteIcon />
            </IconButton>
        </div>

     {/* Correct Answer Input */}
<div style={{ marginTop: "16px" }}>
    <label style={{ fontSize: "14px", fontWeight: "bold" }}>Correct Answers:</label>
    <input
    type="text"
    value={(question.correctAnswers || []).join(", ")} // ✅ Safe join
    onChange={(e) => {
        const answers = e.target.value.split(",").map(item => item.trim());
        const correctAnswerIndices = answers
            .map(answer => (question.options || []).indexOf(answer))
            .filter(index => index !== -1);
        handleCorrectAnswersChange(qIndex, correctAnswerIndices);
    }}
        placeholder="Type the correct answers here (comma separated)"
        style={{
            padding: "10px",
            width: "100%",
            fontSize: "14px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            backgroundColor: "#fafafa",
            transition: "border 0.3s, box-shadow 0.3s",
            marginTop: "8px"
        }}
    />
</div>
    </>
)}

{question.type === "truefalse" && (
    <>
        <div className="form-group" sx={{ mb: 2 }}>
            <label style={{ display: "flex", alignItems: "center", fontSize: "14px" }}>
                <input
                    type="radio"
                    name={`correct_answer-${qIndex}`}
                    value={true}
                    checked={question.correctAnswer === true}
                    onChange={() => handleCorrectAnswerChange(qIndex, true)}
                    style={{ marginRight: "12px", transform: "scale(1.2)" }}
                />
                True
            </label>
            <br />
            <label style={{ display: "flex", alignItems: "center", fontSize: "14px" }}>
                <input
                    type="radio"
                    name={`correct_answer-${qIndex}`}
                    value={false}
                    checked={question.correctAnswer === false}
                    onChange={() => handleCorrectAnswerChange(qIndex, false)}
                    style={{ marginRight: "12px", transform: "scale(1.2)" }}
                />
                False
            </label>
        </div>

        {/* Correct Answer Input */}
        <div style={{ marginTop: "16px" }}>
            <label style={{ fontSize: "14px", fontWeight: "bold" }}>Correct Answer:</label>
            <input
                type="text"
                value={question.correctAnswer ? "True" : "False"}
                onChange={(e) => {
                    const value = e.target.value.trim().toLowerCase();
                    handleCorrectAnswerChange(qIndex, value === "true");
                }}
                placeholder="Type the correct answer here (True/False)"
                style={{
                    padding: "10px",
                    width: "100%",
                    fontSize: "14px",
                    borderRadius: "8px",
                    border: "1px solid #ccc",
                    backgroundColor: "#fafafa",
                    transition: "border 0.3s, box-shadow 0.3s",
                    marginTop: "8px"
                }}
            />
        </div>

        <div className="add-option-group">
            <br />
            <IconButton
                onClick={() => handleRemoveQuestion(qIndex)}
                sx={{
                    color: "#d32f2f",
                    "&:hover": {
                        backgroundColor: "#f8d7da",
                    },
                    borderRadius: "50%",
                    padding: "8px",
                }}
                title="Remove question"
            >
                <DeleteIcon />
            </IconButton>
        </div>
    </>
)}

{question.type === "fillintheblank" && (
    <>
        <input
            type="text"
            value={question.correctAnswer}
            onChange={(e) => handleFillInTheBlankAnswerChange(qIndex, e.target.value)}
            placeholder="Type your answer"
            required
            className="input-field"
            style={{
                padding: "12px",
                width: "100%",
                fontSize: "16px",
                borderRadius: "8px",
                marginTop: "8px",
                marginBottom: "0",
                border: "1px solid #ccc",
                backgroundColor: "#fafafa",
                transition: "border-color 0.3s",
            }}
            onFocus={(e) => (e.target.style.borderColor = "#00796b")}
            onBlur={(e) => (e.target.style.borderColor = "#ccc")}
        />
        <div className="add-option-group">
            <IconButton
                onClick={() => handleRemoveQuestion(qIndex)}
                sx={{
                    color: "#d32f2f",
                    "&:hover": {
                        backgroundColor: "#f8d7da",
                    },
                    borderRadius: "50%",
                    padding: "8px",
                }}
                title="Remove question"
            >
                <DeleteIcon />
            </IconButton>
        </div>
    </>
)}
                            </div>
                        ))}
                        <Box sx={{ display: "flex", justifyContent: "space-around", mt: 3 }}>
                            <Button variant="contained" sx={{
                                backgroundColor: "#00796b",
                                "&:hover": {
                                    backgroundColor: "#004d40",
                                    transform: "scale(1.05)"
                                },
                                transition: "all 0.3s ease"
                            }} onClick={addMultipleChoiceQuestion}>
                                Multiple Choice
                            </Button>
                            <Button variant="contained" sx={{
                                backgroundColor: "#00796b",
                                "&:hover": {
                                    backgroundColor: "#004d40",
                                    transform: "scale(1.05)"
                                },
                                transition: "all 0.3s ease"
                            }} onClick={addTrueFalseQuestion}>
                                True/False
                            </Button>
                            <Button variant="contained" sx={{
                                backgroundColor: "#00796b",
                                "&:hover": {
                                    backgroundColor: "#004d40",
                                    transform: "scale(1.05)"
                                },
                                transition: "all 0.3s ease"
                            }} onClick={addMultipleResponseQuestion}>
                                Multiple Response
                            </Button>
                            <Button variant="contained" sx={{
                                backgroundColor: "#00796b",
                                "&:hover": {
                                    backgroundColor: "#004d40",
                                    transform: "scale(1.05)"
                                },
                                transition: "all 0.3s ease"
                            }} onClick={addFillInTheBlankQuestion}>
                                Fill-in-Blanks
                            </Button>
                         
                        </Box>
                        </form>
                </Box>
             
            );
            case 2:
            return (
             
                <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 4,
                }}
              >
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                  Select How You Want to Add Questions
                </Typography>
         
                {/* Selection Buttons */}
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 4 }}>
                  <Button
                    variant={option === 'import' ? 'contained' : 'outlined'}
                    onClick={() => { setOption('import'); setUploadType(''); }}
                    sx={{ borderRadius: 2, textTransform: 'none', px: 4 }}
                  >
                    Import Questions
                  </Button>
                  <Button
                    variant={option === 'bank' ? 'contained' : 'outlined'}
                    onClick={() => setOption('bank')}
                    sx={{ borderRadius: 2, textTransform: 'none', px: 4 }}
                  >
                    Select from Question Bank
                  </Button>
                </Stack>
         
                {/* Case 1: Import Questions */}
                <Fade in={option === 'import'}>
                  <Box sx={{ display: option === 'import' ? 'block' : 'none' }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Import Questions
                    </Typography>
         
                    <Stack direction="row" spacing={2} sx={{ mb: 2 }} justifyContent="center">
                      <Button
                        variant={uploadType === 'modal' ? 'contained' : 'outlined'}
                        onClick={() => setUploadType('modal')}
                        sx={{ borderRadius: 2 }}
                      >
                        Import from Test
                      </Button>
                      <Button
                        variant={uploadType === 'file' ? 'contained' : 'outlined'}
                        onClick={() => setUploadType('file')}
                        sx={{ borderRadius: 2 }}
                      >
                        Upload CSV / PDF
                      </Button>
                    </Stack>
         
                    {/* Modal Option */}
                    {uploadType === 'modal' && (
                      <>
                        <Typography variant="body1" sx={{ mb: 1 }}>
                          Open import modal to select questions from an existing test
                        </Typography>
                        <Button
                          variant="outlined"
                          onClick={() => setModalOpen(true)}
                          sx={{ borderRadius: 2, textTransform: 'none' }}
                        >
                          Open Import Modal
                        </Button>
         
                        <ImportQuestionsModal
                          open={modalOpen}
                          onClose={() => setModalOpen(false)}
                          setSelectedImportTest={() => {}}
                        />
                      </>
                    )}
         
                    {/* File Upload Option */}
             
                    {uploadType === 'file' && (
  <Box sx={{ mt: 3, maxWidth: 400, mx: 'auto' }}>
    <Input
      type="file"
      onChange={handleFileChange}
      fullWidth
      sx={{ mb: 2 }}
    />
    <Typography variant="body2" color="textSecondary">
      The selected file will be uploaded automatically after test creation.
    </Typography>
  </Box>
                    )}
                  </Box>
                </Fade>
         
                {/* Case 2: Question Bank */}
                <Fade in={option === 'bank'}>
                  <Box sx={{ display: option === 'bank' ? 'block' : 'none' }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      SELECT QUESTIONS FROM QUESTION BANK
                    </Typography>
         
                    {fetchedQuestions.map((question, index) => (
                      <Card
                        key={index}
                        sx={{
                          mb: 2,
                          borderRadius: 2,
                          boxShadow: '0 4px 10px rgba(0,0,0,0.05)',
                          transition: 'transform 0.2s',
                          '&:hover': { transform: 'scale(1.01)' },
                        }}
                      >
                        <CardContent>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={selectedQuestions.some(q => q.id === question.id)}
                                onChange={() => handleQuestionSelect(question)}
                              />
                            }
                            label={
                              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                                {question.text}
                              </Typography>
                            }
                          />
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                </Fade>
              </Box>
            );
            case 3:
              
                return (
                  
                    <Box sx={{ mt: 2 }}>
                        <TextField
                            label="Time Limit Per Question (in minutes)"
                            type="number"
                            fullWidth
                            value={timeLimitPerQuestion}
                            onChange={(e) => setTimeLimitPerQuestion(e.target.value)}
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            label="Marks Per Question"
                            type="number"
                            fullWidth
                            value={marksPerQuestion}
                            onChange={(e) => {
                                setMarksPerQuestion(e.target.value);
                                setTotalMarks(e.target.value);
                            }}
                            sx={{ mb: 2 }}
                        />
                        <Typography variant="body1" sx={{ mb: 2 }}>
                            Total Questions: {totalQuestionsCount}
                        </Typography>
                        <Typography variant="body1" sx={{ mb: 2 }}>
                            Total Marks: {totalQuestionsCount * totalMarks}
                        </Typography>
                        <Typography variant="body1" sx={{ mb: 2 }}>
                            Total Time Limit: {totalQuestionsCount * timeLimitPerQuestion} minutes
                        </Typography>
                    </Box>
                );
                case 4:
                    return (
                        <TextField
                            select
                            label="Passing Criteria (%)"
                            fullWidth
                            value={passCriteria}
                            onChange={(e) => setPassCriteria(e.target.value)}
                            sx={{ mt: 2 }}
                        >
                            <MenuItem value={25}>25%</MenuItem>
                            <MenuItem value={50}>50%</MenuItem>
                            <MenuItem value={75}>75%</MenuItem>
                            <MenuItem value={100}>100%</MenuItem>
                        </TextField>
                    );
                   
                    case 5:
                                            
                                            return (
                                                <Box sx={{ mt: 1, p: 3, borderRadius: 1, boxShadow: 2, backgroundColor: '#fff' }}>
                                                    {/* Introduction Section */}
                                                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold', color: '#333' }}>
                                                        Introduction
                                                    </Typography>
                                                    <Typography variant="body2" sx={{ mb: 1, color: '#666' }}>
                                                        This text is displayed at the top of the test. You can use it for instructions or leave it blank.
                                                    </Typography>
                                                    <TextField
                                                        label="Instructions"
                                                        multiline
                                                        rows={3}
                                                        fullWidth
                                                        variant="outlined"
                                                        value={instructions}
                                                        onChange={(e) => setInstructions(e.target.value)}
                                                        sx={{ mb: 2, backgroundColor: '#f9f9f9', borderRadius: 1 }}
                                                    />
                                       
                                                    {/* Date and Time Settings */}
                                                    <Typography variant="h6" sx={{ mt: 4, mb: 2, fontWeight: 'bold' }}>
                                                        Date and Time Settings
                                                    </Typography>
                                                    <TextField
                        label="Start Date"
                        type="date"
                        fullWidth
                        onChange={(e) => setStartDate(e.target.value)} // Correct usage
                        sx={{ mb: 2 }}
                        InputLabelProps={{ shrink: true }}
                    />
                    <TextField
                        label="End Date"
                        type="date"
                        fullWidth
                        onChange={(e) => setEndDate(e.target.value)} // Correct usage
                        sx={{ mb: 2 }}
                        InputLabelProps={{ shrink: true }}
                    />
                    <TextField
                        label="Due Time"
                        type="time"
                        fullWidth
                        onChange={(e) => setDueTime(e.target.value)} // Correct usage
                        sx={{ mb: 2 }}
                        InputLabelProps={{ shrink: true }}
                    />
                                                    {/* Navigation Settings */}
                                                    <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
                                                        Navigation Settings
                                                    </Typography>
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={allowJumpAround}
                                                                onChange={(e) => setAllowJumpAround(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Allow jumping between questions"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={onlyMoveForward}
                                                                onChange={(e) => setOnlyMoveForward(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Only move forward after answering"
                                                    />
                                       
                                                   
                                                    {/* Browser Functionality Settings */}
                                                    <Typography variant="h6" sx={{ mt: 4, mb: 2, fontWeight: 'bold', color: '#333' }}>
                                                        Browser Functionality
                                                    </Typography>
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={disableRightClick}
                                                                onChange={(e) => setDisableRightClick(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Disable right-click context menu"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={disableCopyPaste}
                                                                onChange={(e) => setDisableCopyPaste(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Disable copy/paste"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={disableTranslate}
                                                                onChange={(e) => setDisableTranslate(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Disable translate"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={disableAutocomplete}
                                                                onChange={(e) => setDisableAutocomplete(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Disable autocomplete"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={disableSpellcheck}
                                                                onChange={(e) => setDisableSpellcheck(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Disable spellcheck"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={disablePrinting}
                                                                onChange={(e) => setDisablePrinting(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Disable printing"
                                                    />
                                                    {/* Allow Retake Option */}
                                                    <Typography variant="h6" sx={{ mt: 4, mb: 2, fontWeight: 'bold', color: '#333' }}>
                                                        Retake Settings
                                                    </Typography>
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={allowRetakes}
                                                                onChange={(e) => setAllowRetakes(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Allow students to retake the test"
                                                    />
                                                    {allowRetakes && (
                                                        <TextField
                                                            label="Number of Retakes"
                                                            type="number"
                                                            fullWidth
                                                            value={numberOfRetakes}
                                                            onChange={(e) => setNumberOfRetakes(e.target.value)}
                                                            sx={{ mt: 1, mb: 2, backgroundColor: '#f9f9f9', borderRadius: 1 }}
                                                        />
                                                    )}
                                                    {/* Other Settings */}
                                                    <Typography variant="h6" sx={{ mt: 4, mb: 2, fontWeight: 'bold', color: '#333' }}>
                                                        Other Settings
                                                    </Typography>
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={randomizeOrder}
                                                                onChange={(e) => setRandomizeOrder(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Randomize the order of the questions during the test"
                                                    />
                    
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={allowBlankAnswers}
                                                                onChange={(e) => setAllowBlankAnswers(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Allow students to submit blank/empty answers"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={penalizeIncorrectAnswers}
                                                                onChange={(e) => setPenalizeIncorrectAnswers(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Penalize incorrect answers (negative marking)"
                                                    />
                                                              <FormControlLabel
                      control={
                        <Switch
                          checked={IsPublic}
                          onChange={(e) => setIsPublic(e.target.checked)}
                          name="isPublic"
                        />
                      }
                      label="Make this test public"
                    />
                    
                                                     {/* Notifications */}
                                                     <Typography variant="h6" sx={{ mt: 4, mb: 2, fontWeight: 'bold', color: '#333' }}>
                                                        Notifications
                                                    </Typography>
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={receiveEmailNotifications}
                                                                onChange={(e) => setReceiveEmailNotifications(e.target.checked)}
                                                                sx={{ color: '#00796b' }}
                                                            />
                                                        }
                                                        label="Receive an email whenever someone finishes this test"
                                                    />
                                                    {receiveEmailNotifications && (
                                                        <TextField
                                                            label="Enter email addresses (comma separated)"
                                                            variant="outlined"
                                                            fullWidth
                                                            value={notificationEmails}
                                                            onChange={(e) => setNotificationEmails(e.target.value)}
                                                            sx={{ mt: 1, backgroundColor: '#fff', borderRadius: 1 }}
                                                        />
                                                    )}
                                       
                                       
                                                    {/* Conclusion Section */}
                                                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold', color: '#333' }}>
                                                        Conclusion
                                                    </Typography>
                                                    <Typography variant="body2" sx={{ mb: 1, color: '#666' }}>
                                                        This text is displayed at the end of the test.
                                                    </Typography>
                                                    <TextField
                                                        label="Conclusion"
                                                        multiline
                                                        rows={3}
                                                        fullWidth
                                                        variant="outlined"
                                                        placeholder="Type your conclusion text here..."
                                                        onChange={(e) => setConclusion(e.target.value)}
                                                        sx={{ mb: 2, backgroundColor: '#f9f9f9', borderRadius: 1 }}
                                                    />
                                                </Box>
                                            );
                        case 6:
                             // Calculate total questions
                            return (
                                <Box sx={{ mt: 2, p: 4, borderRadius: 2, boxShadow: 3, backgroundColor: '#ffffff' }}>
                                    <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold', color: '#333' }}>
                                        Test Summary
                                    </Typography>
                                    <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold', color: '#00796b' }}>
                                        Test Name: {testName}
                                    </Typography>
                                    <Typography variant="body1" sx={{ mb: 1 }}>
                                        Total Questions: {totalQuestionsCount} {/* Use the combined count */}
                                    </Typography>
                                    <Typography variant="body1" sx={{ mb: 1 }}>
                                        Total Time Limit: {totalQuestionsCount * timeLimitPerQuestion} minutes
                                    </Typography>
                                    <Typography variant="body1" sx={{ mb: 1 }}>
                                        Total Marks: {totalQuestionsCount * marksPerQuestion} {/* Update this if needed */}
                                    </Typography>
                                    <Typography variant="body1" sx={{ mb: 1 }}>
                                        Passing Criteria: {passCriteria}%
                                    </Typography>
                                    <Typography variant="body1" sx={{ mb: 1 }}>
                                        Instructions: {instructions || "No instructions provided."}
                                    </Typography>
                                    <Typography variant="body1" sx={{ mb: 1 }}>
                                        Conclusion: {conclusion || "No conclusion provided."}
                                    </Typography>
                                </Box>
                            );
      default:
        return null;
    }
  };

  return (
    <>
     <AdminNavbar/>
     
      <Box sx={{ position: "fixed", top: "64px", bottom: "0px", left: 0, right: 0, display: "flex", flexDirection: "column", padding: "16px", overflowY: "auto", width: "100vw", maxWidth: "100%", margin: 0 }}>
        <Typography variant="h4" sx={{ mb: 4, fontWeight: "bold", color: "#006699" }}>
          Create New Test
        </Typography>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        <Paper sx={{ p: 3 }}>
          {renderStepContent(activeStep)}
        </Paper>
        <Box sx={{ display: "flex", justifyContent: "space-between", mt: 3, padding: "0 16px" }}>
          <Button variant="outlined " disabled={activeStep === 0} onClick={handleBack}>
            Back
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            disabled={
                (activeStep === 0 && (!testName || !testDescription || !subject || !difficulty)) ||
                (activeStep === 1 && questions.length === 0) || // Disable if no questions are created
                (activeStep === 3 && (!timeLimitPerQuestion || !marksPerQuestion)) || // Disable if time limit per question or marks per question are not set
                (activeStep === 4 && !passCriteria) || // Disable if passing criteria is not set
                (activeStep === 5 && (!instructions || !conclusion)) // Disable if instructions or conclusion are not set
              }
          >
            {activeStep === steps.length - 1 ? "Publish" : "Next"}
          </Button>
        </Box>
        <Dialog open={openSuccessDialog} onClose={() => setOpenSuccessDialog(false)}>
        <DialogTitle>Test Published Successfully!</DialogTitle>
        <DialogContent>
          <Typography>Your test has been published. You can now share the test link below:</Typography>
          <Box sx={{ display: "flex", alignItems: "center", mt: 2 }}>
            <TextField
              value={testLink}
              fullWidth
              margin="normal"
              InputProps={{ readOnly: true }}
            />
            <Tooltip title="Copy Link">
              <IconButton onClick={() => copyToClipboard(testLink)}>
                <ContentCopy />
              </IconButton>
            </Tooltip>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCSVModal(true)} color="primary">Send to</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openCSVModal} onClose={() => setOpenCSVModal(false)}>
        <DialogTitle>Upload Emails for Test Access</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Upload a CSV file with a column named <b>email</b> to give test access to selected participants.
          </Typography>
          <input type="file" accept=".csv" onChange={handleCSVUpload} />

          {emailList.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2">✅ {emailList.length} valid emails loaded:</Typography>
              <ul style={{ maxHeight: 150, overflowY: "auto" }}>
                {emailList.map((email, idx) => (
                  <li key={idx}>{email}</li>
                ))}
              </ul>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCSVModal(false)} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleSaveAndSendEmails} variant="contained" color="primary">
            Save & Send
          </Button>
        </DialogActions>
      </Dialog>
        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
            <CircularProgress />
          </Box>
        )}
      </Box>
     
    </>
  );
};

export default EditTestPage;