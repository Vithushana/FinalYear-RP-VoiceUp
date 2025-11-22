export interface StatusStage {
  name: string;
  index: number;
  color: string;
  bgColor: string;
}

export const STATUS_STAGES: StatusStage[] = [
  { name: 'Seen', index: 0, color: 'text-blue-700', bgColor: 'bg-blue-500' },
  { name: 'Verified', index: 1, color: 'text-green-700', bgColor: 'bg-green-500' },
  { name: 'In Progress', index: 2, color: 'text-yellow-700', bgColor: 'bg-yellow-500' },
  { name: 'On Hold', index: 3, color: 'text-orange-700', bgColor: 'bg-orange-500' },
  { name: 'Completed', index: 4, color: 'text-green-700', bgColor: 'bg-green-500' },
];

export const getStatusIndex = (status: string): number => {
  const stage = STATUS_STAGES.find(s => s.name === status);
  return stage ? stage.index : 0;
};

export const getNextStatus = (currentStatus: string): string | null => {
  const currentIndex = getStatusIndex(currentStatus);
  if (currentIndex < STATUS_STAGES.length - 1) {
    return STATUS_STAGES[currentIndex + 1].name;
  }
  return null; // Already at final stage
};

export const getStatusColor = (status: string): { color: string; bgColor: string } => {
  const stage = STATUS_STAGES.find(s => s.name === status);
  return stage ? { color: stage.color, bgColor: stage.bgColor } : { color: 'text-gray-700', bgColor: 'bg-gray-500' };
};

export const canAdvanceStatus = (status: string): boolean => {
  return getStatusIndex(status) < STATUS_STAGES.length - 1;
};