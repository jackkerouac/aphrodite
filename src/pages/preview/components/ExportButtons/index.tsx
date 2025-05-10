import * as React from "react";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

interface ExportButtonsProps {
  saveBadgeAsPng: (type: string) => void;
  displaySettings: {
    showAudioBadge: boolean;
    showResolutionBadge: boolean;
    showReviewBadge: boolean;
  };
}

const ExportButtons: React.FC<ExportButtonsProps> = ({
  saveBadgeAsPng,
  displaySettings
}) => {
  return (
    <div className="grid grid-cols-3 gap-2">
      <Button 
        variant="outline" 
        className="w-full"
        onClick={() => saveBadgeAsPng("audio")}
        disabled={!displaySettings.showAudioBadge}
      >
        <Download className="h-4 w-4 mr-2" />
        Audio Badge
      </Button>
      <Button 
        variant="outline" 
        className="w-full"
        onClick={() => saveBadgeAsPng("resolution")}
        disabled={!displaySettings.showResolutionBadge}
      >
        <Download className="h-4 w-4 mr-2" />
        Resolution Badge
      </Button>
      <Button 
        variant="outline" 
        className="w-full"
        onClick={() => saveBadgeAsPng("review")}
        disabled={!displaySettings.showReviewBadge}
      >
        <Download className="h-4 w-4 mr-2" />
        Review Badge
      </Button>
    </div>
  );
};

export default ExportButtons;
