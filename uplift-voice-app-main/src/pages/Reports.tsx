import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ReportCard } from "@/components/report/ReportCard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Reports = () => {
  // Mock data - would come from API/database
  const mockReports = [
    {
      id: "1",
      title: "Large pothole on Main Street",
      description: "Deep pothole causing traffic hazards near the intersection with Oak Avenue. Approximately 2 feet wide and 6 inches deep.",
      location: "Main Street & Oak Avenue",
      date: "2024-03-15",
      status: "verified" as const,
      priority: "critical",
      image: "https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=800",
    },
    {
      id: "2",
      title: "Broken traffic light",
      description: "Traffic signal not functioning at busy intersection, causing confusion and safety concerns.",
      location: "5th Street & Park Avenue",
      date: "2024-03-14",
      status: "under-review" as const,
      priority: "medium",
      image: "https://images.unsplash.com/photo-1580979018577-7049782d6595?w=800",
    },
    {
      id: "3",
      title: "Damaged road sign",
      description: "Stop sign completely bent and unreadable after accident.",
      location: "Elm Street",
      date: "2024-03-13",
      status: "resolved" as const,
      priority: "low",
      image: "https://images.unsplash.com/photo-1620800259021-93b1bfbc0e2c?w=800",
    },
    {
      id: "4",
      title: "Cracked pavement",
      description: "Large cracks forming across the roadway, potential for expansion.",
      location: "Washington Boulevard",
      date: "2024-03-12",
      status: "pending" as const,
      priority: "medium",
    },
  ];

  const filterReports = (status?: string) => {
    if (!status) return mockReports;
    return mockReports.filter((report) => report.status === status);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 py-12">
        <div className="container mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold mb-4">My Reports</h1>
            <p className="text-lg text-muted-foreground">
              Track the status of your submitted reports
            </p>
          </div>

          <Tabs defaultValue="all" className="space-y-6">
            <TabsList>
              <TabsTrigger value="all">All Reports</TabsTrigger>
              <TabsTrigger value="pending">Pending</TabsTrigger>
              <TabsTrigger value="verified">Verified</TabsTrigger>
              <TabsTrigger value="resolved">Resolved</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-6">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {mockReports.map((report) => (
                  <ReportCard key={report.id} {...report} />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="pending" className="space-y-6">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filterReports("pending").map((report) => (
                  <ReportCard key={report.id} {...report} />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="verified" className="space-y-6">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filterReports("verified").map((report) => (
                  <ReportCard key={report.id} {...report} />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="resolved" className="space-y-6">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filterReports("resolved").map((report) => (
                  <ReportCard key={report.id} {...report} />
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Reports;
