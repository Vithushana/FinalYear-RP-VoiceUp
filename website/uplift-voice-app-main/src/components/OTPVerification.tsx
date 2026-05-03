import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

interface OTPVerificationProps {
    phoneNumber: string;
    onVerify: (otp: string) => void;
    onResend: () => void;
    loading?: boolean;
}

const OTPVerification = ({ phoneNumber, onVerify, onResend, loading = false }: OTPVerificationProps) => {
    const [otp, setOtp] = useState(["", "", "", ""]);
    const inputRefs = [
        useRef<HTMLInputElement>(null),
        useRef<HTMLInputElement>(null),
        useRef<HTMLInputElement>(null),
        useRef<HTMLInputElement>(null),
    ];

    useEffect(() => {
        // Focus first input on mount
        inputRefs[0].current?.focus();
    }, []);

    const handleChange = (index: number, value: string) => {
        if (value.length > 1) return; // Only allow single digit

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        // Auto-focus next input
        if (value && index < 3) {
            inputRefs[index + 1].current?.focus();
        }
    };

    const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
        if (e.key === "Backspace" && !otp[index] && index > 0) {
            inputRefs[index - 1].current?.focus();
        }
    };

    const handleSubmit = () => {
        const otpValue = otp.join("");
        if (otpValue.length === 4) {
            onVerify(otpValue);
        }
    };

    const isComplete = otp.every(digit => digit !== "");

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md mx-4 animate-in fade-in zoom-in duration-200">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-[#1A4776] mb-2">Enter OTP</h2>
                    <p className="text-gray-600 text-sm">
                        Please enter the 4-digit code sent to<br />
                        <span className="font-medium">{phoneNumber}</span>
                    </p>
                </div>

                <div className="flex justify-center gap-3 mb-6">
                    {otp.map((digit, index) => (
                        <input
                            key={index}
                            ref={inputRefs[index]}
                            type="text"
                            inputMode="numeric"
                            maxLength={1}
                            value={digit}
                            onChange={(e) => handleChange(index, e.target.value.replace(/\D/g, ""))}
                            onKeyDown={(e) => handleKeyDown(index, e)}
                            className="w-14 h-14 text-center text-2xl font-bold border-2 border-gray-300 rounded-lg focus:border-[#1688DF] focus:ring-2 focus:ring-[#1688DF] focus:outline-none transition-all"
                        />
                    ))}
                </div>

                <Button
                    onClick={handleSubmit}
                    disabled={!isComplete || loading}
                    className="w-full h-12 bg-[#1A4776] hover:bg-[#1688DF] text-white font-medium rounded-lg transition-colors"
                >
                    {loading ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Verifying...
                        </>
                    ) : (
                        "Enter"
                    )}
                </Button>

                <div className="text-center mt-4">
                    <span className="text-sm text-gray-600">Didn't receive the code? </span>
                    <button
                        onClick={onResend}
                        className="text-sm text-[#1688DF] hover:underline font-medium"
                    >
                        Resend OTP
                    </button>
                </div>
            </div>
        </div>
    );

};

export default OTPVerification;
