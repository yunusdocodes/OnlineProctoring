import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import VideoModal from './videoplayer';
import {
  Paper,
  Typography,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  CircularProgress,
  Chip,
} from "@mui/material";

const TestResultPage = () => {
  const { testId } = useParams();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

useEffect(() => {
   

  const userToken = localStorage.getItem("user_token");
  if (!userToken) {
    console.error("No auth token found");
    setLoading(false);
    return;
  }

  axios.get(`http://localhost:8000/api/test-attempt-results/?test_id=${testId}`, {
      headers: {
        Authorization: `Token ${userToken}`, // 🔐 Pass token here
      },
    })
    .then((res) => {
      setResults(res.data);
      setLoading(false);
    })
    .catch((err) => {
      console.error("Error fetching results", err);
      setLoading(false);
    });
     console.log("Fetched results:", results);
}, [testId]);
 console.log("Fetched results:", results);
  if (loading) return <CircularProgress sx={{ m: 4 }} />;

  return (
    <Paper sx={{ p: 4, m: 4 }}>
      <Typography variant="h5" gutterBottom>
        Results for Test #{testId}
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><b>Name</b></TableCell>
              <TableCell><b>Email</b></TableCell>
              <TableCell><b>Score</b></TableCell>
              <TableCell><b>Result</b></TableCell>
              <TableCell><b>Time Taken</b></TableCell>
              <TableCell><b>Recording</b></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {results.map((attempt) => (
              <TableRow key={attempt.id}>
                <TableCell>{attempt.name}</TableCell>
                <TableCell>{attempt.email}</TableCell>
                <TableCell>{attempt.score !== null ? `${attempt.score}%` : 'Not Evaluated'}</TableCell>
                <TableCell>
                  <Chip
                    label={attempt.passed ? "Passed" : "Failed"}
                    color={attempt.passed ? "success" : "error"}
                    size="small"
                  />
                </TableCell>
                <TableCell>{attempt.time_taken || "-"}</TableCell>
                <TableCell>
                  <VideoModal
                    videoUrl={`http://localhost:8000/api/protected-video/?name=${attempt.name}&test_id=${testId}`}
                    name={attempt.name}
                    testId={testId} // ✅ Add this
                  />

              </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default TestResultPage;
