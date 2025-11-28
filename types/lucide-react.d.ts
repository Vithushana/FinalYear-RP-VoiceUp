declare module "lucide-react" {
  import * as React from "react";

  export interface LucideProps extends React.SVGProps<SVGSVGElement> {
    size?: string | number;
  }

  export const Calendar: React.FC<LucideProps>;
  export const MapPin: React.FC<LucideProps>;
  export const XCircle: React.FC<LucideProps>;
  // Add other icons as needed
}