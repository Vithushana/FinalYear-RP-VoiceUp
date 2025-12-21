// Utility function to get border color based on priority
export const getPriorityBorderColor = (priority: string | number): string => {
  const priorityStr = String(priority).toLowerCase();
  switch (priorityStr) {
    case 'critical':
    case 'high':
    case '1':
      return 'border-red-500'; // Red border for critical/stage 1
    case 'medium':
    case '2':
      return 'border-orange-500'; // Orange border for medium/stage 2
    case 'low':
    case '3':
      return 'border-yellow-500'; // Yellow border for low/stage 3
    default:
      return 'border-gray-200'; // Default gray border
  }
};

// Get priority label for display
export const getPriorityLabel = (priority: string): string => {
  switch (priority?.toLowerCase()) {
    case 'critical':
    case 'high':
    case '1':
      return 'Critical';
    case 'medium':
    case '2':
      return 'Medium';
    case 'low':
    case '3':
      return 'Low';
    default:
      return priority || 'Unknown';
  }
};