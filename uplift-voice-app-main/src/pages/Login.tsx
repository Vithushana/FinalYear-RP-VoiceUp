// frontend/src/pages/Login.tsx
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, LogIn } from "lucide-react";
import { postJSON } from "@/lib/api";

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
      const res = await postJSON<{ ok: boolean; token: string; user: any }>("/api/auth/login", { email, password });
      localStorage.setItem("auth_token", res.token);
      navigate("/dashboard");
    } catch (e: any) {
      setErr(e.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-5xl grid lg:grid-cols-2 rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
        {/* Left (branding) */}
        <div className="hidden lg:flex flex-col items-center justify-center p-12 text-center">
          <img src="/mic.png" alt="Voice Up" className="mb-4 w-20 h-20" />
          <h1 className="text-5xl font-extrabold tracking-tighter mb-4 bg-clip-text text-transparent bg-gradient-to-r from-[#1A4776] to-[#1688DF]">
            VOICE UP
          </h1>
          <p className="text-xl max-w-xl leading-relaxed bg-clip-text text-transparent bg-gradient-to-r from-[#1A4776] to-[#1688DF]">
            Welcome back — let’s get you to your dashboard.
          </p>
          <div className="flex items-center justify-center w-full">
            <img src="/img.png" alt="Voice Up" className="mx-auto w-100 max-w-full h-auto object-contain" />
          </div>
        </div>

        {/* Right (form) */}
        <div className="p-8 sm:p-12 lg:p-16">
          <form onSubmit={onSubmit} className="space-y-6 max-w-md mx-auto">
            <div className="flex items-center justify-center gap-2 mb-2">
              <LogIn className="h-6 w-6 text-[#1A4776]" />
              <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#1A4776] to-[#1688DF]">
                Log in
              </h2>
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>

            <div>
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>

            {err && <div className="text-sm bg-red-100 text-red-700 p-2 rounded">{err}</div>}

            <Button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-[#1A4776] to-[#1688DF] text-white">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Signing in…
                </>
              ) : (
                "Log In"
              )}
            </Button>

            <p className="text-sm text-gray-600 text-center">
              Don&apos;t have an account?{" "}
              <Link to="/signup" className="text-[#1688DF] hover:underline">
                Create one
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
