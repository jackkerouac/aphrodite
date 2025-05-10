import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Filter } from "lucide-react";

interface SelectionFiltersProps {
  onApplyFilter: (filter: FilterCriteria) => void;
  isApplying?: boolean;
}

export interface FilterCriteria {
  type: 'year' | 'resolution' | 'noReviewScore' | 'mediaType' | 'recent';
  yearFrom?: number;
  yearTo?: number;
  resolution?: '4K' | '1080p' | '720p' | 'SD';
  mediaType?: 'Movie' | 'Series';
  recentDays?: number;
}

export const SelectionFilters: React.FC<SelectionFiltersProps> = ({
  onApplyFilter,
  isApplying = false
}) => {
  const [filterType, setFilterType] = useState<FilterCriteria['type']>('year');
  const [yearFrom, setYearFrom] = useState<string>('');
  const [yearTo, setYearTo] = useState<string>('');
  const [resolution, setResolution] = useState<string>('4K');
  const [mediaType, setMediaType] = useState<string>('Movie');
  const [recentDays, setRecentDays] = useState<string>('30');
  const [isOpen, setIsOpen] = useState(false);

  const handleApply = () => {
    const filter: FilterCriteria = { type: filterType };

    switch (filterType) {
      case 'year':
        if (yearFrom) filter.yearFrom = parseInt(yearFrom);
        if (yearTo) filter.yearTo = parseInt(yearTo);
        break;
      case 'resolution':
        filter.resolution = resolution as FilterCriteria['resolution'];
        break;
      case 'mediaType':
        filter.mediaType = mediaType as FilterCriteria['mediaType'];
        break;
      case 'recent':
        filter.recentDays = parseInt(recentDays);
        break;
    }

    onApplyFilter(filter);
    setIsOpen(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          Smart Select
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Smart Selection</DialogTitle>
          <DialogDescription>
            Select items based on specific criteria
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="filter-type">Filter Type</Label>
            <Select value={filterType} onValueChange={(value) => setFilterType(value as FilterCriteria['type'])}>
              <SelectTrigger id="filter-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="year">By Year Range</SelectItem>
                <SelectItem value="resolution">By Resolution</SelectItem>
                <SelectItem value="mediaType">By Media Type</SelectItem>
                <SelectItem value="noReviewScore">Missing Review Score</SelectItem>
                <SelectItem value="recent">Recently Added</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {filterType === 'year' && (
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="year-from">From Year</Label>
                <Input
                  id="year-from"
                  type="number"
                  placeholder="2020"
                  value={yearFrom}
                  onChange={(e) => setYearFrom(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="year-to">To Year</Label>
                <Input
                  id="year-to"
                  type="number"
                  placeholder="2024"
                  value={yearTo}
                  onChange={(e) => setYearTo(e.target.value)}
                />
              </div>
            </div>
          )}

          {filterType === 'resolution' && (
            <div className="grid gap-2">
              <Label htmlFor="resolution">Resolution</Label>
              <Select value={resolution} onValueChange={setResolution}>
                <SelectTrigger id="resolution">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="4K">4K</SelectItem>
                  <SelectItem value="1080p">1080p</SelectItem>
                  <SelectItem value="720p">720p</SelectItem>
                  <SelectItem value="SD">SD</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {filterType === 'mediaType' && (
            <div className="grid gap-2">
              <Label htmlFor="media-type">Media Type</Label>
              <Select value={mediaType} onValueChange={setMediaType}>
                <SelectTrigger id="media-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Movie">Movies</SelectItem>
                  <SelectItem value="Series">TV Series</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {filterType === 'recent' && (
            <div className="grid gap-2">
              <Label htmlFor="recent-days">Added in last (days)</Label>
              <Input
                id="recent-days"
                type="number"
                placeholder="30"
                value={recentDays}
                onChange={(e) => setRecentDays(e.target.value)}
              />
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="secondary" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={isApplying}>
            {isApplying ? 'Applying...' : 'Apply Filter'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
