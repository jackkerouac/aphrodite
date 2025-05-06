import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card.jsx";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs.jsx";
import { PosterBadge } from "../components/badges/PosterBadge.tsx";
import { BadgeControls } from "../components/badges/BadgeControls.tsx";
import { useBadgeSettings } from "../hooks/useBadgeSettings.ts";

// Import dummy poster images
import lightPoster from "../assets/posters/dummy_poster_light.png";
import darkPoster from "../assets/posters/dummy_poster_dark.png";

export default function Preview() {
  const [activeView, setActiveView] = useState("both");
  const { badgeSettings, isLoading, toggleBadge, updateBadgeSetting } = useBadgeSettings();

  // Helper function to get badge value
  const getBadgeValue = (type: 'audio' | 'resolution' | 'review') => {
    if (type === 'review') {
      const ratings = {
        tmdb: '8.7',
        imdb: '8.2/10',
        rottentomatoes: '94%'
      };
      return ratings[badgeSettings.review.source as keyof typeof ratings];
    }
    return badgeSettings[type].format;
  };

  if (isLoading) {
    return <div>Loading badge settings...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Preview</h1>
      <p className="text-muted-foreground">
        Preview how your badges will look on light and dark posters.
      </p>
      
      <div className="mb-6">
        <Tabs defaultValue="both" onValueChange={setActiveView} value={activeView}>
          <TabsList>
            <TabsTrigger value="both">Both</TabsTrigger>
            <TabsTrigger value="light">Light</TabsTrigger>
            <TabsTrigger value="dark">Dark</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        {(activeView === "both" || activeView === "light") && (
          <Card className={activeView === "both" ? "" : "md:col-span-2"}>
            <CardHeader>
              <CardTitle>Light Theme Poster</CardTitle>
              <CardDescription>
                Preview with light background
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center">
              <div className="border border-gray-200 w-64 h-auto flex flex-col items-center justify-center overflow-hidden relative">
              <img 
                  src={(lightPoster)}
                  alt="Light theme poster preview" 
                  className="max-w-full h-auto object-contain"
                />
                
                {/* Audio badge */}
                {badgeSettings.audio.enabled && (
                  <PosterBadge
                    type="audio"
                    position={badgeSettings.audio.position}
                    value={badgeSettings.audio.format}
                    theme="light"
                  />
                )}
                
                {/* Resolution badge */}
                {badgeSettings.resolution.enabled && (
                  <PosterBadge
                    type="resolution"
                    position={badgeSettings.resolution.position}
                    value={badgeSettings.resolution.format}
                    theme="light"
                  />
                )}
                
                {/* Review badge */}
                {badgeSettings.review.enabled && (
                  <PosterBadge
                    type="review"
                    position={badgeSettings.review.position}
                    value={getBadgeValue('review')}
                    theme="light"
                  />
                )}
              </div>
            </CardContent>
          </Card>
        )}
        
        {(activeView === "both" || activeView === "dark") && (
          <Card className={activeView === "both" ? "" : "md:col-span-2"}>
            <CardHeader>
              <CardTitle>Dark Theme Poster</CardTitle>
              <CardDescription>
                Preview with dark background
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center">
              <div className="border border-gray-700 w-64 h-auto flex flex-col items-center justify-center overflow-hidden relative">
                <img 
                  src={(darkPoster)}
                  alt="Dark theme poster preview" 
                  className="max-w-full h-auto object-contain"
                />
                
                {/* Audio badge */}
                {badgeSettings.audio.enabled && (
                  <PosterBadge
                    type="audio"
                    position={badgeSettings.audio.position}
                    value={badgeSettings.audio.format}
                    theme="dark"
                  />
                )}
                
                {/* Resolution badge */}
                {badgeSettings.resolution.enabled && (
                  <PosterBadge
                    type="resolution"
                    position={badgeSettings.resolution.position}
                    value={badgeSettings.resolution.format}
                    theme="dark"
                  />
                )}
                
                {/* Review badge */}
                {badgeSettings.review.enabled && (
                  <PosterBadge
                    type="review"
                    position={badgeSettings.review.position}
                    value={getBadgeValue('review')}
                    theme="dark"
                  />
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Badge Controls */}
      <div className="mt-6">
        <BadgeControls 
          badgeSettings={badgeSettings}
          toggleBadge={toggleBadge}
          updateBadgeSetting={updateBadgeSetting}
        />
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">About Poster Previews</h2>
        <Card>
          <CardContent className="pt-6">
            <p className="mb-4">This preview page shows how your configured badges will look on both light and dark themed posters. The previews include:</p>
            
            <ul className="list-disc pl-6 space-y-2 mb-4">
              <li><strong>Audio Badge</strong>: Shows audio format information (e.g., Dolby Atmos, DTS-HD)</li>
              <li><strong>Resolution Badge</strong>: Displays the resolution of the media (e.g., 4K, 1080p)</li>
              <li><strong>Review Badge</strong>: Shows rating information from review services</li>
            </ul>
            
            <p>Changes you make in the badge settings below will be reflected in real-time in these previews. This allows you to see how your customizations will appear before applying them to your actual library.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
