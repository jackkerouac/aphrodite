import React from 'react';
import { Button } from '@/components/ui/button';
import { Download } from 'lucide-react';

interface DownloadPosterButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

const DownloadPosterButton: React.FC<DownloadPosterButtonProps> = ({
  onClick,
  disabled = false
}) => {
  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      className="w-full mt-4"
      variant="default"
    >
      <Download className="mr-2 h-4 w-4" />
      Download Poster
    </Button>
  );
};

export default DownloadPosterButton;
