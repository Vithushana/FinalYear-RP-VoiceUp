// frontend/src/pages/Auth.tsx
import React, { useState } from "react";
import { ChevronDown, Loader2, LogIn, UserPlus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { postJSON } from "@/lib/api";

/* ---------------- Mock Data for Position Modal ---------------- */
const positionData = {
  "Central Province": {
    "District A": {
      "North Region": ["Policy Advisor", "Support Staff"],
      "South Region": ["Community Manager"],
    },
    "District B": {
      "East Region": ["Department Head", "Regional Officer"],
      "West Region": ["Support Staff"],
    },
  },
  "Western Province": {
    "District X": {
      "City Region": ["Policy Advisor", "Community Manager"],
      "Rural Region": ["Regional Officer"],
    },
  },
};
const getProvinces = () => Object.keys(positionData);

/* ---------------- Position Modal ---------------- */
const PositionModal = ({ onClose, onSelect }: { onClose: () => void; onSelect: (val: string) => void }) => {
  const [selections, setSelections] = useState({ province: "", district: "", region: "", designation: "" });

  const districts = selections.province ? Object.keys(positionData[selections.province]) : [];
  const regions =
    selections.province && selections.district ? Object.keys(positionData[selections.province][selections.district]) : [];
  const designations =
    selections.province && selections.district && selections.region
      ? positionData[selections.province][selections.district][selections.region]
      : [];

  const handleSelectChange = (name: string, value: string) => {
    setSelections((prev) => {
      let next = { ...prev, [name]: value };
      if (name === "province") next = { ...next, district: "", region: "", designation: "" };
      if (name === "district") next = { ...next, region: "", designation: "" };
      if (name === "region") next = { ...next, designation: "" };
      return next;
    });
  };

  const handleConfirm = () => {
    if (!selections.designation) return alert("Please select a Designation.");
    onSelect(`${selections.designation} (${selections.province}, ${selections.district})`);
  };

  const isComplete = selections.designation !== "";

  return (
    <div className="fixed inset-0 z-50 bg-gray-900/50 flex items-center justify-center p-3" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-2xl w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-[#1A4776]">Select Position Details</h3>
        </div>

        <div className="p-5 space-y-3">
          <div>
            <Label htmlFor="modal-province" className="text-sm">Province</Label>
            <div className="relative">
              <select
                id="modal-province"
                value={selections.province}
                onChange={(e) => handleSelectChange("province", e.target.value)}
                className="appearance-none h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                <option value="" disabled>Select Province</option>
                {getProvinces().map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
            </div>
          </div>

          <div>
            <Label htmlFor="modal-district" className="text-sm">District</Label>
            <div className="relative">
              <select
                id="modal-district"
                value={selections.district}
                onChange={(e) => handleSelectChange("district", e.target.value)}
                disabled={!selections.province}
                className="appearance-none h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50"
              >
                <option value="" disabled>Select District</option>
                {districts.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
            </div>
          </div>

          <div>
            <Label htmlFor="modal-region" className="text-sm">Region</Label>
            <div className="relative">
              <select
                id="modal-region"
                value={selections.region}
                onChange={(e) => handleSelectChange("region", e.target.value)}
                disabled={!selections.district}
                className="appearance-none h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50"
              >
                <option value="" disabled>Select Region</option>
                {regions.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
            </div>
          </div>

          <div>
            <Label htmlFor="modal-designation" className="text-sm">Designation</Label>
            <div className="relative">
              <select
                id="modal-designation"
                value={selections.designation}
                onChange={(e) => handleSelectChange("designation", e.target.value)}
                disabled={!selections.region}
                className="appearance-none h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50"
              >
                <option value="" disabled>Select Designation</option>
                {designations.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
            </div>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-gray-200 flex justify-end">
          <Button
            type="button"
            onClick={handleConfirm}
            disabled={!isComplete}
            className={`h-9 px-4 bg-gradient-to-r from-[#1A4776] to-[#1688DF] text-white ${!isComplete ? "opacity-50 cursor-not-allowed" : "shadow-sm"}`}
          >
            OK
          </Button>
        </div>
      </div>
    </div>
  );
};

/* ---------------- Auth Page (Tabs: Login / Signup) ---------------- */
const Auth: React.FC = () => {
  const navigate = useNavigate();
  const [tab, setTab] = useState<"login" | "signup">("login");

  const LeftPanel = (
    <div className="hidden lg:flex flex-col items-center justify-center p-10 text-center">
      <img src="/mic.png" alt="Voice Up" className="mb-3 w-16 h-16" />
      <h1 className="text-4xl font-extrabold tracking-tight mb-3 bg-clip-text text-transparent bg-gradient-to-r from-[#1A4776] to-[#1688DF]">
        VOICE UP
      </h1>
      <p className="text-base max-w-md leading-relaxed bg-clip-text text-transparent bg-gradient-to-r from-[#1A4776] to-[#1688DF]">
        Empowering you to serve better — we streamline your tasks and relay every citizen&apos;s voice directly to you
      </p>
      <div className="mt-4 w-full">
        <img src="/img.png" alt="Voice Up" className="mx-auto max-w-full h-auto object-contain" />
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-6xl bg-white grid lg:grid-cols-2 rounded-xl border border-gray-200 shadow-md overflow-hidden">
        {LeftPanel}
        <div className="p-6 sm:p-8 lg:p-10">
          {/* Tabs */}
          <div className="mb-5 flex gap-1 bg-gray-100 rounded-md p-1 w-full max-w-md mx-auto">
            <button
              onClick={() => setTab("login")}
              className={`flex-1 h-9 rounded-md text-sm font-medium transition ${
                tab === "login" ? "bg-white shadow text-[#1A4776]" : "text-gray-600"
              }`}
            >
              <span className="inline-flex items-center justify-center gap-2 h-full">
                <LogIn className="h-4 w-4" /> Log In
              </span>
            </button>
            <button
              onClick={() => setTab("signup")}
              className={`flex-1 h-9 rounded-md text-sm font-medium transition ${
                tab === "signup" ? "bg-white shadow text-[#1688DF]" : "text-gray-600"
              }`}
            >
              <span className="inline-flex items-center justify-center gap-2 h-full">
                <UserPlus className="h-4 w-4" /> Sign Up
              </span>
            </button>
          </div>

          {tab === "login" ? (
            <LoginForm onSuccess={() => navigate("/dashboard")} />
          ) : (
            <SignupForm onSuccess={() => setTab("login")} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Auth;

/* ---------------- Login Form (compact, no placeholders) ---------------- */
const LoginForm: React.FC<{ onSuccess: () => void }> = ({ onSuccess }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      const res = await postJSON<{ ok: boolean; token: string; user: any }>("/api/auth/login", { email, password });
      localStorage.setItem("auth_token", res.token);
      onSuccess();
    } catch (e: any) {
      setErr(e.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4 max-w-md mx-auto">
      <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#1A4776] to-[#1688DF] text-center">
        Welcome back
      </h2>

      <div className="space-y-1">
        <Label htmlFor="login-email" className="text-sm">Email</Label>
        <Input
          id="login-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="h-9 text-sm"
          required
        />
      </div>

      <div className="space-y-1">
        <Label htmlFor="login-pass" className="text-sm">Password</Label>
        <Input
          id="login-pass"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="h-9 text-sm"
          required
        />
      </div>

      {err && <div className="text-xs bg-red-100 text-red-700 p-2 rounded">{err}</div>}

      <Button type="submit" disabled={loading} className="h-9 w-full bg-gradient-to-r from-[#1A4776] to-[#1688DF] text-white">
        {loading ? (<><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Signing in…</>) : ("Log In")}
      </Button>
    </form>
  );
};

/* ---------------- Signup Form (compact, no placeholders) ---------------- */
const SignupForm: React.FC<{ onSuccess: () => void }> = ({ onSuccess }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    position: "Select your position details",
    phone: "",
    email: "",
    password: "",
    agreed: false,
    securityCode: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.agreed) {
      setMessage("You must agree to all statements to sign up.");
      return;
    }
    setIsSubmitting(true);
    setMessage("");
    try {
      await postJSON<{ ok: boolean; message: string }>("/api/auth/signup", {
        name: formData.name,
        email: formData.email,
        password: formData.password,
        phone: formData.phone,
        position: formData.position,
        securityCode: formData.securityCode,
      });
      onSuccess(); // switch to login tab
    } catch (e: any) {
      setMessage(e.message || "Signup failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-2 max-w-md">
      <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#1A4776] to-[#1688DF] text-center">
        Create your account
      </h2>

      <div className="space-y-0">
        <Label htmlFor="name" className="text-sm">Your Name</Label>
        <Input id="name" name="name" value={formData.name} onChange={handleChange} className="h-9 text-sm" required />
      </div>

      <div className="space-y-0">
        <Label className="text-sm">Position</Label>
        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          className="h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-left text-sm focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          <span className={formData.position ? "text-gray-900" : "text-gray-500"}>
            {formData.position || "Select Designation"}
          </span>
        </button>
      </div>

      <div className="space-y-0">
        <Label htmlFor="phone" className="text-sm">Phone Number</Label>
        <Input id="phone" name="phone" type="tel" value={formData.phone} onChange={handleChange} className="h-9 text-sm" required />
      </div>

      <div className="space-y-0">
        <Label htmlFor="email" className="text-sm">Email</Label>
        <Input id="email" name="email" type="email" value={formData.email} onChange={handleChange} className="h-9 text-sm" required />
      </div>

      <div className="space-y-0">
        <Label htmlFor="password" className="text-sm">Password</Label>
        <Input id="password" name="password" type="password" value={formData.password} onChange={handleChange} className="h-9 text-sm" required />
      </div>

      <div className="space-y-0">
        <Label htmlFor="securityCode" className="text-sm">Security Code</Label>
        <Input id="securityCode" name="securityCode" value={formData.securityCode} onChange={handleChange} className="h-9 text-sm" required />
      </div>

      <label className="flex items-center gap-2">
        <Checkbox
          id="agreed"
          checked={formData.agreed}
          onCheckedChange={(checked) => setFormData((prev) => ({ ...prev, agreed: Boolean(checked) }))}
        />
        <span className="text-sm text-gray-700">I agree to all the statements</span>
      </label>

      {message && (
        <div className={`p-2 rounded text-xs ${message.includes("successfully") ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {message}
        </div>
      )}

      <Button type="submit" disabled={isSubmitting} className="h-9 w-full bg-gradient-to-r from-[#1A4776] to-[#1688DF] text-white">
        {isSubmitting ? (<><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating…</>) : ("Sign Up")}
      </Button>

      {isModalOpen && (
        <PositionModal
          onClose={() => setIsModalOpen(false)}
          onSelect={(val) => {
            setFormData((p) => ({ ...p, position: val }));
            setIsModalOpen(false);
          }}
        />
      )}
    </form>
  );
};
