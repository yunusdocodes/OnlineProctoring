import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import {

    Typography,

} from '@mui/material';

const TestReport = () => {
  const { testId } = useParams();
  const [report, setReport] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const token = localStorage.getItem("user_token");
        const headers = { Authorization: `Token ${token}` };
        const response = await axios.get(`http://127.0.0.1:8000/api/test-report/${testId}/`, { headers });
        setReport(response.data);
      } catch (error) {
        console.error("Error fetching report:", error);
      }
    };

    fetchReport();
  }, [testId]);
  useEffect(() => {
    console.log("Fetched Report Data:", report);
  }, [report]);
  if (!report) return <p>Loading report...</p>;

  return (
    <div>
<Typography variant="h6">Test Report: {report?.test_name || "N/A"}</Typography>
<Typography>Score: {report?.score ?? "N/A"}%</Typography>
<Typography>Total Questions: {report?.total_questions ?? "N/A"}</Typography>

    </div>
  );
};

export default TestReport;
