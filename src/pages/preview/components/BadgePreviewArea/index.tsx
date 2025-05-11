import * as React from "react";
import { useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScanEye } from "lucide-react";
import FixedPosterPreview from "@/components/badges/FixedPosterPreview";
import { PosterDimensions } from "@/services/posterService";
import { BadgePosition } from "@/components/badges/PositionSelector";

interface BadgePreviewAreaProps {
  activeBadgeType: string | null;
  debugMode: boolean;
  loading: boolean;
  posterDimensions: PosterDimensions;
  togglePoster: () => void;
  toggleDebugMode: () => void;
  activePoster: string;
  renderBadges: (ctx: CanvasRenderingContext2D, dimensions: PosterDimensions) => Promise<void>;
  onBadgePositionChange: (type: string, position: BadgePosition) => void;
  onPosterLoad: (dimensions: PosterDimensions) => void;
}

const BadgePreviewArea: React.FC<BadgePreviewAreaProps> = ({
  activeBadgeType,
  debugMode,
  loading,
  posterDimensions,
  togglePoster,
  toggleDebugMode,
  activePoster,
  renderBadges,
  onBadgePositionChange,
  onPosterLoad
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ScanEye className="w-5 h-5" />
          Preview
        </CardTitle>
        <CardDescription>
        Preview your badge designs with selectable positions
        </CardDescription>
        {/* Poster Switcher and Debug Mode Toggle */}
        <div className="mt-4 flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={togglePoster}
          >
            Switch to {activePoster === "light" ? "Dark" : "Light"} Poster
          </Button>
          <Button 
            variant={debugMode ? "secondary" : "outline"} 
            size="sm" 
            onClick={toggleDebugMode}
          >
            {debugMode ? "Disable" : "Enable"} Debug Mode
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col items-center p-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-sm text-muted-foreground">Loading badge settings...</p>
          </div>
        ) : (
          <>
            <FixedPosterPreview 
              onPosterLoad={onPosterLoad}
              onBadgePositionChange={onBadgePositionChange}
              activeBadgeType={activeBadgeType}
              renderBadges={renderBadges}
              debugMode={debugMode}
            />
            <p className="text-sm text-muted-foreground mt-4">
              {activeBadgeType ? `Use the position grid buttons to place the ${activeBadgeType} badge` : "Select a badge type to edit its position"}
            </p>
          </>
        )}
        <canvas 
          ref={canvasRef} 
          className="hidden" // Hidden canvas for debugging
          width={posterDimensions.width || 300} 
          height={posterDimensions.height || 300} 
        />
      </CardContent>
    </Card>
  );
};

export default BadgePreviewArea;