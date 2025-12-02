import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X, AlertCircle } from "lucide-react";
import { useState } from "react";

export const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2">
          <AlertCircle className="h-7 w-7 text-primary" />
          <span className="text-xl font-bold text-foreground">Voice Up</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          <Link
            to="/"
            className={`text-sm font-medium transition-colors hover:text-primary ${
              isActive("/") ? "text-primary" : "text-foreground/80"
            }`}
          >
            Home
          </Link>
          <Link
            to="/report"
            className={`text-sm font-medium transition-colors hover:text-primary ${
              isActive("/report") ? "text-primary" : "text-foreground/80"
            }`}
          >
            Report Issue
          </Link>
          <Link
            to="/reports"
            className={`text-sm font-medium transition-colors hover:text-primary ${
              isActive("/reports") ? "text-primary" : "text-foreground/80"
            }`}
          >
            My Reports
          </Link>
          <Link
            to="/map"
            className={`text-sm font-medium transition-colors hover:text-primary ${
              isActive("/map") ? "text-primary" : "text-foreground/80"
            }`}
          >
            Map View
          </Link>
        </div>

        <div className="hidden md:flex items-center gap-4">
          <Link to="/profile">
            <Button variant="ghost">Profile</Button>
          </Link>
          <Link to="/report">
            <Button>Submit Report</Button>
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle menu"
        >
          {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden border-t bg-background">
          <div className="container mx-auto px-4 py-4 flex flex-col gap-4">
            <Link
              to="/"
              className="text-sm font-medium text-foreground/80 hover:text-primary"
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              to="/report"
              className="text-sm font-medium text-foreground/80 hover:text-primary"
              onClick={() => setIsMenuOpen(false)}
            >
              Report Issue
            </Link>
            <Link
              to="/reports"
              className="text-sm font-medium text-foreground/80 hover:text-primary"
              onClick={() => setIsMenuOpen(false)}
            >
              My Reports
            </Link>
            <Link
              to="/map"
              className="text-sm font-medium text-foreground/80 hover:text-primary"
              onClick={() => setIsMenuOpen(false)}
            >
              Map View
            </Link>
            <Link
              to="/profile"
              className="text-sm font-medium text-foreground/80 hover:text-primary"
              onClick={() => setIsMenuOpen(false)}
            >
              Profile
            </Link>
            <Link to="/report" onClick={() => setIsMenuOpen(false)}>
              <Button className="w-full">Submit Report</Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
