import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../ui/card';
import { H1, H2, Body, BodySmall } from '../ui/typography';
import { Loader, SpinLoader, LoadingDots, ButtonLoader } from '../ui/loader';

/**
 * Component showcasing animations from the Aphrodite style guide
 * @returns {JSX.Element} Animations example
 */
const AnimationsExample = () => {
  const [isShaking, setIsShaking] = useState(false);
  const [isPulsing, setIsPulsing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const triggerShake = () => {
    setIsShaking(true);
    setTimeout(() => setIsShaking(false), 500);
  };

  const togglePulse = () => {
    setIsPulsing(!isPulsing);
  };

  const simulateLoading = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  return (
    <div className="p-page space-y-section">
      <div>
        <H1>Animation Examples</H1>
        <Body className="mt-2 text-neutral">
          This example demonstrates the animations and transitions from the Aphrodite style guide
        </Body>
      </div>

      {/* Button Animations */}
      <section className="space-y-default">
        <H2>Button Animations</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <BodySmall>Button Press</BodySmall>
            <Button className="btn-press">
              Press Me
            </Button>
          </div>
          
          <div className="space-y-2">
            <BodySmall>Hover Glow</BodySmall>
            <Button className="hover-glow">
              Hover Over Me
            </Button>
          </div>
          
          <div className="space-y-2">
            <BodySmall>Shake Animation</BodySmall>
            <div className="flex flex-col items-start gap-2">
              <Button 
                className={isShaking ? 'shake' : ''}
                onClick={triggerShake}
              >
                Trigger Shake
              </Button>
              <BodySmall>Click the button to see the effect</BodySmall>
            </div>
          </div>
          
          <div className="space-y-2">
            <BodySmall>Loading Button</BodySmall>
            <Button 
              onClick={simulateLoading}
              disabled={isLoading}
            >
              {isLoading ? <ButtonLoader label="Loading..." /> : 'Click to Load'}
            </Button>
          </div>
        </div>
      </section>

      {/* Loaders */}
      <section className="space-y-default">
        <H2>Loaders</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Opacity Loader</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center py-4">
              <div className="flex items-center gap-4">
                <Loader size="sm" />
                <Loader size="md" />
                <Loader size="lg" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Spin Loader</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center py-4">
              <div className="flex items-center gap-4">
                <SpinLoader size="sm" />
                <SpinLoader size="md" />
                <SpinLoader size="lg" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Loading Dots</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center py-4">
              <div className="flex items-center gap-4">
                <LoadingDots size="sm" />
                <LoadingDots size="md" />
                <LoadingDots size="lg" />
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Element Animations */}
      <section className="space-y-default">
        <H2>Element Animations</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <BodySmall>Fade In</BodySmall>
            <Card className="fade-in">
              <CardContent className="py-4">
                <Body>This card fades in when rendered</Body>
              </CardContent>
            </Card>
          </div>
          
          <div className="space-y-2">
            <BodySmall>Slide In</BodySmall>
            <Card className="slide-in">
              <CardContent className="py-4">
                <Body>This card slides in from the bottom</Body>
              </CardContent>
            </Card>
          </div>
          
          <div className="space-y-2">
            <BodySmall>Pulse Animation</BodySmall>
            <div className="flex flex-col items-start gap-2">
              <Card className={isPulsing ? 'pulse' : ''}>
                <CardContent className="py-4">
                  <Body>This card can pulse</Body>
                </CardContent>
              </Card>
              <Button size="sm" onClick={togglePulse}>
                {isPulsing ? 'Stop Pulse' : 'Start Pulse'}
              </Button>
            </div>
          </div>
          
          <div className="space-y-2">
            <BodySmall>Badge Animation</BodySmall>
            <Card>
              <CardContent className="py-4 relative">
                <Body>Badges appear with a subtle animation</Body>
                <span className="badge-appear absolute top-0 right-0 bg-primary-purple text-white text-xs px-2 py-1 rounded-bl-lg rounded-tr-lg">
                  New
                </span>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Progress Animation */}
      <section className="space-y-default">
        <H2>Progress Animation</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg space-y-6">
          <div className="space-y-2">
            <BodySmall>Progress Bar</BodySmall>
            <div className="h-2 w-full bg-bg-white dark:bg-[#2E2E3E] rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary-purple progress-animate" 
                style={{ '--progress-value': '75%' }}
              ></div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <BodySmall>25% Complete</BodySmall>
              <div className="h-2 w-full bg-bg-white dark:bg-[#2E2E3E] rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent-indigo progress-animate" 
                  style={{ '--progress-value': '25%' }}
                ></div>
              </div>
            </div>
            
            <div className="space-y-2">
              <BodySmall>50% Complete</BodySmall>
              <div className="h-2 w-full bg-bg-white dark:bg-[#2E2E3E] rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent-indigo progress-animate" 
                  style={{ '--progress-value': '50%' }}
                ></div>
              </div>
            </div>
            
            <div className="space-y-2">
              <BodySmall>75% Complete</BodySmall>
              <div className="h-2 w-full bg-bg-white dark:bg-[#2E2E3E] rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent-indigo progress-animate" 
                  style={{ '--progress-value': '75%' }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Transition Examples */}
      <section className="space-y-default">
        <H2>CSS Transitions</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <BodySmall>Modal Transition (Simulated)</BodySmall>
            <div className="border-2 border-dashed border-neutral p-4 rounded-lg">
              <div className="bg-bg-white dark:bg-[#2A2540] p-4 rounded-lg shadow-lg modal-transition modal-enter-active">
                <H3 className="mb-2">Modal Title</H3>
                <Body className="mb-4">This demonstrates how modals transition in and out.</Body>
                <Button size="sm">Close</Button>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <BodySmall>Tab Switching (Simulated)</BodySmall>
            <div className="border-b border-neutral">
              <div className="flex space-x-4">
                <div className="tab-switch tab-active px-4 py-2 border-b-2 border-primary-purple">
                  <BodySmall>Active Tab</BodySmall>
                </div>
                <div className="tab-switch tab-inactive px-4 py-2 border-b-2 border-transparent">
                  <BodySmall>Inactive Tab</BodySmall>
                </div>
                <div className="tab-switch tab-inactive px-4 py-2 border-b-2 border-transparent">
                  <BodySmall>Inactive Tab</BodySmall>
                </div>
              </div>
            </div>
            <div className="p-4 bg-bg-white dark:bg-[#2A2540] rounded-lg mt-4">
              <Body>Tab content area</Body>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AnimationsExample;