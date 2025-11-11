import { useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import SendIcon from "@mui/icons-material/Send";
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import { askQuestion } from "../apis";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.js",
  import.meta.url
).toString();

interface Props {
  pdfUrl: string;
}

export default function DocumentChat({ pdfUrl }: Props) {
  const [numPages, setNumPages] = useState<number>(0);

  const [messages, setMessages] = useState<
    { role: "user" | "bot"; text: string }[]
  >([]);
  const [input, setInput] = useState("");
  const pageRefs = useRef<(HTMLDivElement|null)[]>([]);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const onDocumentLoad = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };
  console.log(pageRefs)

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { role: "user" as const, text: input };
    setMessages((prev) => [...prev, userMessage]);

    // Add temporary "Thinking..." message
    setMessages((prev) => [...prev, { role: "bot", text: "Thinking..." }]);

    const userInput = input;
    setInput("");

    try {
      const response = await askQuestion(userInput, pdfUrl);

      const { answer, sources } = response;

      // Scroll or jump to first source page
      if (sources && sources.length > 0) {
        const targetPage = sources[0].page - 1; // 0-indexed
        const pageEl = pageRefs.current[targetPage];
        if (pageEl) {
          if (containerRef.current && pageEl) {
          // Scroll container to page element
          const container = containerRef.current;
          const topPos = pageEl.offsetTop;
          container.scrollTo({
            top: topPos,
            behavior: "smooth",
          });
        }
        }
      }

      // Replace "Thinking..." with answer
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "bot", text: answer };
        return updated;
      });
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "bot", text: "⚠️ Error responding" };
        return updated;
      });
    }
  };

  return (
    <div className="h-[calc(100vh-65px)] flex items-center justify-center bg-gray-100 border">
      <div
        className="w-1/2 h-full overflow-auto bg-white border-r"
        id="pdf-container"
        ref={containerRef}
      >
        <Document file={pdfUrl} onLoadSuccess={onDocumentLoad}>
          {Array.from({ length: numPages }, (_, i) => (
            <div
              key={i}
              ref={(el) => void (pageRefs.current[i] = el)}
              className="mb-2"
            >
              <Page
                pageNumber={i + 1}
                width={600}
                renderTextLayer={false}
                renderAnnotationLayer={false}
              />
            </div>
          ))}
        </Document>
      </div>


      <div className="w-1/2 h-full flex flex-col p-4">
        <div className="flex-1 overflow-y-auto space-y-3 border rounded-lg p-4 bg-white">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[80%] px-3 py-2 rounded-lg ${
                m.role === "user"
                  ? "bg-blue-500 text-white self-end ml-auto"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {m.text}
            </div>
          ))}
        </div>

        <div className="mt-4 flex items-center gap-2">
          <TextField
            fullWidth
            size="small"
            placeholder="Ask something about the document..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <IconButton color="primary" onClick={sendMessage}>
            <SendIcon />
          </IconButton>
        </div>
      </div>
    </div>
  );
}
