import { AlertTriangle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface StrikeIndicatorProps {
  strikes: number;
  maxStrikes?: number;
}

export const StrikeIndicator = ({ strikes, maxStrikes = 3 }: StrikeIndicatorProps) => {
  const getStatusColor = () => {
    if (strikes === 0) return "text-success";
    if (strikes >= maxStrikes) return "text-destructive";
    return "text-warning";
  };

  const getStatusText = () => {
    if (strikes === 0) return "Good Standing";
    if (strikes >= maxStrikes) return "Account Restricted";
    return "Warning Status";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className={`h-5 w-5 ${getStatusColor()}`} />
          Account Status
        </CardTitle>
        <CardDescription>
          Strike system helps maintain quality reports
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Current Strikes</span>
            <Badge variant={strikes === 0 ? "default" : strikes >= maxStrikes ? "destructive" : "secondary"}>
              {strikes} / {maxStrikes}
            </Badge>
          </div>

          <div className="flex gap-2">
            {Array.from({ length: maxStrikes }).map((_, index) => (
              <div
                key={index}
                className={`h-2 flex-1 rounded-full ${
                  index < strikes ? "bg-destructive" : "bg-muted"
                }`}
              />
            ))}
          </div>

          <div className={`text-sm font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </div>

          <div className="text-sm text-muted-foreground space-y-2">
            <p className="font-medium text-foreground">Strike Reasons:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Uploading irrelevant images</li>
              <li>Submitting abusive content</li>
              <li>Posting AI-generated or manipulated images</li>
              <li>Multiple rejected reports</li>
            </ul>
          </div>

          {strikes >= maxStrikes && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 text-sm text-destructive">
              Your account is restricted. Please contact support to review your case.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
