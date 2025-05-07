import React from 'react';
import {
  H1,
  H2,
  H3,
  BodyLarge,
  Body,
  BodySmall,
  CodeText,
  Label,
  Subtitle
} from '../ui/typography';

/**
 * Component showcasing the typography system
 * @returns {JSX.Element} Typography example component
 */
const TypographyExample = () => {
  return (
    <div className="p-page space-y-section">
      <div>
        <H1>Typography System (H1)</H1>
        <Subtitle className="mt-2">
          This example demonstrates all typography components from the Aphrodite style guide
        </Subtitle>
      </div>

      <div className="space-y-default">
        <H2>Heading Examples (H2)</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg">
          <H1>Page Title (H1)</H1>
          <div className="h-1 w-full my-4 bg-secondary-lilac"></div>
          
          <H2>Section Header (H2)</H2>
          <div className="h-1 w-full my-4 bg-secondary-lilac"></div>
          
          <H3>Subsection Heading (H3)</H3>
        </div>
      </div>

      <div className="space-y-default">
        <H2>Text Body Examples</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg space-y-4">
          <div>
            <Label>Body Large (16px)</Label>
            <BodyLarge>
              Used for dialog content and modals. The quick brown fox jumps over the lazy dog.
              This text is larger and more prominent for better readability in focused interfaces.
            </BodyLarge>
          </div>
          
          <div>
            <Label>Body (14px)</Label>
            <Body>
              Primary UI content text. The quick brown fox jumps over the lazy dog.
              This is the standard text size for most interface elements and content areas.
            </Body>
          </div>
          
          <div>
            <Label>Body Small (12px)</Label>
            <BodySmall>
              Used for labels, metadata, and table headers. The quick brown fox jumps over the lazy dog.
              This smaller text is perfect for supporting information and compact UI elements.
            </BodySmall>
          </div>
        </div>
      </div>

      <div className="space-y-default">
        <H2>Special Text Elements</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg space-y-4">
          <div>
            <Label>Code Text (13px, Monospace)</Label>
            <CodeText className="block p-2 bg-bg-white dark:bg-bg-dark rounded">
              const aphrodite = new PosterGenerator({ quality: "4K" });
              aphrodite.generate();
            </CodeText>
          </div>
          
          <div>
            <Label>Subtitle</Label>
            <H3>Feature Section</H3>
            <Subtitle className="mt-1">
              Descriptive text that provides additional context below headings
            </Subtitle>
          </div>
          
          <div>
            <Label>Form Label Example</Label>
            <div className="mt-1">
              <Label htmlFor="example-input">Input Label</Label>
              <input 
                id="example-input"
                type="text"
                className="w-full h-12 px-3 rounded-lg border border-neutral"
                placeholder="Input with proper labeling"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-default">
        <H2>Text Colors & Styles</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>Primary Color</Label>
            <Body className="text-primary-purple">
              Text in primary purple color
            </Body>
          </div>
          
          <div>
            <Label>Accent Color</Label>
            <Body className="text-accent-indigo">
              Text in accent indigo color
            </Body>
          </div>
          
          <div>
            <Label>Neutral Color</Label>
            <Body className="text-neutral">
              Text in neutral gray color
            </Body>
          </div>
          
          <div>
            <Label>Success Color</Label>
            <Body className="text-success">
              Text in success green color
            </Body>
          </div>
          
          <div>
            <Label>Error Color</Label>
            <Body className="text-error">
              Text in error red color
            </Body>
          </div>
          
          <div>
            <Label>Warning Color</Label>
            <Body className="text-warning">
              Text in warning amber color
            </Body>
          </div>
          
          <div>
            <Label>Bold Weight</Label>
            <Body className="font-bold">
              Text with bold (700) weight
            </Body>
          </div>
          
          <div>
            <Label>Semibold Weight</Label>
            <Body className="font-semibold">
              Text with semibold (600) weight
            </Body>
          </div>
          
          <div>
            <Label>Medium Weight</Label>
            <Body className="font-medium">
              Text with medium (500) weight
            </Body>
          </div>
          
          <div>
            <Label>Regular Weight</Label>
            <Body className="font-normal">
              Text with regular (400) weight
            </Body>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypographyExample;
