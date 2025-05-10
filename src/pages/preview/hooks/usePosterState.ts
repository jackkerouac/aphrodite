import { useState, useEffect } from "react";
import { PosterDimensions } from "@/services/posterService";
import { preloadResolutionImages } from "@/utils/resolutionUtils";
// Import dummy poster images
import lightPoster from "../../../assets/example_poster_light.png";
import darkPoster from "../../../assets/example_poster_dark.png";

export interface PosterState {
  activePoster: string;
  posterImage: string;
  posterDimensions: PosterDimensions;
  debugMode: boolean;
  loading: boolean;
  togglePoster: () => void;
  toggleDebugMode: () => void;
  handlePosterLoad: (dimensions: PosterDimensions) => void;
  setLoading: (loading: boolean) => void;
}

export const usePosterState = (): PosterState => {
  // State for poster and badge display
  const [activePoster, setActivePoster] = useState("light");
  const [posterImage, setPosterImage] = useState(lightPoster);
  const [posterDimensions, setPosterDimensions] = useState<PosterDimensions>({
    width: 0,
    height: 0,
    aspectRatio: 1,
  });
  
  // Debug mode toggle
  const [debugMode, setDebugMode] = useState(false);
  
  // Loading state
  const [loading, setLoading] = useState(true);

  // Preload resolution images when component mounts
  useEffect(() => {
    const preloadImages = async () => {
      try {
        console.log('Preloading resolution badge images...');
        await preloadResolutionImages();
        console.log('Resolution badge images preloaded successfully');
      } catch (error) {
        console.error('Error preloading resolution badge images:', error);
      }
    };
    
    preloadImages();
  }, []);

  // Toggle between light and dark poster
  const togglePoster = () => {
    if (activePoster === "light") {
      setActivePoster("dark");
      setPosterImage(darkPoster);
    } else {
      setActivePoster("light");
      setPosterImage(lightPoster);
    }
  };

  // Toggle debug mode
  const toggleDebugMode = () => {
    setDebugMode(!debugMode);
  };

  // Handle poster image loading and set dimensions
  const handlePosterLoad = (dimensions: PosterDimensions) => {
    console.log('Poster dimensions received from PosterPreview:', dimensions);
    setPosterDimensions(dimensions);
  };

  return {
    activePoster,
    posterImage,
    posterDimensions,
    debugMode,
    loading,
    togglePoster,
    toggleDebugMode,
    handlePosterLoad,
    setLoading
  };
};
