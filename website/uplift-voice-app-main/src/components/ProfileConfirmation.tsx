import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User } from "lucide-react";

interface ProfileConfirmationProps {
    userData: {
        name: string;
        email: string;
        phone: string;
        position: string;
    };
    onConfirm: (updatedData: any) => void;
    onBack: () => void;
}

const ProfileConfirmation = ({ userData, onConfirm, onBack }: ProfileConfirmationProps) => {
    const [formData, setFormData] = useState(userData);

    const handleChange = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map(word => word[0])
            .join("")
            .toUpperCase()
            .slice(0, 2);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md animate-in fade-in zoom-in duration-200">
                <div className="text-center mb-6">
                    <div className="flex justify-center mb-4">
                        <Avatar className="h-24 w-24 bg-gradient-to-br from-[#1A4776] to-[#1688DF] border-4 border-yellow-400">
                            <AvatarFallback className="bg-transparent text-white text-2xl font-bold">
                                {getInitials(formData.name)}
                            </AvatarFallback>
                        </Avatar>
                    </div>
                    <h2 className="text-2xl font-bold text-[#1A4776]">User Profile</h2>
                    <p className="text-sm text-gray-600 mt-1">Review and edit your details if needed</p>
                </div>

                <div className="space-y-4">
                    <div>
                        <Label htmlFor="confirm-name" className="text-sm font-medium text-gray-700">
                            Full Name
                        </Label>
                        <Input
                            id="confirm-name"
                            value={formData.name}
                            onChange={(e) => handleChange("name", e.target.value)}
                            className="mt-1 bg-gray-50"
                        />
                    </div>

                    <div>
                        <Label htmlFor="confirm-email" className="text-sm font-medium text-gray-700">
                            Email
                        </Label>
                        <Input
                            id="confirm-email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => handleChange("email", e.target.value)}
                            className="mt-1 bg-gray-50"
                        />
                    </div>

                    <div>
                        <Label htmlFor="confirm-phone" className="text-sm font-medium text-gray-700">
                            Phone Number
                        </Label>
                        <Input
                            id="confirm-phone"
                            value={formData.phone}
                            onChange={(e) => handleChange("phone", e.target.value)}
                            className="mt-1 bg-gray-50"
                        />
                    </div>

                    <div>
                        <Label htmlFor="confirm-position" className="text-sm font-medium text-gray-700">
                            Position
                        </Label>
                        <Input
                            id="confirm-position"
                            value={formData.position}
                            onChange={(e) => handleChange("position", e.target.value)}
                            className="mt-1 bg-gray-50"
                        />
                    </div>
                </div>

                <div className="flex gap-3 mt-6">
                    <Button
                        onClick={onBack}
                        variant="outline"
                        className="flex-1 h-11 border-[#1A4776] text-[#1A4776] hover:bg-gray-50"
                    >
                        Back
                    </Button>
                    <Button
                        onClick={() => onConfirm(formData)}
                        className="flex-1 h-11 bg-[#1A4776] hover:bg-[#1688DF] text-white font-medium"
                    >
                        Save
                    </Button>
                </div>
            </div>
        </div>
    );

};

export default ProfileConfirmation;
