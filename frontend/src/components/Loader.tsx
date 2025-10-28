import { Loader2 } from 'lucide-react';

interface LoaderProps {
  size?: number;
  text?: string;
}

export const Loader = ({ size = 24, text }: LoaderProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="animate-spin text-primary-600" size={size} />
      {text && <p className="mt-4 text-gray-600 dark:text-gray-400">{text}</p>}
    </div>
  );
};
