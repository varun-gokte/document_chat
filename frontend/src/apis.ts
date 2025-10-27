const BASE_URL = "http://localhost:8000";
export async function uploadFile(file: File): Promise<any> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload file");
  }

  return response.json(); 
}

export interface AskResponse {
  answer: string;
  sources: { page: number; start: number; end: number }[];
}

export async function askQuestion(
  question: string,
  pdfUrl: string
): Promise<AskResponse> {
  const response = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, pdfUrl }),
  });

  if (!response.ok) {
    throw new Error("Failed to get response from backend");
  }

  const data = await response.json();

  // Ensure sources array exists
  return {
    answer: data.answer,
    sources: data.sources || [],
  };
}

