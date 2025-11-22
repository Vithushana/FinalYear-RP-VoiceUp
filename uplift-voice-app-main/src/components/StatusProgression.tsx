import React, { useState } from 'react';
import { STATUS_STAGES, getStatusIndex } from '@/utils/statusProgression';
import StatusConfirmationDialog from './StatusConfirmationDialog';

interface StatusProgressionProps {
  currentStatus: string;
  issueId: string;
  onStatusUpdate?: (newStatus: string) => void;
  showNextButton?: boolean;
}

const StatusProgression: React.FC<StatusProgressionProps> = ({
  currentStatus,
  issueId,
  onStatusUpdate,
  showNextButton = true
}) => {
  const currentIndex = getStatusIndex(currentStatus);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingStatus, setPendingStatus] = useState<string>('');

  const handleStatusClick = (targetStatus: string, targetIndex: number) => {
    // Allow clicking only on the next status in progression
    if (onStatusUpdate && targetStatus !== currentStatus && targetIndex === currentIndex + 1) {
      setPendingStatus(targetStatus);
      setShowConfirmation(true);
    }
  };

  const handleConfirm = () => {
    if (onStatusUpdate && pendingStatus) {
      onStatusUpdate(pendingStatus);
    }
    setShowConfirmation(false);
    setPendingStatus('');
  };

  const handleCancel = () => {
    setShowConfirmation(false);
    setPendingStatus('');
  };

  return (
    <>
      <div className="flex flex-col items-center gap-4">
        {/* Status Circles with Labels */}
        <div className="flex items-center justify-center gap-8">
          {STATUS_STAGES.map((stage, index) => (
            <div key={stage.name} className="flex flex-col items-center gap-2">
              <button
                onClick={() => handleStatusClick(stage.name, index)}
                className={`w-6 h-6 rounded-full transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-400 ${
                  index === currentIndex 
                    ? 'bg-green-500 ring-2 ring-green-300' 
                    : index < currentIndex
                    ? 'bg-green-400'
                    : 'bg-gray-300 hover:bg-gray-400'
                } ${
                  onStatusUpdate && index === currentIndex + 1 
                    ? 'cursor-pointer' 
                    : 'cursor-default'
                }`}
                title={`${stage.name}${onStatusUpdate && index === currentIndex + 1 ? ' (Click to advance)' : ''}`}
                disabled={!onStatusUpdate || index !== currentIndex + 1}
              />
              <span className={`text-xs font-medium ${
                index === currentIndex ? 'text-green-600' : 'text-gray-500'
              }`}>
                {stage.name}
              </span>
            </div>
          ))}
        </div>
        
        {/* Current Status Label */}
        <div className="text-sm font-medium text-blue-600">
          Status: {currentStatus}
        </div>
      </div>

      {/* Confirmation Dialog */}
      <StatusConfirmationDialog
        isOpen={showConfirmation}
        fromStatus={currentStatus}
        toStatus={pendingStatus}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </>
  );
};

export default StatusProgression;