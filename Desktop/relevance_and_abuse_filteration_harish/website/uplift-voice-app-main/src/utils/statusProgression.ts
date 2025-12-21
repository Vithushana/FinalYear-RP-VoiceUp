export interface StatusStage {
  name: string;
  backendValue: string;
  index: number;
  color: string;
  bgColor: string;
}

export const STATUS_STAGES: StatusStage[] = [
  { name: 'Seen', backendValue: 'seen', index: 0, color: 'text-blue-700', bgColor: 'bg-blue-500' },
  { name: 'Verified', backendValue: 'verified', index: 1, color: 'text-green-700', bgColor: 'bg-green-500' },
  { name: 'On Hold', backendValue: 'hold', index: 2, color: 'text-orange-700', bgColor: 'bg-orange-500' },
  { name: 'In Progress', backendValue: 'in_progress', index: 3, color: 'text-yellow-700', bgColor: 'bg-yellow-500' },
  { name: 'Completed', backendValue: 'completed', index: 4, color: 'text-green-700', bgColor: 'bg-green-500' },
  { name: 'Closed', backendValue: 'closed', index: 5, color: 'text-gray-700', bgColor: 'bg-gray-500' },
];

export const getStatusIndex = (status: string): number => {
  const normalizedStatus = status.toLowerCase().trim();

  // Special case: 'submitted' status should not highlight any circle
  if (normalizedStatus === 'submitted') {
    return -1;
  }

  const stage = STATUS_STAGES.find(s =>
    s.backendValue === normalizedStatus ||
    s.name.toLowerCase() === normalizedStatus
  );
  return stage ? stage.index : -1;
};

export const getNextStatus = (currentStatus: string): string | null => {
  const currentIndex = getStatusIndex(currentStatus);
  if (currentIndex < STATUS_STAGES.length - 1) {
    return STATUS_STAGES[currentIndex + 1].backendValue;
  }
  return null; // Already at final stage
};

export const getStatusColor = (status: string): { color: string; bgColor: string } => {
  const normalizedStatus = status.toLowerCase().trim();
  const stage = STATUS_STAGES.find(s =>
    s.backendValue === normalizedStatus ||
    s.name.toLowerCase() === normalizedStatus
  );
  return stage ? { color: stage.color, bgColor: stage.bgColor } : { color: 'text-gray-700', bgColor: 'bg-gray-500' };
};

export const canAdvanceStatus = (status: string): boolean => {
  return getStatusIndex(status) < STATUS_STAGES.length - 1;
};

export const getStatusDisplayName = (status: string): string => {
  const normalizedStatus = status.toLowerCase().trim();
  const stage = STATUS_STAGES.find(s =>
    s.backendValue === normalizedStatus ||
    s.name.toLowerCase() === normalizedStatus
  );
  return stage ? stage.name : status;
};