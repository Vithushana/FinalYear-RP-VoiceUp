import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Calendar, MapPin } from "lucide-react";
import { getPriorityBorderColor } from "@/utils/priorityColors";

interface ReportCardProps {
  id: string;
  title: string;
  description: string;
  location: string;
  date: string;
  status: "pending" | "under-review" | "verified" | "rejected" | "resolved";
  priority?: string;
  image?: string;
}

const statusConfig = {
  pending: { label: "Pending Review", variant: "secondary" as const },
  "under-review": { label: "Under Review", variant: "default" as const },
  verified: { label: "Verified", variant: "default" as const },
  rejected: { label: "Rejected", variant: "destructive" as const },
  resolved: { label: "Resolved", variant: "default" as const },
};

export const ReportCard = ({
  title,
  description,
  location,
  date,
  status,
  priority,
  image,
}: ReportCardProps) => {
  const { label, variant } = statusConfig[status];

  return (
    <Card className={`overflow-hidden hover:shadow-medium transition-smooth border-2 ${getPriorityBorderColor(priority || 'low')}`}>
      {image && (
        <div className="aspect-video w-full overflow-hidden bg-muted">
          <img
            src={image}
            alt={title}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-lg line-clamp-2">{title}</h3>
          <Badge variant={variant}>{label}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
          {description}
        </p>
        <div className="flex flex-col gap-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            <span className="line-clamp-1">{location}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>{date}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
