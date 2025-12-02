import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ReportForm } from "@/components/report/ReportForm";

const Report = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 py-12 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl md:text-4xl font-bold mb-4">Submit a Report</h1>
              <p className="text-lg text-muted-foreground">
                Help improve your community by reporting road issues
              </p>
            </div>
            
            <ReportForm />
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Report;
