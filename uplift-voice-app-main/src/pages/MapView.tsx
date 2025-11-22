import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Calendar } from "lucide-react";
import { getPriorityBorderColor } from "@/utils/priorityColors";

const MapView = () => {
  // Mock data for reported issues
  const reportedIssues = [
    {
      id: 1,
      title: "Large pothole on Main Street",
      location: "Main Street & Oak Avenue",
      date: "2024-03-15",
      status: "verified",
      priority: "critical",
      coordinates: { lat: 40.7128, lng: -74.0060 },
    },
    {
      id: 2,
      title: "Broken traffic light",
      location: "5th Street & Park Avenue",
      date: "2024-03-14",
      status: "under-review",
      priority: "medium",
      coordinates: { lat: 40.7580, lng: -73.9855 },
    },
    {
      id: 3,
      title: "Damaged road sign",
      location: "Elm Street",
      date: "2024-03-13",
      status: "resolved",
      priority: "low",
      coordinates: { lat: 40.7589, lng: -73.9851 },
    },
  ];

  const statusConfig = {
    pending: { label: "Pending", color: "bg-muted" },
    "under-review": { label: "Under Review", color: "bg-primary" },
    verified: { label: "Verified", color: "bg-primary" },
    rejected: { label: "Rejected", color: "bg-destructive" },
    resolved: { label: "Resolved", color: "bg-success" },
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 py-12">
        <div className="container mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold mb-4">Issue Map View</h1>
            <p className="text-lg text-muted-foreground">
              Visualize all reported issues in your area
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Map Container */}
            <div className="lg:col-span-2">
              <Card className="h-[600px]">
                <CardContent className="p-0 h-full">
                  <div className="w-full h-full bg-muted rounded-lg flex items-center justify-center">
                    <div className="text-center space-y-4 p-8">
                      <MapPin className="h-16 w-16 text-primary mx-auto" />
                      <div>
                        <h3 className="text-xl font-semibold mb-2">Interactive Map</h3>
                        <p className="text-muted-foreground">
                          Map integration would display all reported issues with markers
                        </p>
                        <p className="text-sm text-muted-foreground mt-4">
                          Click on markers to view report details and status
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Issue List */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Reports</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {reportedIssues.map((issue) => (
                    <div
                      key={issue.id}
                      className={`p-4 rounded-lg border-2 ${getPriorityBorderColor(issue.priority)} hover:border-primary transition-colors cursor-pointer`}
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <MapPin className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium mb-1 line-clamp-2">{issue.title}</h4>
                          <p className="text-sm text-muted-foreground line-clamp-1">
                            {issue.location}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="h-4 w-4" />
                          {issue.date}
                        </div>
                        <Badge
                          variant={
                            issue.status === "resolved"
                              ? "default"
                              : issue.status === "rejected"
                              ? "destructive"
                              : "secondary"
                          }
                        >
                          {statusConfig[issue.status as keyof typeof statusConfig].label}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Legend</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {Object.entries(statusConfig).map(([key, value]) => (
                    <div key={key} className="flex items-center gap-3">
                      <div className={`h-4 w-4 rounded-full ${value.color}`} />
                      <span className="text-sm">{value.label}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default MapView;
