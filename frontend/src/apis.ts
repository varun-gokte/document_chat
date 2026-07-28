const BASE_URL = "https://document-chat-hduw.onrender.com/";

export async function uploadFile(file: File) {
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
  documentId: string | null,
  history: { role: "user" | "bot"; text: string }[] = []
): Promise<AskResponse> {
  const response = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, document_id: documentId, history }),
  });

  if (!response.ok) {
    throw new Error("Failed to get response from backend");
  }

  const data = await response.json();

  return {
    answer: data.answer,
    sources: data.sources || [],
  };
}