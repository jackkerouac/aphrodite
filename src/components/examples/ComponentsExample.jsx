import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../ui/card';
import { Input } from '../ui/input';
import { H1, H2, H3, Body, BodySmall, BodyLarge, Label } from '../ui/typography';
import { Heart, Search, Bell, Settings, ChevronRight, CheckCircle2, AlertCircle } from 'lucide-react';

/**
 * Component showcasing the UI components from the Aphrodite style guide
 * @returns {JSX.Element} Components example
 */
const ComponentsExample = () => {
  const [inputValue, setInputValue] = useState('');
  const [hasError, setHasError] = useState(false);
  const [hasSuccess, setHasSuccess] = useState(false);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    setHasError(false);
    setHasSuccess(false);
  };

  const validateInput = () => {
    if (!inputValue.trim()) {
      setHasError(true);
      setHasSuccess(false);
    } else {
      setHasError(false);
      setHasSuccess(true);
    }
  };

  return (
    <div className="p-page space-y-section">
      <div>
        <H1>UI Components (H1)</H1>
        <Body className="mt-2 text-neutral">
          This example demonstrates the core UI components from the Aphrodite style guide
        </Body>
      </div>

      {/* Buttons Section */}
      <section className="space-y-default">
        <H2>Buttons</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Primary Button</Label>
              <Button>Primary Button</Button>
            </div>
            
            <div className="space-y-2">
              <Label>Secondary Button</Label>
              <Button variant="secondary">Secondary Button</Button>
            </div>
            
            <div className="space-y-2">
              <Label>Icon Button</Label>
              <div className="flex space-x-2">
                <Button variant="icon" size="icon">
                  <Heart size={20} />
                </Button>
                <Button variant="icon" size="icon">
                  <Search size={20} />
                </Button>
                <Button variant="icon" size="icon">
                  <Bell size={20} />
                </Button>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Ghost Button</Label>
              <Button variant="ghost">Ghost Button</Button>
            </div>
            
            <div className="space-y-2">
              <Label>Link Button</Label>
              <Button variant="link">Link Button</Button>
            </div>
            
            <div className="space-y-2">
              <Label>Destructive Button</Label>
              <Button variant="destructive">Delete Item</Button>
            </div>
          </div>
          
          <div className="mt-6 space-y-2">
            <Label>Button Sizes</Label>
            <div className="flex flex-wrap items-center gap-4">
              <Button size="sm">Small</Button>
              <Button>Default</Button>
              <Button size="lg">Large</Button>
            </div>
          </div>
          
          <div className="mt-6 space-y-2">
            <Label>Disabled State</Label>
            <div className="flex flex-wrap items-center gap-4">
              <Button disabled>Disabled Primary</Button>
              <Button variant="secondary" disabled>Disabled Secondary</Button>
            </div>
          </div>
        </div>
      </section>

      {/* Cards Section */}
      <section className="space-y-default">
        <H2>Cards</H2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Simple Card</CardTitle>
              <CardDescription>This is a basic card with a title and description</CardDescription>
            </CardHeader>
            <CardContent>
              <Body>
                Cards are used to group related content and actions. They can contain
                various elements such as text, buttons, and inputs.
              </Body>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings size={20} className="text-primary-purple" />
                Card with Actions
              </CardTitle>
              <CardDescription>This card includes interactive elements</CardDescription>
            </CardHeader>
            <CardContent>
              <Body className="mb-4">
                Cards can include form elements, buttons, and other interactive components.
              </Body>
              <Input placeholder="Enter some text..." className="w-full mb-2" />
            </CardContent>
            <CardFooter className="justify-between">
              <Button variant="ghost" size="sm">Cancel</Button>
              <Button size="sm">Submit</Button>
            </CardFooter>
          </Card>
          
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Feature Card</CardTitle>
              <CardDescription>A wider card spanning multiple columns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex flex-col items-center text-center p-4">
                  <div className="bg-secondary-lilac text-primary-purple p-3 rounded-full mb-3">
                    <Heart size={24} />
                  </div>
                  <H3 className="mb-2">Customizable</H3>
                  <BodySmall>Fully customizable according to your needs</BodySmall>
                </div>
                
                <div className="flex flex-col items-center text-center p-4">
                  <div className="bg-secondary-lilac text-primary-purple p-3 rounded-full mb-3">
                    <Bell size={24} />
                  </div>
                  <H3 className="mb-2">Responsive</H3>
                  <BodySmall>Responsive design that works on all devices</BodySmall>
                </div>
                
                <div className="flex flex-col items-center text-center p-4">
                  <div className="bg-secondary-lilac text-primary-purple p-3 rounded-full mb-3">
                    <Settings size={24} />
                  </div>
                  <H3 className="mb-2">Powerful</H3>
                  <BodySmall>Powerful features to enhance your workflow</BodySmall>
                </div>
              </div>
            </CardContent>
            <CardFooter className="justify-center">
              <Button className="w-full md:w-auto">Learn More <ChevronRight size={16} className="ml-1" /></Button>
            </CardFooter>
          </Card>
        </div>
      </section>

      {/* Inputs Section */}
      <section className="space-y-default">
        <H2>Inputs</H2>
        
        <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg space-y-6">
          <div className="space-y-2">
            <Label htmlFor="default-input">Default Input</Label>
            <Input 
              id="default-input"
              placeholder="Enter some text..."
              className="w-full"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="error-input">Input with Error</Label>
            <Input 
              id="error-input"
              placeholder="Enter some text..."
              className="w-full"
              error={true}
            />
            <BodySmall className="text-error flex items-center gap-1 mt-1">
              <AlertCircle size={14} /> This field is required
            </BodySmall>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="success-input">Input with Success</Label>
            <Input 
              id="success-input"
              placeholder="Enter some text..."
              className="w-full"
              success={true}
              defaultValue="Correct input"
            />
            <BodySmall className="text-success flex items-center gap-1 mt-1">
              <CheckCircle2 size={14} /> Input is valid
            </BodySmall>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="disabled-input">Disabled Input</Label>
            <Input 
              id="disabled-input"
              placeholder="This input is disabled"
              className="w-full"
              disabled
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="interactive-input">Interactive Input</Label>
            <Input 
              id="interactive-input"
              placeholder="Type something and click validate..."
              className="w-full"
              value={inputValue}
              onChange={handleInputChange}
              error={hasError}
              success={hasSuccess}
            />
            {hasError && (
              <BodySmall className="text-error flex items-center gap-1 mt-1">
                <AlertCircle size={14} /> Input cannot be empty
              </BodySmall>
            )}
            {hasSuccess && (
              <BodySmall className="text-success flex items-center gap-1 mt-1">
                <CheckCircle2 size={14} /> Input validated successfully
              </BodySmall>
            )}
            <div className="mt-2">
              <Button onClick={validateInput} size="sm">
                Validate
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Component Combinations Section */}
      <section className="space-y-default">
        <H2>Component Combinations</H2>
        
        <Card>
          <CardHeader>
            <CardTitle>Form Example</CardTitle>
            <CardDescription>A sample form using multiple components</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input id="username" placeholder="Enter your username" className="w-full" />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="Enter your email" className="w-full" />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="Enter your password" className="w-full" />
              <BodySmall className="text-neutral mt-1">
                Password must be at least 8 characters long
              </BodySmall>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end space-x-2">
            <Button variant="ghost">Cancel</Button>
            <Button>Submit</Button>
          </CardFooter>
        </Card>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="flex flex-col justify-between">
            <div>
              <CardHeader>
                <CardTitle>Basic Plan</CardTitle>
                <CardDescription>For individuals and small projects</CardDescription>
              </CardHeader>
              <CardContent>
                <BodyLarge className="font-bold text-primary-purple">$9.99 / month</BodyLarge>
                <ul className="mt-4 space-y-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>10 GB storage</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>2 users</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>Basic support</Body>
                  </li>
                </ul>
              </CardContent>
            </div>
            <CardFooter>
              <Button variant="secondary" className="w-full">Choose Plan</Button>
            </CardFooter>
          </Card>
          
          <Card className="flex flex-col justify-between relative border-2 border-primary-purple">
            <div className="absolute top-0 right-0 bg-primary-purple text-white px-3 py-1 rounded-bl-lg rounded-tr-lg">
              <BodySmall>Most Popular</BodySmall>
            </div>
            <div>
              <CardHeader>
                <CardTitle>Pro Plan</CardTitle>
                <CardDescription>For professional users and teams</CardDescription>
              </CardHeader>
              <CardContent>
                <BodyLarge className="font-bold text-primary-purple">$24.99 / month</BodyLarge>
                <ul className="mt-4 space-y-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>50 GB storage</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>10 users</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>Priority support</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>Advanced features</Body>
                  </li>
                </ul>
              </CardContent>
            </div>
            <CardFooter>
              <Button className="w-full">Choose Plan</Button>
            </CardFooter>
          </Card>
          
          <Card className="flex flex-col justify-between">
            <div>
              <CardHeader>
                <CardTitle>Enterprise Plan</CardTitle>
                <CardDescription>For large organizations</CardDescription>
              </CardHeader>
              <CardContent>
                <BodyLarge className="font-bold text-primary-purple">$99.99 / month</BodyLarge>
                <ul className="mt-4 space-y-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>Unlimited storage</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>Unlimited users</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>24/7 dedicated support</Body>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={16} className="text-success" />
                    <Body>Custom integrations</Body>
                  </li>
                </ul>
              </CardContent>
            </div>
            <CardFooter>
              <Button variant="secondary" className="w-full">Contact Sales</Button>
            </CardFooter>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default ComponentsExample;
