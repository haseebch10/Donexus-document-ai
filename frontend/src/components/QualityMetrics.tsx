import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import type { QualityMetrics as QualityMetricsType } from '@/types/api';

interface QualityMetricsProps {
  metrics: QualityMetricsType;
}

export function QualityMetrics({ metrics }: QualityMetricsProps) {
  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQualityIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="h-5 w-5 text-green-600" />;
    if (score >= 60) return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  const getQualityLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Poor';
  };

  const overallScore = metrics.overall_score;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Extraction Quality Score</CardTitle>
            <CardDescription>AI-powered quality assessment</CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            {getQualityIcon(overallScore)}
            <span className={`text-2xl font-bold ${getQualityColor(overallScore)}`}>
              {overallScore.toFixed(1)}%
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Quality Badge */}
        <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
          <span className="font-medium">Quality Rating:</span>
          <Badge 
            variant={overallScore >= 80 ? "default" : overallScore >= 60 ? "secondary" : "destructive"}
            className="text-sm px-3 py-1"
          >
            {getQualityLabel(overallScore)}
          </Badge>
        </div>

        {/* Individual Metrics */}
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Confidence</span>
              <span className="text-muted-foreground">
                {(metrics.confidence_score * 100).toFixed(1)}%
              </span>
            </div>
            <Progress value={metrics.confidence_score * 100} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Completeness</span>
              <span className="text-muted-foreground">
                {metrics.completeness_score.toFixed(1)}%
              </span>
            </div>
            <Progress value={metrics.completeness_score} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Validation</span>
              <span className="text-muted-foreground">
                {metrics.validation_score.toFixed(1)}%
              </span>
            </div>
            <Progress value={metrics.validation_score} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Consistency</span>
              <span className="text-muted-foreground">
                {metrics.consistency_score.toFixed(1)}%
              </span>
            </div>
            <Progress value={metrics.consistency_score} className="h-2" />
          </div>
        </div>

        {/* Warnings and Errors */}
        {(metrics.warnings.length > 0 || metrics.validation_errors.length > 0) && (
          <div className="space-y-3 pt-4 border-t">
            {metrics.validation_errors.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-destructive flex items-center">
                  <XCircle className="h-4 w-4 mr-2" />
                  Errors ({metrics.validation_errors.length})
                </h4>
                <ul className="space-y-1">
                  {metrics.validation_errors.map((error, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-6">
                      • {error}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {metrics.warnings.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-yellow-600 flex items-center">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Warnings ({metrics.warnings.length})
                </h4>
                <ul className="space-y-1">
                  {metrics.warnings.map((warning, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground pl-6">
                      • {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
