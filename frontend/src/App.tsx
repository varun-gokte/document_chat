import { useState } from "react";
import FileUpload from "./components/FileUpload";
import DocumentChat from "./components/DocumentChat";

export default function App() {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  return (
    <div className="w-screen h-screen">
      {pdfUrl ? (
        <DocumentChat pdfUrl={pdfUrl} />
      ) : (
        <FileUpload onUploadSuccess={(file) => setPdfUrl(URL.createObjectURL(file))} />
      )}
    </div>
  );
}
