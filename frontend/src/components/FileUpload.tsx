import { useState, type ChangeEvent, type FormEvent, type DragEvent } from "react";
import { Card, Button, Typography } from "@mui/material";
import { uploadFile } from "../apis";

interface FileUploadFormProps {
  onUploadSuccess: (file: File) => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>("");

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setMessage("");
    }
  };

  const handleDrop = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      setFile(droppedFile);
      setFileName(droppedFile.name);
      setMessage("");
    }
  };

  const handleDragOver = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setMessage("");

    try {
      const result = await uploadFile(file);
      console.log("results", result);

      // ✅ Instead of resetting, notify parent we are ready to move to chat UI
      onUploadSuccess(file);
      
    } catch (err) {
      setMessage("Upload failed. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-gray-100">
      <Card className="p-8 shadow-xl flex flex-col items-center gap-4 w-[400px]">
        <Typography variant="h6" className="font-semibold">
          Upload a File
        </Typography>

        <form onSubmit={handleSubmit} className="flex flex-col w-full gap-4">
          <label
            htmlFor="file-upload"
            className="border-2 border-dashed border-gray-400 rounded-lg p-6 w-full text-center cursor-pointer hover:border-blue-500 transition"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <Typography className="text-gray-600">
              {fileName ? fileName : "Drag and drop a file here, or click to select"}
            </Typography>

            <input
              id="file-upload"
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>

          <Button type="submit" variant="contained" disabled={!file || loading} className="w-full">
            {loading ? "Uploading..." : "Upload"}
          </Button>
        </form>

        {message && (
          <Typography className={`text-sm ${message.includes("success") ? "text-green-600" : "text-red-600"}`}>
            {message}
          </Typography>
        )}
      </Card>
    </div>
  );
}
