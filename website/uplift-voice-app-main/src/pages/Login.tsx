// frontend/src/pages/Login.tsx
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { postJSON } from "@/lib/api";
import { saveAuthToken, saveUserData } from "@/utils/authUtils";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const res = await postJSON<any>("/api/auth/login", { email, password });

      // Save both token and user data to localStorage using safe utilities
      saveAuthToken(res.token);
      saveUserData(res.user);

      console.log("✅ Login successful, user data saved:", res.user);
      navigate("/dashboard");
    } catch (e: any) {
      setErr(e.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 bg-white rounded-3xl shadow-2xl overflow-hidden" style={{ minHeight: '700px' }}>
        {/* Left side - Full Branding Image */}
        <div
          className="hidden lg:block bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: 'url(/login-bg.png)',
            minHeight: '700px'
          }}
        />

        {/* Right side - Login Form */}
        <div className="flex items-center justify-center p-8 sm:p-12 lg:p-16 bg-white">
          <div className="w-full max-w-md">
            <div className="mb-8 text-center">
              <h2 className="text-3xl font-bold mb-2" style={{ color: '#1A4776' }}>
                Welcome back
              </h2>
            </div>

            <form onSubmit={onSubmit} className="space-y-6">
              <div>
                <Label htmlFor="email" className="text-gray-700 font-medium">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-gray-700 font-medium">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>

              {err && (
                <div className="text-sm bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg">
                  {err}
                </div>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full text-white font-semibold py-6 rounded-lg transition-all"
                style={{ backgroundColor: '#1A4776' }}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Logging in...
                  </>
                ) : (
                  "Log In"
                )}
              </Button>

              <p className="text-sm text-gray-600 text-center mt-6">
                Don&apos;t have an account?{" "}
                <Link to="/signup" className="font-semibold hover:underline" style={{ color: '#1688DF' }}>
                  Create one
                </Link>
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
