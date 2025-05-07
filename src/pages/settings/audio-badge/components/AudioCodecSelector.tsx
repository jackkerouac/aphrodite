import React from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface AudioCodecSelectorProps {
  selectedAudioCodec: string;
  handleAudioCodecChange: (value: string) => void;
  audioCodecOptions: string[];
}

const AudioCodecSelector: React.FC<AudioCodecSelectorProps> = ({
  selectedAudioCodec,
  handleAudioCodecChange,
  audioCodecOptions
}) => {
  return (
    <div className="space-y-2">
      <Label htmlFor="audio-codec">Audio Codec Type</Label>
      <Select
        value={selectedAudioCodec}
        onValueChange={handleAudioCodecChange}
      >
        <SelectTrigger>
          <SelectValue placeholder="Select audio codec type" />
        </SelectTrigger>
        <SelectContent>
          {audioCodecOptions.map((option) => (
            <SelectItem key={option} value={option}>
              {option.replace(/_/g, ' ').toUpperCase()}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export default AudioCodecSelector;