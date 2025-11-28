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
        <h3 className="text-lg font-semibold">{title}</h3>
      </CardHeader>
      <CardContent>
        <p>{description}</p>
        <div className="flex items-center gap-2 mt-2">
          <MapPin className="w-4 h-4 text-gray-500" />
          <span>{location}</span>
        </div>
        <div className="flex items-center gap-2 mt-2">
          <Calendar className="w-4 h-4 text-gray-500" />
          <span>{date}</span>
        </div>
      </CardContent>
      <CardFooter>
        <Badge variant={variant}>{label}</Badge>
      </CardFooter>
    </Card>
  );
};
