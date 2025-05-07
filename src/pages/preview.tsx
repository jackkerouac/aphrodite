import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card.jsx";
import { Button } from "@/components/ui/button"
import { FileSliders, ScanEye } from "lucide-react";

// Import dummy poster images
import lightPoster from "../assets/posters/dummy_poster_light.png";
import darkPoster from "../assets/posters/dummy_poster_dark.png";


export default function Preview() {
  const [activePoster, setActivePoster] = useState("light");
  const [posterImage, setPosterImage] = useState(lightPoster);
  const [buttonText, setButtonText] = useState("Switch to Dark Poster");

  const togglePoster = () => {
    if (activePoster === "light") {
      setActivePoster("dark");
      setPosterImage(darkPoster);
      setButtonText("Switch to Light Poster");
    } else {
      setActivePoster("light");
      setPosterImage(lightPoster);
      setButtonText("Switch to Dark Poster");
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <h1 className="text-3xl font-bold tracking-tight">API Settings</h1>
      <p className="text-muted-foreground">Preview your poster configuration</p>
      <div className="flex flex-col md:flex-row gap-8">
        {/* Poster Settings Card (Left - 50%) */}
        <div className="w-full md:w-1/2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSliders className="w-5 h-5" />
                Poster Settings
              </CardTitle>
              <CardDescription>Customize badge appearance</CardDescription>
            </CardHeader>
            <CardContent>
              {/* We will add BadgeControls here later */}
              <div>Poster Settings Controls</div>
            </CardContent>
          </Card>
        </div>

        {/* Preview Card (Right - 50%) */}
        <div className="w-full md:w-1/2">
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                  <ScanEye className="w-5 h-5" />
                  Preview
              </CardTitle>
              <CardDescription>
                Poster Preview
              </CardDescription>
              {/* Poster Switcher */}
              <div className="mt-4">
              </div>
            </CardHeader>
            <CardContent className="flex flex-col justify-center flex-grow items-center">
              <img
                src={posterImage}
                alt="Poster Preview"
                className="max-w-full h-auto object-contain"
              />
              <Button className="mt-4" onClick={togglePoster}>
                {buttonText}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
