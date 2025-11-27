import React from 'react';
import { Button } from '@/components/ui/button';

interface StatusConfirmationDialogProps {
  isOpen: boolean;
  fromStatus: string;
  toStatus: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const StatusConfirmationDialog: React.FC<StatusConfirmationDialogProps> = ({
  isOpen,
  fromStatus,
  toStatus,
  onConfirm,
  onCancel
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-2xl">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Are you confirming that you change the progress from
          </h3>
          
          <div className="text-xl font-semibold mb-6">
            "{fromStatus}" to "{toStatus}"
          </div>
          
          <div className="flex gap-4 justify-center">
            <Button
              onClick={onCancel}
              variant="outline"
              className="px-6 py-2 bg-gray-300 hover:bg-gray-400 text-gray-700 border-gray-300"
            >
              Cancel
            </Button>
            <Button
              onClick={onConfirm}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              Confirm
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusConfirmationDialog;