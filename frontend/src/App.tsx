import { useState } from "react";
import FileUpload from "./components/FileUpload";
import DocumentChat from "./components/DocumentChat";

export default function App() {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);

 return (
    <div className="flex flex-col min-h-screen w-screen">
      {/* Main content */}
      <div className="flex-grow bg-gray-100">
        {pdfUrl ? (
          <DocumentChat pdfUrl={pdfUrl||""} documentId={documentId} />
        ) : (
          <FileUpload
            onUploadSuccess={(id, file) => {
              setDocumentId(id);
              setPdfUrl(URL.createObjectURL(file));
            }}
          />
        )}
      </div>

    </div>
  );
}