import { useCallback, useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing?: boolean;
}

export function FileUpload({ onFileSelect, isProcessing }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const handleRemoveFile = useCallback(() => {
    setSelectedFile(null);
  }, []);

  return (
    <Card
      className={cn(
        "relative border-2 border-dashed transition-colors",
        isDragging && "border-primary bg-primary/5",
        isProcessing && "opacity-60 pointer-events-none"
      )}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <div className="p-12">
        {!selectedFile ? (
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="rounded-full bg-primary/10 p-6">
              <Upload className="h-10 w-10 text-primary" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Upload Lease Document</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Drag and drop your PDF lease document here, or click to browse
              </p>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <Button
                onClick={() => document.getElementById('file-input')?.click()}
                disabled={isProcessing}
              >
                <Upload className="mr-2 h-4 w-4" />
                Select PDF File
              </Button>
              <p className="text-xs text-muted-foreground">
                Supported format: PDF (max 10MB)
              </p>
            </div>
            <input
              id="file-input"
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={handleFileInput}
              disabled={isProcessing}
            />
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="rounded-lg bg-primary/10 p-3">
                <FileText className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            {!isProcessing && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRemoveFile}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
