import React, { useRef, useEffect } from 'react';
import { extractBadgeWithTransparency } from "@/services/badgeRenderer";

interface BadgePreviewProps {
  badgeData: string;
  width: number;
  height: number;
}

const BadgePreview: React.FC<BadgePreviewProps> = ({ badgeData, width, height }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
    };
    img.src = badgeData;
  }, [badgeData, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
    />
  );
};

export default BadgePreview;