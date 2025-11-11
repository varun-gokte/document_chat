import { useState } from "react";
import FileUpload from "./components/FileUpload";
import DocumentChat from "./components/DocumentChat";
import Footer from "./components/Footer";

export default function App() {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

 return (
    <div className="flex flex-col min-h-screen w-screen">
      {/* Main content */}
      <div className="flex-grow bg-gray-100">
        {pdfUrl ? (
          <DocumentChat pdfUrl={pdfUrl||""} />
        ) : (
          <FileUpload onUploadSuccess={(file) => setPdfUrl(URL.createObjectURL(file))} />
        )}
      </div>

      {/* Sticky footer */}
      <Footer />
    </div>
  );
}