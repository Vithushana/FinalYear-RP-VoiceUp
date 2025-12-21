// frontend/src/pages/Auth.tsx
import React, { useState } from "react";
import { ChevronDown, Loader2, LogIn, UserPlus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { postJSON } from "@/lib/api";
import OTPVerification from "@/components/OTPVerification";
import ProfileConfirmation from "@/components/ProfileConfirmation";

/* ---------------- Road Officer Position Data ---------------- */
const roadPositionData = {
  "Western Province": {
    "Colombo": {
      "Colombo MC": ["Chief Engineer - RDA", "Deputy Chief Engineer - RDA", "Assistant Engineer - RDA", "MC Engineer", "MC Assistant Engineer"],
      "Dehiwala-Mount Lavinia MC": ["MC Chief Engineer", "MC Engineer", "MC Technical Officer"],
      "Sri Jayawardenepura Kotte MC": ["MC Chief Engineer", "MC Engineer", "RDD Engineer"],
      "Kaduwela MC": ["MC Chief Engineer", "MC Engineer", "MC Assistant Engineer"],
      "Kolonnawa UC": ["UC Engineer", "UC Technical Officer"],
      "Kesbewa UC": ["UC Engineer", "UC Technical Officer"],
      "Maharagama UC": ["UC Engineer", "UC Technical Officer"],
      "Moratuwa MC": ["MC Chief Engineer", "MC Engineer"],
      "Homagama UC": ["UC Engineer", "UC Technical Officer"],
      "Seethawaka PS": ["PS Engineer", "PS Technical Officer"],
      "Padukka PS": ["PS Engineer", "PS Technical Officer"],
      "Hanwella PS": ["PS Engineer", "PS Technical Officer"],
      "Rathmalana UC": ["UC Engineer", "UC Technical Officer"]
    },
    "Gampaha": {
      "Gampaha District Office": ["Chief Engineer - RDD", "Deputy Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Negombo MC": ["MC Chief Engineer", "MC Engineer"],
      "Ja-Ela UC": ["UC Engineer", "UC Technical Officer"]
    },
    "Kalutara": {
      "Kalutara District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Kalutara UC": ["UC Chief Engineer", "UC Engineer"]
    }
  },
  "Central Province": {
    "Kandy": {
      "Kandy MC": ["MC Chief Engineer", "MC Deputy Engineer", "MC Assistant Engineer", "RDA Engineer"],
      "Kandy District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"]
    },
    "Matale": {
      "Matale District Office": ["Chief Engineer - RDD", "Deputy Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Matale MC": ["MC Engineer", "MC Technical Officer"]
    },
    "Nuwara Eliya": {
      "Nuwara Eliya District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Nuwara Eliya MC": ["MC Chief Engineer", "MC Engineer"]
    }
  },
  "Southern Province": {
    "Galle": {
      "Galle MC": ["MC Chief Engineer", "MC Deputy Engineer", "MC Assistant Engineer"],
      "Galle District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD", "RDA Engineer"]
    },
    "Matara": {
      "Matara District Office": ["Chief Engineer - RDD", "Deputy Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Matara MC": ["MC Chief Engineer", "MC Engineer"]
    },
    "Hambantota": {
      "Hambantota District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Hambantota UC": ["UC Engineer", "UC Technical Officer"]
    }
  },
  "Northern Province": {
    "Jaffna": {
      "Jaffna MC": ["MC Chief Engineer", "MC Engineer", "MC Assistant Engineer"],
      "Jaffna District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD", "RDA Engineer"]
    },
    "Kilinochchi": {
      "Kilinochchi District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"]
    },
    "Mannar": {
      "Mannar District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"]
    }
  },
  "Eastern Province": {
    "Trincomalee": {
      "Trincomalee District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD", "RDA Engineer"],
      "Trincomalee UC": ["UC Chief Engineer", "UC Engineer"]
    },
    "Batticaloa": {
      "Batticaloa District Office": ["Chief Engineer - RDD", "Deputy Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Batticaloa MC": ["MC Chief Engineer", "MC Engineer"]
    },
    "Ampara": {
      "Ampara District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"]
    }
  },
  "North Western Province": {
    "Kurunegala": {
      "Kurunegala MC": ["MC Chief Engineer", "MC Deputy Engineer", "MC Assistant Engineer"],
      "Kurunegala District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD", "RDA Engineer"]
    },
    "Puttalam": {
      "Puttalam District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Puttalam UC": ["UC Engineer", "UC Technical Officer"]
    }
  },
  "North Central Province": {
    "Anuradhapura": {
      "Anuradhapura District Office": ["Chief Engineer - RDD", "Deputy Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Anuradhapura MC": ["MC Chief Engineer", "MC Engineer"]
    },
    "Polonnaruwa": {
      "Polonnaruwa District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Polonnaruwa UC": ["UC Chief Engineer", "UC Engineer"]
    }
  },
  "Uva Province": {
    "Badulla": {
      "Badulla District Office": ["Chief Engineer - RDD", "Deputy Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Badulla MC": ["MC Chief Engineer", "MC Engineer"]
    },
    "Monaragala": {
      "Monaragala District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"]
    }
  },
  "Sabaragamuwa Province": {
    "Ratnapura": {
      "Ratnapura District Office": ["Chief Engineer - RDD", "Deputy Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Ratnapura MC": ["MC Chief Engineer", "MC Engineer"]
    },
    "Kegalle": {
      "Kegalle District Office": ["Chief Engineer - RDD", "Assistant Engineer - RDD"],
      "Kegalle UC": ["UC Engineer", "UC Technical Officer"]
    }
  }
};

/* ---------------- Garbage Officer Position Data ---------------- */
const garbagePositionData = {
  "Western Province": {
    "Colombo": {
      "Colombo MC": ["Chief Sanitation Officer", "Deputy Sanitation Officer", "Garbage Management Head", "Waste Management Supervisor", "Sanitation Inspector"],
      "Dehiwala-Mount Lavinia MC": ["MC Sanitation Officer", "Waste Collection Supervisor", "Sanitation Inspector"],
      "Sri Jayawardenepura Kotte MC": ["MC Sanitation Officer", "Garbage Management Officer", "Waste Disposal Coordinator"],
      "Kaduwela MC": ["MC Sanitation Officer", "Waste Management Officer", "Garbage Collection Supervisor"],
      "Kolonnawa UC": ["UC Sanitation Officer", "Waste Management Officer"],
      "Kesbewa UC": ["UC Sanitation Officer", "Garbage Collection Supervisor"],
      "Maharagama UC": ["UC Sanitation Officer", "Waste Management Officer"],
      "Moratuwa MC": ["MC Sanitation Officer", "Garbage Management Officer"],
      "Homagama UC": ["UC Sanitation Officer", "Waste Management Officer"],
      "Seethawaka PS": ["PS Sanitation Officer", "Waste Management Officer"],
      "Padukka PS": ["PS Sanitation Officer", "Waste Management Officer"],
      "Hanwella PS": ["PS Sanitation Officer", "Waste Management Officer"],
      "Rathmalana UC": ["UC Sanitation Officer", "Waste Management Officer"]
    },
    "Gampaha": {
      "Gampaha District Office": ["District Sanitation Officer", "Waste Management Coordinator", "Sanitation Supervisor"],
      "Negombo MC": ["MC Sanitation Officer", "Garbage Collection Head"],
      "Ja-Ela UC": ["UC Sanitation Officer", "Waste Management Officer"]
    },
    "Kalutara": {
      "Kalutara District Office": ["District Sanitation Officer", "Waste Management Officer"],
      "Kalutara UC": ["UC Sanitation Officer", "Garbage Management Officer"]
    }
  },
  "Central Province": {
    "Kandy": {
      "Kandy MC": ["Chief Sanitation Officer", "Waste Management Head", "Garbage Collection Supervisor", "Sanitation Inspector"],
      "Kandy District Office": ["District Sanitation Officer", "Waste Management Coordinator"]
    },
    "Matale": {
      "Matale District Office": ["District Sanitation Officer", "Waste Management Officer", "Sanitation Supervisor"],
      "Matale MC": ["MC Sanitation Officer", "Garbage Management Officer"]
    },
    "Nuwara Eliya": {
      "Nuwara Eliya District Office": ["District Sanitation Officer", "Waste Management Officer"],
      "Nuwara Eliya MC": ["MC Sanitation Officer", "Garbage Collection Head"]
    }
  },
  "Southern Province": {
    "Galle": {
      "Galle MC": ["Chief Sanitation Officer", "Deputy Sanitation Officer", "Waste Management Head"],
      "Galle District Office": ["District Sanitation Officer", "Waste Management Coordinator", "Sanitation Supervisor"]
    },
    "Matara": {
      "Matara District Office": ["District Sanitation Officer", "Waste Management Officer", "Sanitation Supervisor"],
      "Matara MC": ["MC Sanitation Officer", "Garbage Management Officer"]
    },
    "Hambantota": {
      "Hambantota District Office": ["District Sanitation Officer", "Waste Management Officer"],
      "Hambantota UC": ["UC Sanitation Officer", "Garbage Collection Supervisor"]
    }
  },
  "Northern Province": {
    "Jaffna": {
      "Jaffna MC": ["Chief Sanitation Officer", "Waste Management Head", "Sanitation Inspector"],
      "Jaffna District Office": ["District Sanitation Officer", "Waste Management Coordinator", "Sanitation Supervisor"]
    },
    "Kilinochchi": {
      "Kilinochchi District Office": ["District Sanitation Officer", "Waste Management Officer"]
    },
    "Mannar": {
      "Mannar District Office": ["District Sanitation Officer", "Waste Management Officer"]
    }
  },
  "Eastern Province": {
    "Trincomalee": {
      "Trincomalee District Office": ["District Sanitation Officer", "Waste Management Coordinator", "Sanitation Supervisor"],
      "Trincomalee UC": ["UC Sanitation Officer", "Garbage Management Officer"]
    },
    "Batticaloa": {
      "Batticaloa District Office": ["District Sanitation Officer", "Waste Management Officer", "Sanitation Supervisor"],
      "Batticaloa MC": ["MC Sanitation Officer", "Garbage Management Officer"]
    },
    "Ampara": {
      "Ampara District Office": ["District Sanitation Officer", "Waste Management Officer"]
    }
  },
  "North Western Province": {
    "Kurunegala": {
      "Kurunegala MC": ["Chief Sanitation Officer", "Deputy Sanitation Officer", "Waste Management Head"],
      "Kurunegala District Office": ["District Sanitation Officer", "Waste Management Coordinator", "Sanitation Supervisor"]
    },
    "Puttalam": {
      "Puttalam District Office": ["District Sanitation Officer", "Waste Management Officer"],
      "Puttalam UC": ["UC Sanitation Officer", "Garbage Collection Supervisor"]
    }
  },
  "North Central Province": {
    "Anuradhapura": {
      "Anuradhapura District Office": ["District Sanitation Officer", "Waste Management Officer", "Sanitation Supervisor"],
      "Anuradhapura MC": ["MC Sanitation Officer", "Garbage Management Officer"]
    },
    "Polonnaruwa": {
      "Polonnaruwa District Office": ["District Sanitation Officer", "Waste Management Officer"],
      "Polonnaruwa UC": ["UC Sanitation Officer", "Garbage Management Officer"]
    }
  },
  "Uva Province": {
    "Badulla": {
      "Badulla District Office": ["District Sanitation Officer", "Waste Management Officer", "Sanitation Supervisor"],
      "Badulla MC": ["MC Sanitation Officer", "Garbage Management Officer"]
    },
    "Monaragala": {
      "Monaragala District Office": ["District Sanitation Officer", "Waste Management Officer"]
    }
  },
  "Sabaragamuwa Province": {
    "Ratnapura": {
      "Ratnapura District Office": ["District Sanitation Officer", "Waste Management Officer", "Sanitation Supervisor"],
      "Ratnapura MC": ["MC Sanitation Officer", "Garbage Management Officer"]
    },
    "Kegalle": {
      "Kegalle District Office": ["District Sanitation Officer", "Waste Management Officer"],
      "Kegalle UC": ["UC Sanitation Officer", "Garbage Collection Supervisor"]
    }
  }
};

const getProvinces = (officerType: string) => {
  return officerType === "road" ? Object.keys(roadPositionData) : Object.keys(garbagePositionData);
};

/* ---------------- Position Modal with Officer Type Selection ---------------- */
const PositionModal = ({ onClose, onSelect }: { onClose: () => void; onSelect: (val: string, officerType: string, region: string) => void }) => {
  const [selections, setSelections] = useState({
    officerType: "",
    province: "",
    district: "",
    region: "",
    designation: ""
  });

  const positionData = selections.officerType === "road" ? roadPositionData : garbagePositionData;
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
      if (name === "officerType") next = { ...next, province: "", district: "", region: "", designation: "" };
      if (name === "province") next = { ...next, district: "", region: "", designation: "" };
      if (name === "district") next = { ...next, region: "", designation: "" };
      if (name === "region") next = { ...next, designation: "" };
      return next;
    });
  };

  const handleConfirm = () => {
    if (!selections.designation) return alert("Please select a Designation.");
    onSelect(`${selections.designation} (${selections.province}, ${selections.district})`, selections.officerType, selections.region);
  };

  const isComplete = selections.designation !== "";

  return (
    <div className="fixed inset-0 z-50 bg-gray-900/50 flex items-center justify-center p-3" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 py-4 border-b border-gray-200 sticky top-0 bg-white">
          <h3 className="text-lg font-semibold text-[#1A4776]">Select Position Details</h3>
        </div>

        <div className="p-5 space-y-3">
          {/* Officer Type Selection */}
          <div>
            <Label htmlFor="modal-officer-type" className="text-sm font-semibold">Officer Type</Label>
            <div className="relative">
              <select
                id="modal-officer-type"
                value={selections.officerType}
                onChange={(e) => handleSelectChange("officerType", e.target.value)}
                className="appearance-none h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                <option value="" disabled>Select Officer Type</option>
                <option value="road">Road Related</option>
                <option value="garbage">Garbage Related</option>
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
            </div>
          </div>

          <div>
            <Label htmlFor="modal-province" className="text-sm">Province</Label>
            <div className="relative">
              <select
                id="modal-province"
                value={selections.province}
                onChange={(e) => handleSelectChange("province", e.target.value)}
                disabled={!selections.officerType}
                className="appearance-none h-9 w-full rounded-md border border-gray-300 bg-white px-3 text-sm focus-visible:ring-2 focus-visible:ring-blue-500 disabled:opacity-50"
              >
                <option value="" disabled>Select Province</option>
                {selections.officerType && getProvinces(selections.officerType).map((p) => (
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
                {designations.map((des) => (
                  <option key={des} value={des}>{des}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
            </div>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-gray-200 flex justify-end sticky bottom-0 bg-white">
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
              className={`flex-1 h-9 rounded-md text-sm font-medium transition ${tab === "login" ? "bg-white shadow text-[#1A4776]" : "text-gray-600"
                }`}
            >
              <span className="inline-flex items-center justify-center gap-2 h-full">
                <LogIn className="h-4 w-4" /> Log In
              </span>
            </button>
            <button
              onClick={() => setTab("signup")}
              className={`flex-1 h-9 rounded-md text-sm font-medium transition ${tab === "signup" ? "bg-white shadow text-[#1688DF]" : "text-gray-600"
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
      const res = await postJSON<any>("/api/auth/login", { email, password });

      // Save both token and user data to localStorage (same as signup)
      localStorage.setItem("auth_token", res.token);
      const userData = res.data?.user || res.user;
      if (userData) localStorage.setItem("user", JSON.stringify(userData));

      console.log("✅ Auth.tsx login successful, user data saved:", res.user);
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

/* ---------------- Signup Form with OTP Flow and Officer Type ---------------- */
const SignupForm: React.FC<{ onSuccess: () => void }> = ({ onSuccess }) => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [step, setStep] = useState<"form" | "otp" | "confirm">("form");
  const [phoneNumber, setPhoneNumber] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    position: "Select your position details",
    officerType: "", // 'road' or 'garbage'
    officerRegion: "", // Region/MC/UC (e.g., Kaduwela MC)
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
      // Send OTP with officer_type
      await postJSON<{ success: boolean; message: string }>("/api/auth/send-otp", {
        name: formData.name,
        email: formData.email,
        password: formData.password,
        phone: formData.phone,
        position: formData.position,
        officer_type: formData.officerType, // Include officer type
        officer_region: formData.officerRegion, // Include officer region
        securityCode: formData.securityCode,
      });
      setPhoneNumber(formData.phone);
      setStep("otp");
    } catch (e: any) {
      setMessage(e.message || "Signup failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOTPVerify = async (otp: string) => {
    try {
      const response = await postJSON<{ success: boolean; data: { userData: any } }>("/api/auth/verify-otp", {
        phone: phoneNumber,
        otp: otp,
      });
      if (response.success) {
        setStep("confirm");
      }
    } catch (e: any) {
      alert(e.message || "OTP verification failed");
    }
  };

  const handleResendOTP = async () => {
    try {
      await postJSON<{ success: boolean }>("/api/auth/resend-otp", {
        phone: phoneNumber,
      });
      alert("OTP resent successfully");
    } catch (e: any) {
      alert(e.message || "Failed to resend OTP");
    }
  };

  const handleProfileConfirm = async (updatedData: any) => {
    try {
      const response = await postJSON<{ success: boolean; data: { token: string; user: any } }>("/api/auth/complete-signup", {
        phone: phoneNumber,
        name: updatedData.name,
        email: updatedData.email,
        position: updatedData.position,
        officer_type: formData.officerType, // Include officer type
        officer_region: formData.officerRegion, // Include officer region
      });

      if (response.success && response.data) {
        localStorage.setItem("auth_token", response.data.token);
        localStorage.setItem("user", JSON.stringify(response.data.user));
        navigate("/dashboard");
      }
    } catch (e: any) {
      alert(e.message || "Signup completion failed");
    }
  };

  // Show OTP screen
  if (step === "otp") {
    return (
      <OTPVerification
        phoneNumber={phoneNumber}
        onVerify={handleOTPVerify}
        onResend={handleResendOTP}
      />
    );
  }

  // Show profile confirmation screen
  if (step === "confirm") {
    return (
      <ProfileConfirmation
        userData={{
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          position: formData.position,
        }}
        onConfirm={handleProfileConfirm}
        onBack={() => setStep("form")}
      />
    );
  }

  // Show signup form
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
          onSelect={(val, officerType, region) => {
            setFormData((p) => ({ ...p, position: val, officerType: officerType, officerRegion: region }));
            setIsModalOpen(false);
          }}
        />
      )}
    </form>
  );
};
