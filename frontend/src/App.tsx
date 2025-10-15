import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Header } from '@/components/Header';
import { FileUpload } from '@/components/FileUpload';
import { ExtractionResults } from '@/components/ExtractionResults';
import { QualityMetrics } from '@/components/QualityMetrics';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { uploadDocument } from '@/lib/api';
import type { UploadResponse } from '@/types/api';
import { AlertCircle, Download, ArrowLeft, Loader2 } from 'lucide-react';

function HomePage() {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await uploadDocument(file);
      navigate('/results', { state: { data: response } });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process document');
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
                onFileSelect={handleFileSelect} 
                isProcessing={isProcessing}
              />
              {isProcessing && (
                <div className="mt-4 flex items-center justify-center space-x-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Processing document with AI...</span>
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
  const data = (location.state as { data: UploadResponse })?.data;

  if (!data) {
    navigate('/');
    return null;
  }

  const handleExportJSON = () => {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lease-extraction-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
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
              Upload Another Document
            </Button>
            <Button 
              onClick={handleExportJSON}
              className="gap-2"
            >
              <Download className="h-4 w-4" />
              Export as JSON
            </Button>
          </div>

          {/* Results Grid */}
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <ExtractionResults data={data.extraction} />
            </div>
            <div>
              <QualityMetrics metrics={data.quality_metrics} />
            </div>
          </div>

          {/* AI Model Info */}
          <Card className="bg-muted/50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between text-sm">
                <div>
                  <span className="text-muted-foreground">AI Model:</span>
                  <span className="ml-2 font-medium">{data.extraction.ai_model_used}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Extracted:</span>
                  <span className="ml-2 font-medium">
                    {new Date(data.extraction.extraction_timestamp).toLocaleString('de-DE')}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
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
