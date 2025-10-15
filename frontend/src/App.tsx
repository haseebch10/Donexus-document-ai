import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Header } from '@/components/Header';
import { FileUpload } from '@/components/FileUpload';
import { ExtractionResults } from '@/components/ExtractionResults';
import { QualityMetrics } from '@/components/QualityMetrics';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { uploadDocuments } from '@/lib/api';
import { exportToJSON, exportToExcel, exportAllToJSON, exportAllToExcel } from '@/lib/export';
import type { BatchUploadResult } from '@/types/api';
import { AlertCircle, Download, ArrowLeft, Loader2, X, FileText, Upload, ChevronDown, FileJson, FileSpreadsheet } from 'lucide-react';

function HomePage() {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFilesSelect = (files: File[]) => {
    setSelectedFiles(files);
    setError(null);
  };

  const handleProcessDocuments = async () => {
    if (selectedFiles.length === 0) return;
    
    setIsProcessing(true);
    setError(null);

    try {
      const response = await uploadDocuments(selectedFiles);
      
      // Handle partial failures
      if (response.failed > 0 && response.results.length > 0) {
        const errorMsg = `Warning: ${response.failed} of ${response.total_files} file(s) failed to process. Successfully processed ${response.results.length} file(s).`;
        setError(errorMsg);
        // Still navigate to show successful results
        navigate('/results', { state: { results: response.results, hasErrors: true } });
      } else if (response.results.length > 0) {
        // All successful
        navigate('/results', { state: { results: response.results, hasErrors: false } });
      } else if (response.failed > 0) {
        // All failed
        const errorDetails = response.errors?.map(e => `• ${e.original_filename}: ${e.error}`).join('\n') || 'Unknown error';
        setError(`All files failed to process:\n${errorDetails}`);
      }
    } catch (err) {
      // Network or unexpected errors
      let errorMessage = 'Failed to process documents. ';
      if (err instanceof Error) {
        if (err.message.includes('Network')) {
          errorMessage += 'Please check your internet connection and that the backend server is running.';
        } else if (err.message.includes('413')) {
          errorMessage += 'One or more files exceed the 10MB size limit.';
        } else {
          errorMessage += err.message;
        }
      } else {
        errorMessage += 'Please try again.';
      }
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      <Header />
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-4">
            <h2 className="text-4xl font-bold tracking-tight">
              Extract Lease Data with AI
            </h2>
            <p className="text-xl text-muted-foreground">
              Upload a German lease agreement (Mietvertrag) and let our AI extract all the important information instantly
            </p>
          </div>

          {/* Upload Card */}
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Upload Document</CardTitle>
              <CardDescription>
                Supported format: PDF • Maximum size: 10MB
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileUpload 
                onFilesSelect={handleFilesSelect} 
                isProcessing={isProcessing}
                maxFiles={3}
              />
              {selectedFiles.length > 0 && !isProcessing && (
                <div className="mt-6 flex justify-center">
                  <Button 
                    onClick={handleProcessDocuments}
                    size="lg"
                    className="w-full max-w-md"
                  >
                    <Upload className="mr-2 h-5 w-5" />
                    Process {selectedFiles.length} Document{selectedFiles.length > 1 ? 's' : ''} with AI
                  </Button>
                </div>
              )}
              {isProcessing && (
                <div className="mt-4 flex items-center justify-center space-x-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Processing documents with AI...</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 pt-8">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">🎯 High Accuracy</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Advanced AI models ensure precise extraction of all lease details
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">⚡ Instant Results</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Get structured data in seconds, not hours of manual work
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">✅ Quality Scored</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Every extraction includes comprehensive quality metrics
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const results = (location.state as { results: BatchUploadResult[] })?.results;
  const [activeTab, setActiveTab] = useState('0');
  const [openTabs, setOpenTabs] = useState<BatchUploadResult[]>(results || []);

  if (!results || results.length === 0) {
    navigate('/');
    return null;
  }

  const handleCloseTab = (index: number) => {
    const newTabs = openTabs.filter((_, i) => i !== index);
    setOpenTabs(newTabs);
    
    if (newTabs.length === 0) {
      navigate('/');
    } else if (parseInt(activeTab) >= newTabs.length) {
      setActiveTab(String(newTabs.length - 1));
    }
  };

  const currentResult = openTabs[parseInt(activeTab)];

  const truncateFilename = (filename: string, maxLength = 20) => {
    if (filename.length <= maxLength) return filename;
    const ext = filename.split('.').pop();
    const nameWithoutExt = filename.slice(0, filename.lastIndexOf('.'));
    const truncatedName = nameWithoutExt.slice(0, maxLength - ext!.length - 4) + '...';
    return `${truncatedName}.${ext}`;
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Action Bar */}
          <div className="flex items-center justify-between">
            <Button 
              variant="outline" 
              onClick={() => navigate('/')}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Upload More Documents
            </Button>
            <div className="flex gap-2">
              {/* Export All Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="gap-2">
                    <Download className="h-4 w-4" />
                    Export All
                    <ChevronDown className="h-4 w-4 ml-1" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => exportAllToJSON(openTabs)}>
                    <FileJson className="mr-2 h-4 w-4" />
                    Export as JSON
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => exportAllToExcel(openTabs)}>
                    <FileSpreadsheet className="mr-2 h-4 w-4" />
                    Export as Excel
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Export Current Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button className="gap-2">
                    <Download className="h-4 w-4" />
                    Export Current
                    <ChevronDown className="h-4 w-4 ml-1" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => currentResult && exportToJSON(currentResult)}>
                    <FileJson className="mr-2 h-4 w-4" />
                    Export as JSON
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => currentResult && exportToExcel(currentResult)}>
                    <FileSpreadsheet className="mr-2 h-4 w-4" />
                    Export as Excel
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="relative border-b">
              <TabsList className="h-auto bg-transparent p-0 w-full justify-start">
                {openTabs.map((result, index) => (
                  <div key={index} className="relative group inline-flex items-center">
                    <TabsTrigger 
                      value={String(index)}
                      className="relative rounded-b-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-muted/50 px-4 py-2.5 pr-2 gap-2"
                    >
                      <FileText className="h-4 w-4" />
                      <span className="text-sm font-medium">
                        {truncateFilename(result.original_filename)}
                      </span>
                    </TabsTrigger>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCloseTab(index);
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 z-10"
                      aria-label={`Close ${result.original_filename}`}
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </TabsList>
            </div>

            {openTabs.map((result, index) => (
              <TabsContent key={index} value={String(index)} className="mt-6">
                <div className="grid lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 space-y-6">
                    <ExtractionResults data={result.extraction} />
                  </div>
                  <div>
                    <QualityMetrics metrics={result.quality_metrics} />
                  </div>
                </div>

                {/* AI Model Info */}
                <Card className="bg-muted/50 mt-6">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between text-sm">
                      <div>
                        <span className="text-muted-foreground">AI Model:</span>
                        <span className="ml-2 font-medium">{result.extraction.ai_model_used}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Extracted:</span>
                        <span className="ml-2 font-medium">
                          {new Date(result.extraction.extraction_timestamp).toLocaleString('de-DE')}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Processing Time:</span>
                        <span className="ml-2 font-medium">
                          {result.processing_time_seconds.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </Router>
  );
}
