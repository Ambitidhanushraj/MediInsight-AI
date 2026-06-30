import { useEffect, useState } from "react";
import axios from "axios";
import jsPDF from "jspdf";

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [reportId, setReportId] = useState("");
  const [loading, setLoading] = useState(false);
  const [age, setAge] = useState("");
  const [sex, setSex] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [answerModel, setAnswerModel] = useState("");
  const [reportAnswer, setReportAnswer] = useState("");
  const [reportAnswerModel, setReportAnswerModel] = useState("");
  const [historyItems, setHistoryItems] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [doctorMode, setDoctorMode] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem("doctorMode") === "true";
  });
  const [reportList, setReportList] = useState([]);
  const [compareReportId, setCompareReportId] = useState("");
  const [compareData, setCompareData] = useState(null);
  const [compareFilter, setCompareFilter] = useState("all");
  const [loadingMedicalAnswer, setLoadingMedicalAnswer] = useState(false);
  const [loadingReportAnswer, setLoadingReportAnswer] = useState(false);
  const [analysisSearch, setAnalysisSearch] = useState("");
  const [analysisStatusFilter, setAnalysisStatusFilter] = useState("all");
  const [analysisSortBy, setAnalysisSortBy] = useState("severity");
  const [toast, setToast] = useState({
    show: false,
    message: "",
    type: "info",
  });

  useEffect(() => {
    loadHistory("");
    loadReportList();
  }, []);

  const showToast = (message, type = "info") => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast((prev) => ({ ...prev, show: false }));
    }, 2200);
  };

  const scrollToSection = (sectionId) => {
    const target = document.getElementById(sectionId);
    if (!target) return;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const toCsvValue = (value) => {
    const text = String(value ?? "");
    return `"${text.replace(/"/g, '""')}"`;
  };

  const downloadCsvFile = (filename, headers, rows) => {
    const csv = [
      headers.map(toCsvValue).join(","),
      ...rows.map((row) => row.map(toCsvValue).join(",")),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportAnalysisCsv = () => {
    const rows = getFilteredAnalysisRows().map((row) => [
      row.name,
      row.value,
      row.status,
      result?.report_type || "Unknown",
      result?.risk_level || "Unknown",
    ]);
    downloadCsvFile(
      `analysis_${(result?.report_type || "report").toLowerCase()}_${new Date().toISOString().slice(0, 10)}.csv`,
      ["Parameter", "Value", "Status", "Report Type", "Risk Level"],
      rows
    );
    showToast("Analysis CSV exported", "success");
  };

  const exportComparisonCsv = () => {
    if (!compareData) {
      showToast("Load a comparison report first", "error");
      return;
    }

    const rows = getComparisonRows().map(([param, curr]) => {
      const prev = compareData.analysis?.[param];
      const prevVal = prev?.value ?? "";
      const currVal = curr?.value ?? "";
      let delta = "";
      const prevNum = parseFloat(prevVal);
      const currNum = parseFloat(currVal);
      if (!Number.isNaN(prevNum) && !Number.isNaN(currNum)) {
        delta = (currNum - prevNum).toFixed(2);
      }
      return [
        param,
        prevVal,
        prev?.status || "",
        currVal,
        curr?.status || "",
        delta,
      ];
    });

    downloadCsvFile(
      `comparison_${new Date().toISOString().slice(0, 10)}.csv`,
      ["Parameter", "Previous Value", "Previous Status", "Current Value", "Current Status", "Delta"],
      rows
    );
    showToast("Comparison CSV exported", "success");
  };

  const toggleDoctorMode = () => {
    const nextMode = !doctorMode;
    setDoctorMode(nextMode);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("doctorMode", nextMode ? "true" : "false");
    }
    showToast(nextMode ? "Doctor Mode enabled" : "Patient Mode enabled", "info");
  };

  const loadHistory = async (currentReportId = "") => {
    try {
      const url = currentReportId
        ? `${API_BASE_URL}/chat-history?report_id=${encodeURIComponent(currentReportId)}&limit=20`
        : `${API_BASE_URL}/chat-history?limit=20`;
      const response = await axios.get(url);
      setHistoryItems(response.data.items || []);
    } catch (error) {
      console.error(error);
    }
  };

  const clearHistory = async (currentReportId = "") => {
    try {
      const url = currentReportId
        ? `${API_BASE_URL}/chat-history?report_id=${encodeURIComponent(currentReportId)}`
        : `${API_BASE_URL}/chat-history`;
      await axios.delete(url);
      await loadHistory(currentReportId);
      showToast("Chat history cleared", "success");
    } catch (error) {
      console.error(error);
      showToast("Failed to clear history", "error");
    }
  };

  const uploadReport = async () => {
    if (!file) {
      showToast("Please select a file", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    if (age) formData.append("age", age);
    if (sex) formData.append("sex", sex);

    try {
      setLoading(true);

      const response = await axios.post(
        `${API_BASE_URL}/upload-report`,
        formData
      );

      setResult(response.data);
      setReportId(response.data.report_id || "");
      await loadHistory(response.data.report_id || "");
      // Refresh report list for comparison picker
      loadReportList();
      showToast("Report analyzed successfully", "success");
    } catch (error) {
      console.error(error);
      showToast("Upload failed", "error");
    } finally {
      setLoading(false);
    }
  };

  const askMedical = async () => {
    if (!question.trim()) {
      showToast("Please enter a question", "error");
      return;
    }

    try {
      setLoadingMedicalAnswer(true);
      const response = await axios.post(
        `${API_BASE_URL}/ask-medical`,
        {
          question: question,
          doctor_mode: doctorMode,
        }
      );

      setAnswer(response.data.answer);
      setAnswerModel(response.data.model || "");
      await loadHistory(reportId);
    } catch (error) {
      console.error(error);
      showToast("Failed to get answer", "error");
    } finally {
      setLoadingMedicalAnswer(false);
    }
  };

  const askAboutReport = async () => {
    if (!question.trim()) {
      showToast("Please enter a question", "error");
      return;
    }

    if (!result?.text_preview) {
      showToast("Please upload a report first", "error");
      return;
    }

    try {
      setLoadingReportAnswer(true);
      const response = await axios.post(
        `${API_BASE_URL}/ask-report`,
        {
          question: question,
          report_text: result.text_preview,
          report_id: reportId || null,
          doctor_mode: doctorMode,
        }
      );

      setReportAnswer(response.data.answer);
      setReportAnswerModel(response.data.model || "");
      await loadHistory(reportId);
    } catch (error) {
      console.error(error);
      showToast("Failed to get report answer", "error");
    } finally {
      setLoadingReportAnswer(false);
    }
  };

  const downloadPDF = () => {
    if (!result) return;

    const pdf = new jsPDF();

    pdf.setFontSize(18);
    pdf.text("MediInsight AI Report", 20, 20);

    pdf.setFontSize(12);
    pdf.text(`Report Type: ${result.report_type}`, 20, 40);
    pdf.text(`Risk Level: ${result.risk_level}`, 20, 55);
    pdf.text(`Summary: ${result.summary}`, 20, 70);

    pdf.save("mediinsight-report.pdf");
  };

  const loadReportList = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reports?limit=20`);
      setReportList(response.data.reports || []);
    } catch (error) {
      console.error(error);
    }
  };

  const loadComparison = async () => {
    if (!compareReportId) return;
    try {
      const response = await axios.get(`${API_BASE_URL}/reports/${compareReportId}/analysis`);
      setCompareData(response.data);
      showToast("Comparison report loaded", "success");
    } catch (error) {
      console.error(error);
      showToast("Could not load comparison report", "error");
    }
  };

  const chartData = result
    ? Object.entries(result.analysis || {}).map(([name, data]) => ({
        name,
        value: data.value,
      }))
    : [];

  const getHealthScore = () => {
    if (!result) return 0;

    if (result.risk_level === "Low Risk") return 90;
    if (result.risk_level === "Moderate Risk") return 70;

    return 40;
  };

  const getStatusSeverity = (status) => {
    if (status === "Critical High" || status === "Critical Low") return 4;
    if (status === "High" || status === "Low") return 3;
    if (status === "Unknown") return 2;
    return 1;
  };

  const getFilteredAnalysisRows = () => {
    const rows = Object.entries(result?.analysis || {}).map(([name, data]) => ({
      name,
      ...data,
    }));

    const filteredRows = rows.filter((row) => {
      const matchesSearch = row.name.toLowerCase().includes(analysisSearch.toLowerCase());
      const matchesStatus =
        analysisStatusFilter === "all"
          ? true
          : analysisStatusFilter === "abnormal"
          ? row.status !== "Normal"
          : analysisStatusFilter === "critical"
          ? row.status === "Critical Low" || row.status === "Critical High"
          : row.status === analysisStatusFilter;
      return matchesSearch && matchesStatus;
    });

    return filteredRows.sort((a, b) => {
      if (analysisSortBy === "name") {
        return a.name.localeCompare(b.name);
      }
      if (analysisSortBy === "value") {
        const av = parseFloat(a.value);
        const bv = parseFloat(b.value);
        if (Number.isNaN(av) && Number.isNaN(bv)) return 0;
        if (Number.isNaN(av)) return 1;
        if (Number.isNaN(bv)) return -1;
        return bv - av;
      }
      return getStatusSeverity(b.status) - getStatusSeverity(a.status);
    });
  };

  const getComparisonRows = () => {
    const rows = Object.entries(result?.analysis || {});
    return rows.filter(([param, curr]) => {
      const prev = compareData?.analysis?.[param];
      if (compareFilter === "abnormal") {
        return curr.status !== "Normal" || (prev && prev.status !== "Normal");
      }
      if (compareFilter === "changed") {
        if (!prev) return false;
        const currNum = parseFloat(curr?.value);
        const prevNum = parseFloat(prev?.value);
        if (!Number.isNaN(currNum) && !Number.isNaN(prevNum)) {
          return currNum !== prevNum;
        }
        return String(curr?.value) !== String(prev?.value);
      }
      return true;
    });
  };

  const getComparisonSummary = () => {
    const rows = getComparisonRows();
    let increased = 0;
    let decreased = 0;
    let unchanged = 0;

    rows.forEach(([param, curr]) => {
      const prev = compareData?.analysis?.[param];
      if (!prev) return;
      const currNum = parseFloat(curr?.value);
      const prevNum = parseFloat(prev?.value);
      if (Number.isNaN(currNum) || Number.isNaN(prevNum)) return;
      if (currNum > prevNum) increased += 1;
      else if (currNum < prevNum) decreased += 1;
      else unchanged += 1;
    });

    return { increased, decreased, unchanged };
  };

  const pageClass = darkMode
    ? "min-h-screen bg-[radial-gradient(circle_at_top_right,_#172554_0%,_#0f172a_40%,_#020617_100%)] p-8 text-white"
    : "min-h-screen bg-[radial-gradient(circle_at_top_right,_#e0f2fe_0%,_#f8fafc_45%,_#eef2ff_100%)] p-8";

  const cardClass = darkMode
    ? "bg-slate-800/90 shadow rounded-xl p-4 text-white border border-slate-700"
    : "bg-white/90 shadow rounded-xl p-4 border border-slate-200";

  const panelClass = darkMode
    ? "bg-slate-800/90 rounded-xl shadow-lg border border-slate-700 p-6 mb-6 text-white"
    : "bg-white/90 rounded-xl shadow-lg border border-slate-200 p-6 mb-6";

  const sectionClass = darkMode
    ? "bg-slate-800/90 rounded-xl shadow p-6 mb-6 text-white border border-slate-700"
    : "bg-white/90 rounded-xl shadow p-6 mb-6 border border-slate-200";

  const tableHeaderClass = darkMode ? "bg-slate-700" : "bg-gray-100";

  const inputClass = darkMode
    ? "border border-slate-600 bg-slate-700 text-white p-2 rounded w-full"
    : "border p-2 rounded w-full";

  return (
    <div className={pageClass}>
      {toast.show && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-2 rounded-lg shadow-lg text-white ${
            toast.type === "error"
              ? "bg-red-600"
              : toast.type === "success"
              ? "bg-emerald-600"
              : "bg-sky-600"
          }`}
        >
          {toast.message}
        </div>
      )}
      <div className="max-w-7xl mx-auto">
        <div className={`sticky top-4 z-20 mb-8 rounded-2xl backdrop-blur shadow-lg px-5 py-4 ${darkMode ? "bg-slate-900/70 border border-slate-700" : "bg-white/70 border border-slate-200"}`}>
          <div className="flex flex-wrap justify-between items-center gap-3">
            <div>
              <h1 className="text-4xl font-black tracking-tight" style={{ fontFamily: "Poppins, ui-sans-serif" }}>
                MediInsight AI
              </h1>
              <p className="text-sm opacity-70">Clinical report intelligence for patients and doctors</p>
            </div>

            <div className="flex gap-2 items-center">
            <button
              onClick={toggleDoctorMode}
              className={`px-4 py-2 rounded font-semibold transition-colors ${
                doctorMode
                  ? "bg-blue-700 text-white"
                  : "bg-blue-100 text-blue-800"
              }`}
              title="Switches AI responses between patient-friendly and clinical language"
            >
              {doctorMode ? "🩺 Doctor Mode" : "👤 Patient Mode"}
            </button>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="bg-gray-700 text-white px-4 py-2 rounded"
            >
              {darkMode ? "☀ Light Mode" : "🌙 Dark Mode"}
            </button>
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            <div className={`rounded-lg px-3 py-2 ${darkMode ? "bg-slate-800" : "bg-slate-100"}`}>
              <span className="opacity-70">Mode</span>
              <p className="font-semibold">{doctorMode ? "Doctor" : "Patient"}</p>
            </div>
            <div className={`rounded-lg px-3 py-2 ${darkMode ? "bg-slate-800" : "bg-slate-100"}`}>
              <span className="opacity-70">Saved Reports</span>
              <p className="font-semibold">{reportList.length}</p>
            </div>
            <div className={`rounded-lg px-3 py-2 ${darkMode ? "bg-slate-800" : "bg-slate-100"}`}>
              <span className="opacity-70">Chat Entries</span>
              <p className="font-semibold">{historyItems.length}</p>
            </div>
            <div className={`rounded-lg px-3 py-2 ${darkMode ? "bg-slate-800" : "bg-slate-100"}`}>
              <span className="opacity-70">Current Risk</span>
              <p className="font-semibold">{result?.risk_level || "No report"}</p>
            </div>
          </div>
        </div>

        <div className={`sticky top-40 z-10 mb-6 rounded-xl px-3 py-2 shadow ${darkMode ? "bg-slate-900/80 border border-slate-700" : "bg-white/80 border border-slate-200"}`}>
          <div className="flex flex-wrap gap-2 text-sm">
            <button onClick={() => scrollToSection("upload-section")} className="px-3 py-1 rounded-full bg-sky-600 text-white">Upload</button>
            <button onClick={() => scrollToSection("analysis-section")} className="px-3 py-1 rounded-full bg-indigo-600 text-white">Analysis</button>
            <button onClick={() => scrollToSection("chat-section")} className="px-3 py-1 rounded-full bg-emerald-600 text-white">Chat</button>
            <button onClick={() => scrollToSection("compare-section")} className="px-3 py-1 rounded-full bg-amber-600 text-white">Compare</button>
            <button onClick={() => scrollToSection("timeline-section")} className="px-3 py-1 rounded-full bg-violet-600 text-white">Timeline</button>
          </div>
        </div>

        {/* Upload Section */}
        <div id="upload-section" className={sectionClass}>
          <h2 className="text-xl font-semibold mb-4">
            Upload Medical Report
          </h2>

          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            className="mb-4"
          />

          <div className="flex gap-4 mb-4">
            <div>
              <label className="text-sm font-medium mr-2">Age (optional)</label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="e.g. 35"
                className={`${inputClass} w-24`}
                min="1" max="120"
              />
            </div>
            <div>
              <label className="text-sm font-medium mr-2">Sex (optional)</label>
              <select
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                className={inputClass + " w-32"}
              >
                <option value="">Select</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
          </div>

          <br />

          <button
            onClick={uploadReport}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg"
          >
            Upload Report
          </button>

          {loading && (
            <div className="mt-4 animate-pulse">
              <p className="text-blue-600 font-semibold mb-2">Analyzing report...</p>
              <div className="h-3 bg-slate-300 rounded w-1/2 mb-2" />
              <div className="h-3 bg-slate-200 rounded w-2/3 mb-2" />
              <div className="h-3 bg-slate-300 rounded w-1/3" />
            </div>
          )}
        </div>

        {result && (
          <>
            {/* Critical Alert Banner */}
            {result.has_critical && (
              <div className="bg-red-600 text-white rounded-xl p-4 mb-6 shadow-lg flex items-start gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <p className="font-bold text-lg">CRITICAL VALUES DETECTED</p>
                  <p className="text-sm mt-1">
                    The following parameters are at dangerous levels and require <strong>immediate medical attention</strong>:
                    {" "}{result.critical_parameters?.join(", ")}
                  </p>
                  <p className="text-xs mt-1 opacity-90">Please consult a doctor or go to the nearest emergency facility immediately.</p>
                </div>
              </div>
            )}
            {/* Dashboard Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className={cardClass}>
                <h3 className="font-semibold text-gray-500">
                  Report Type
                </h3>

                <p className="text-xl font-bold">
                  {result.report_type}
                </p>
              </div>

              <div className={cardClass}>
                <h3 className="font-semibold text-gray-500">
                  Risk Level
                </h3>

                <p
                  className={`text-xl font-bold ${
                    result.risk_level?.includes("High")
                      ? "text-red-600"
                      : result.risk_level?.includes("Moderate")
                      ? "text-orange-500"
                      : "text-green-600"
                  }`}
                >
                  {result.risk_level}
                </p>
              </div>

              <div className={cardClass}>
                <h3 className="font-semibold text-gray-500">
                  Parameters
                </h3>

                <p className="text-xl font-bold">
                  {Object.keys(result.analysis || {}).length}
                </p>
              </div>

              <div className={cardClass}>
                <h3 className="font-semibold text-gray-500">
                  Health Score
                </h3>

                <p className="text-xl font-bold text-blue-600">
                  {getHealthScore()}%
                </p>
              </div>
            </div>

            {/* Confidence Score */}
            {result.confidence && (
              <div className={sectionClass}>
                <h2 className="text-xl font-semibold mb-3">🎯 Extraction Confidence</h2>
                <div className="flex flex-wrap items-center gap-4">
                  <span
                    className={`text-3xl font-bold ${
                      result.confidence.score >= 80
                        ? "text-green-500"
                        : result.confidence.score >= 50
                        ? "text-orange-500"
                        : "text-red-500"
                    }`}
                  >
                    {result.confidence.score}%
                  </span>
                  <span className="text-sm opacity-70">
                    Extracted <strong>{result.confidence.extracted}</strong> of{" "}
                    <strong>{result.confidence.expected}</strong> expected{" "}
                    {result.report_type} parameters
                  </span>
                  {result.confidence.missing?.length > 0 && (
                    <span className="text-xs opacity-60 italic">
                      Missing: {result.confidence.missing.join(", ")}
                    </span>
                  )}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mt-3">
                  <div
                    className={`h-3 rounded-full transition-all ${
                      result.confidence.score >= 80
                        ? "bg-green-500"
                        : result.confidence.score >= 50
                        ? "bg-orange-400"
                        : "bg-red-500"
                    }`}
                    style={{ width: `${result.confidence.score}%` }}
                  />
                </div>
              </div>
            )}

            {/* Summary */}
            <div className={sectionClass}>
              <h2 className="text-xl font-semibold mb-4">
                Summary
              </h2>

              <div className="mb-6">
                <div className="flex justify-between mb-2">
                  <span>Health Score</span>
                  <span>{getHealthScore()}%</span>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full ${
                      getHealthScore() >= 80
                        ? "bg-green-500"
                        : getHealthScore() >= 60
                        ? "bg-orange-500"
                        : "bg-red-500"
                    }`}
                    style={{
                      width: `${getHealthScore()}%`,
                    }}
                  />
                </div>
              </div>

              <p>{result.summary}</p>

              <button
                onClick={downloadPDF}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg mt-4"
              >
                📄 Download PDF Report
              </button>
            </div>

            {/* Chart */}
            <div className={panelClass}>
              <h2 className="text-xl font-semibold mb-4">
                Blood Report Visualization
              </h2>

              <div style={{ width: "100%", height: 350 }}>
                <ResponsiveContainer>
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Line Chart */}
            <div className={panelClass}>
              <h2 className="text-xl font-semibold mb-4">
                Trend Visualization
              </h2>

              <div style={{ width: "100%", height: 350 }}>
                <ResponsiveContainer>
                  <LineChart data={chartData}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Analysis Table */}
            <div id="analysis-section" className={sectionClass}>
              <div className="flex flex-wrap justify-between items-center gap-2 mb-4">
                <h2 className="text-xl font-semibold">
                Analysis
                </h2>
                <div className="flex items-center gap-2">
                  <div className="text-sm opacity-70">{getFilteredAnalysisRows().length} shown</div>
                  <button
                    onClick={exportAnalysisCsv}
                    className="text-sm bg-slate-700 hover:bg-slate-800 text-white px-3 py-1 rounded"
                  >
                    Export CSV
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <input
                  type="text"
                  value={analysisSearch}
                  onChange={(e) => setAnalysisSearch(e.target.value)}
                  className={inputClass}
                  placeholder="Search parameter..."
                />
                <select
                  value={analysisStatusFilter}
                  onChange={(e) => setAnalysisStatusFilter(e.target.value)}
                  className={inputClass}
                >
                  <option value="all">All Statuses</option>
                  <option value="abnormal">Abnormal Only</option>
                  <option value="critical">Critical Only</option>
                  <option value="Normal">Normal</option>
                  <option value="High">High</option>
                  <option value="Low">Low</option>
                  <option value="Unknown">Unknown</option>
                </select>
                <select
                  value={analysisSortBy}
                  onChange={(e) => setAnalysisSortBy(e.target.value)}
                  className={inputClass}
                >
                  <option value="severity">Sort by Severity</option>
                  <option value="value">Sort by Value</option>
                  <option value="name">Sort A-Z</option>
                </select>
              </div>

              <div className="hidden md:block">
                <table className="w-full border">
                  <thead>
                    <tr className={tableHeaderClass}>
                      <th className="border p-2">
                        Parameter
                      </th>
                      <th className="border p-2">
                        Value
                      </th>
                      <th className="border p-2">
                        Status
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {getFilteredAnalysisRows().map(
                      (value) => (
                        <tr key={value.name}>
                          <td className="border p-2">
                            {value.name}
                          </td>

                          <td className="border p-2">
                            {value.value}
                          </td>

                          <td className="border p-2">
                            <span
                              className={`px-3 py-1 rounded-full text-white text-sm font-semibold ${
                                value.status === "Normal"
                                  ? "bg-green-500"
                                  : value.status === "Low"
                                  ? "bg-red-500"
                                  : value.status === "High"
                                  ? "bg-orange-500"
                                  : value.status === "Critical Low" || value.status === "Critical High"
                                  ? "bg-red-800 animate-pulse"
                                  : "bg-gray-500"
                              }`}
                            >
                              {value.status}
                            </span>
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>

              <div className="md:hidden space-y-2">
                {getFilteredAnalysisRows().map((value) => (
                  <div key={value.name} className={`rounded-lg border p-3 ${darkMode ? "bg-slate-900/60 border-slate-700" : "bg-white border-slate-200"}`}>
                    <p className="font-semibold mb-1">{value.name}</p>
                    <p className="text-sm mb-2">Value: <strong>{value.value}</strong></p>
                    <span
                      className={`px-3 py-1 rounded-full text-white text-xs font-semibold ${
                        value.status === "Normal"
                          ? "bg-green-500"
                          : value.status === "Low"
                          ? "bg-red-500"
                          : value.status === "High"
                          ? "bg-orange-500"
                          : value.status === "Critical Low" || value.status === "Critical High"
                          ? "bg-red-800"
                          : "bg-gray-500"
                      }`}
                    >
                      {value.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className={sectionClass}>
              <h2 className="text-xl font-semibold mb-4">
                Recommendations
              </h2>

              <ul>
                {result.recommendations?.map((item, index) => (
                  <li
                    key={index}
                    className="mb-2 bg-green-50 border border-green-200 p-3 rounded-lg text-black"
                  >
                    ✓ {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Medical Chat */}
            <div id="chat-section" className={sectionClass}>
              <h2 className="text-xl font-semibold mb-4">
                Ask Medical Question
              </h2>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="What causes iron deficiency?"
                  className={inputClass}
                />

                <button
                  onClick={askMedical}
                  disabled={loadingMedicalAnswer}
                  className="bg-green-600 hover:bg-green-700 text-white px-5 rounded"
                >
                  {loadingMedicalAnswer ? "Thinking..." : "Ask"}
                </button>
              </div>

              {answer && (
                <div className={`mt-6 border p-4 rounded-xl shadow text-black ${
                  doctorMode ? "bg-blue-50 border-blue-300" : "bg-green-50 border-green-200"
                }`}>
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold">Answer</h3>
                    <div className="flex gap-2">
                      <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                        doctorMode ? "bg-blue-700 text-white" : "bg-green-100 text-green-800 border border-green-300"
                      }`}>
                        {doctorMode ? "🩺 Doctor Mode" : "👤 Patient Mode"}
                      </span>
                      {answerModel && (
                        <span className="text-xs bg-blue-100 border border-blue-300 text-blue-700 px-2 py-1 rounded-full">
                          {answerModel === "openrouter" ? "🤖 OpenRouter AI" : answerModel === "gemini" ? "✨ Gemini AI" : "📚 RAG"}
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="whitespace-pre-wrap">{answer}</p>
                </div>
              )}
            </div>

            {/* Report Chat */}
            <div className={sectionClass}>
              <h2 className="text-xl font-semibold mb-4">
                📄 Chat With Uploaded Report
              </h2>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Why is my MCHC low?"
                  className={inputClass}
                />

                <button
                  onClick={askAboutReport}
                  disabled={loadingReportAnswer}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-5 rounded"
                >
                  {loadingReportAnswer ? "Thinking..." : "Ask Report"}
                </button>
              </div>

              {reportAnswer && (
                <div className={`mt-6 border p-4 rounded-xl shadow text-black ${
                  doctorMode ? "bg-blue-50 border-blue-300" : "bg-purple-50 border-purple-200"
                }`}>
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold">Report Answer</h3>
                    <div className="flex gap-2">
                      <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                        doctorMode ? "bg-blue-700 text-white" : "bg-purple-100 text-purple-800 border border-purple-300"
                      }`}>
                        {doctorMode ? "🩺 Doctor Mode" : "👤 Patient Mode"}
                      </span>
                      {reportAnswerModel && (
                        <span className="text-xs bg-purple-100 border border-purple-300 text-purple-700 px-2 py-1 rounded-full">
                          {reportAnswerModel === "openrouter" ? "🤖 OpenRouter AI" : reportAnswerModel === "gemini" ? "✨ Gemini AI" : "📚 RAG"}
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="whitespace-pre-wrap">{reportAnswer}</p>
                </div>
              )}
            </div>

            {/* Chat History */}
            <div className={sectionClass}>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Chat History</h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => loadHistory(reportId)}
                    className="bg-slate-600 hover:bg-slate-700 text-white px-3 py-1 rounded"
                  >
                    Refresh
                  </button>
                  <button
                    onClick={() => clearHistory(reportId)}
                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
                  >
                    Clear
                  </button>
                </div>
              </div>

              {historyItems.length === 0 ? (
                <p className="text-sm opacity-70">No chat history yet.</p>
              ) : (
                <div className="space-y-3 max-h-96 overflow-auto pr-1">
                  {historyItems.map((item) => (
                    <div
                      key={item.id}
                      className="border border-slate-300 dark:border-slate-600 rounded-lg p-3"
                    >
                      <div className="flex justify-between items-center text-xs mb-2 opacity-80">
                        <span>{item.context_type === "report" ? "Report Chat" : "General Chat"}</span>
                        <span>{item.model || "unknown"} · {new Date(item.created_at).toLocaleString()}</span>
                      </div>
                      <p className="font-semibold mb-1">Q: {item.question}</p>
                      <p>A: {item.answer}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Report Comparison */}
            <div id="compare-section" className={sectionClass}>
              <h2 className="text-xl font-semibold mb-4">📊 Compare Reports</h2>
              <div className="flex gap-2 mb-4">
                <select
                  value={compareReportId}
                  onChange={(e) => {
                    setCompareReportId(e.target.value);
                    setCompareData(null);
                  }}
                  className={inputClass}
                >
                  <option value="">Select a previous report to compare...</option>
                  {reportList
                    .filter((r) => r.id !== reportId)
                    .map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.filename} — {r.report_type} — {r.risk_level} —{" "}
                        {new Date(r.created_at).toLocaleDateString()}
                      </option>
                    ))}
                </select>
                <button
                  onClick={loadComparison}
                  disabled={!compareReportId}
                  className="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white px-4 py-2 rounded whitespace-nowrap"
                >
                  Compare
                </button>
                <button
                  onClick={exportComparisonCsv}
                  disabled={!compareData}
                  className="bg-slate-700 hover:bg-slate-800 disabled:opacity-40 text-white px-4 py-2 rounded whitespace-nowrap"
                >
                  Export CSV
                </button>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                <button
                  onClick={() => setCompareFilter("all")}
                  className={`px-3 py-1 rounded-full text-sm ${compareFilter === "all" ? "bg-slate-800 text-white" : "bg-slate-100"}`}
                >
                  All
                </button>
                <button
                  onClick={() => setCompareFilter("changed")}
                  className={`px-3 py-1 rounded-full text-sm ${compareFilter === "changed" ? "bg-amber-600 text-white" : "bg-amber-100 text-amber-800"}`}
                >
                  Changed Only
                </button>
                <button
                  onClick={() => setCompareFilter("abnormal")}
                  className={`px-3 py-1 rounded-full text-sm ${compareFilter === "abnormal" ? "bg-red-600 text-white" : "bg-red-100 text-red-800"}`}
                >
                  Abnormal Only
                </button>
              </div>

              {compareData && (() => {
                const summary = getComparisonSummary();
                return (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4 text-sm">
                    <div className="rounded-lg bg-red-100 text-red-800 border border-red-200 px-3 py-2">
                      Increased: <strong>{summary.increased}</strong>
                    </div>
                    <div className="rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-200 px-3 py-2">
                      Decreased: <strong>{summary.decreased}</strong>
                    </div>
                    <div className="rounded-lg bg-slate-100 text-slate-800 border border-slate-200 px-3 py-2">
                      Unchanged: <strong>{summary.unchanged}</strong>
                    </div>
                  </div>
                );
              })()}

              {compareData && (
                <div>
                  <div className="hidden md:block overflow-x-auto">
                    <table className="w-full border text-sm">
                      <thead>
                        <tr className={tableHeaderClass}>
                          <th className="border p-2 text-left">Parameter</th>
                          <th className="border p-2">
                            Previous ({compareData.filename || compareReportId.slice(0, 8)})
                          </th>
                          <th className="border p-2">Current</th>
                          <th className="border p-2">Change</th>
                        </tr>
                      </thead>
                      <tbody>
                        {getComparisonRows().map(([param, curr]) => {
                          const prev = compareData.analysis?.[param];
                          let arrow = "—";
                          let arrowColor = "text-gray-400";
                          if (prev && curr && curr.value !== null && prev.value !== null) {
                            const diff = parseFloat(curr.value) - parseFloat(prev.value);
                            if (diff > 0) { arrow = "↑"; arrowColor = "text-red-500"; }
                            else if (diff < 0) { arrow = "↓"; arrowColor = "text-green-500"; }
                            else { arrow = "→"; arrowColor = "text-gray-400"; }
                          }
                          return (
                            <tr key={param}>
                              <td className="border p-2 font-medium">{param}</td>
                              <td className="border p-2 text-center">
                                {prev ? `${prev.value} (${prev.status})` : "—"}
                              </td>
                              <td className="border p-2 text-center">
                                {curr.value} ({curr.status})
                              </td>
                              <td className={`border p-2 text-center font-bold text-xl ${arrowColor}`}>
                                {arrow}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  <div className="md:hidden space-y-2">
                    {getComparisonRows().map(([param, curr]) => {
                      const prev = compareData.analysis?.[param];
                      let arrow = "—";
                      let arrowColor = "text-gray-400";
                      if (prev && curr && curr.value !== null && prev.value !== null) {
                        const diff = parseFloat(curr.value) - parseFloat(prev.value);
                        if (diff > 0) { arrow = "↑"; arrowColor = "text-red-500"; }
                        else if (diff < 0) { arrow = "↓"; arrowColor = "text-green-500"; }
                        else { arrow = "→"; arrowColor = "text-gray-400"; }
                      }
                      return (
                        <div key={param} className={`rounded-lg border p-3 ${darkMode ? "bg-slate-900/60 border-slate-700" : "bg-white border-slate-200"}`}>
                          <div className="flex items-center justify-between">
                            <p className="font-semibold">{param}</p>
                            <span className={`font-bold text-xl ${arrowColor}`}>{arrow}</span>
                          </div>
                          <p className="text-sm mt-1">Prev: {prev ? `${prev.value} (${prev.status})` : "—"}</p>
                          <p className="text-sm">Curr: {curr.value} ({curr.status})</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {!compareData && compareReportId && (
                <p className="text-sm opacity-60 mt-2">
                  Click Compare to load the selected report.
                </p>
              )}
              {reportList.filter((r) => r.id !== reportId).length === 0 && (
                <p className="text-sm opacity-60">
                  No previous reports available. Upload more reports to enable comparison.
                </p>
              )}
            </div>

            {/* Report Timeline */}
            <div id="timeline-section" className={sectionClass}>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">🗂 Report Timeline</h2>
                <button
                  onClick={loadReportList}
                  className="bg-slate-600 hover:bg-slate-700 text-white px-3 py-1 rounded"
                >
                  Refresh Timeline
                </button>
              </div>

              {reportList.length === 0 ? (
                <p className="text-sm opacity-70">No reports yet.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {reportList.map((r) => (
                    <div
                      key={r.id}
                      className={`rounded-xl border p-3 transition-shadow ${
                        r.id === reportId
                          ? "border-sky-400 shadow-lg"
                          : darkMode
                          ? "border-slate-700 bg-slate-900/50"
                          : "border-slate-200 bg-white"
                      }`}
                    >
                      <p className="font-semibold truncate" title={r.filename}>{r.filename}</p>
                      <p className="text-xs opacity-70 mt-1">{new Date(r.created_at).toLocaleString()}</p>
                      <div className="mt-2 flex flex-wrap gap-2 text-xs">
                        <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                          {r.report_type || "Unknown"}
                        </span>
                        <span className={`px-2 py-1 rounded-full border ${
                          (r.risk_level || "").includes("High")
                            ? "bg-red-100 text-red-800 border-red-200"
                            : (r.risk_level || "").includes("Moderate")
                            ? "bg-amber-100 text-amber-800 border-amber-200"
                            : "bg-emerald-100 text-emerald-800 border-emerald-200"
                        }`}>
                          {r.risk_level || "No risk"}
                        </span>
                      </div>
                      <button
                        onClick={() => {
                          setCompareReportId(r.id);
                          setCompareData(null);
                          showToast("Report selected for comparison", "info");
                        }}
                        className="mt-3 bg-sky-600 hover:bg-sky-700 text-white px-3 py-1 rounded text-sm"
                        disabled={r.id === reportId}
                      >
                        {r.id === reportId ? "Current Report" : "Select For Compare"}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;