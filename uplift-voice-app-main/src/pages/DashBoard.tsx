import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Shield, CheckCircle2, AlertCircle, MapPin, Camera, TrendingUp } from "lucide-react";

const Index = () => {
  const features = [
    {
      icon: Camera,
      title: "Easy Reporting",
      description: "Upload photos and descriptions of road issues in seconds",
    },
    {
      icon: Shield,
      title: "AI Verification",
      description: "Advanced AI checks authenticity and filters inappropriate content",
    },
    {
      icon: CheckCircle2,
      title: "Relevance Check",
      description: "Ensures reports are about actual infrastructure issues",
    },
    {
      icon: MapPin,
      title: "Location Tracking",
      description: "View all reported issues on an interactive map",
    },
  ];

  const stats = [
    { value: "10,000+", label: "Reports Submitted" },
    { value: "8,500+", label: "Issues Resolved" },
    { value: "50+", label: "Cities Covered" },
    { value: "95%", label: "Accuracy Rate" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      {/* Hero Section */}
      <section className="gradient-hero py-20 md:py-32 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center space-y-8">
            <h1 className="text-4xl md:text-6xl font-bold leading-tight">
              Make Your Voice Heard
            </h1>
            <p className="text-xl md:text-2xl text-white/90">
              Report road issues and infrastructure problems directly to authorities with AI-powered verification
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/report">
                <Button size="lg" variant="secondary" className="w-full sm:w-auto">
                  Submit a Report
                </Button>
              </Link>
              <Link to="/map">
                <Button size="lg" variant="outline" className="w-full sm:w-auto bg-white/10 hover:bg-white/20 text-white border-white/30">
                  View Map
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-muted/30 border-y">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-primary mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How Voice Up Works</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Our AI-powered platform ensures only genuine, relevant reports reach the authorities
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="gradient-card shadow-soft hover:shadow-medium transition-smooth">
                <CardHeader>
                  <feature.icon className="h-12 w-12 text-primary mb-4" />
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* AI Verification Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">AI-Powered Verification</h2>
              <p className="text-lg text-muted-foreground">
                Multi-layer verification ensures report quality and authenticity
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <AlertCircle className="h-10 w-10 text-primary mb-4" />
                  <CardTitle>Relevance Check</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>✓ Verifies photos show actual road issues</p>
                  <p>✓ Rejects irrelevant content (selfies, memes)</p>
                  <p>✓ Ensures focus on infrastructure problems</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <Shield className="h-10 w-10 text-primary mb-4" />
                  <CardTitle>Abuse Filtration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>✓ Detects inappropriate content</p>
                  <p>✓ Filters offensive language</p>
                  <p>✓ Protects against misuse</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CheckCircle2 className="h-10 w-10 text-primary mb-4" />
                  <CardTitle>Image Authenticity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>✓ Detects AI-generated images</p>
                  <p>✓ Identifies manipulated photos</p>
                  <p>✓ Ensures genuine evidence</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <TrendingUp className="h-10 w-10 text-primary mb-4" />
                  <CardTitle>Text Verification</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>✓ Analyzes description authenticity</p>
                  <p>✓ Detects AI-written content</p>
                  <p>✓ Validates genuine reports</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <Card className="gradient-hero text-white border-0">
            <CardContent className="py-12 text-center space-y-6">
              <h2 className="text-3xl md:text-4xl font-bold">
                Ready to Make a Difference?
              </h2>
              <p className="text-xl text-white/90 max-w-2xl mx-auto">
                Join thousands of citizens helping improve road infrastructure in their communities
              </p>
              <Link to="/report">
                <Button size="lg" variant="secondary">
                  Submit Your First Report
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;
