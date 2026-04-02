const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? 'http://127.0.0.1:8000/api/v1' : '/api/v1');

async function parseResponse(response) {
  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      payload?.detail ||
      payload?.message ||
      'Request failed. Please check the backend server and try again.';
    throw new Error(message);
  }

  return payload?.data ?? payload;
}

export async function runEvaluation({
  studentName,
  studentId,
  questionPaperTitle,
  questionPaperFile,
  answerSheetFile,
  markingSchemeFile,
}) {
  const formData = new FormData();
  formData.append('student_name', studentName);
  formData.append('student_id', studentId || '');
  formData.append('question_paper_title', questionPaperTitle || '');
  formData.append('question_paper', questionPaperFile);
  formData.append('answer_sheet', answerSheetFile);

  if (markingSchemeFile) {
    formData.append('marking_scheme', markingSchemeFile);
  }

  const response = await fetch(`${API_BASE_URL}/evaluations/run`, {
    method: 'POST',
    body: formData,
  });

  return parseResponse(response);
}

export async function getBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return parseResponse(response);
}
