# Component Usage Guide

This document explains how to use the core UI components from the Aphrodite style guide.

## Button Component

The Button component provides a flexible and customizable button with multiple variants and sizes.

### Basic Usage

```jsx
import { Button } from '../components/ui/button';

const MyComponent = () => {
  return (
    <div>
      <Button>Primary Button</Button>
      <Button variant="secondary">Secondary Button</Button>
      <Button variant="destructive">Delete</Button>
    </div>
  );
};
```

### Button Variants

- `primary` (default) - Background: `#4C1D95`, Text: white
- `secondary` - Border: `#4C1D95`, Text: `#4C1D95`, Background: transparent
- `icon` - Designed for icon buttons with minimal padding
- `ghost` - Transparent background with hover effect
- `link` - Text-only button with underline on hover
- `destructive` - Red background for destructive actions

### Button Sizes

- `default` - Height: 48px (12rem)
- `sm` - Height: 40px (10rem)
- `lg` - Height: 56px (14rem)
- `icon` - Square button for icons

### Additional Props

- `asChild` - Use the button as a wrapper (useful with Radix Slot)
- `disabled` - Disable the button

### Examples

```jsx
// Icon button
import { Button } from '../components/ui/button';
import { Heart, Bell, Search } from 'lucide-react';

const IconButtons = () => {
  return (
    <div className="flex space-x-2">
      <Button variant="icon" size="icon">
        <Heart size={20} />
      </Button>
      <Button variant="icon" size="icon">
        <Bell size={20} />
      </Button>
      <Button variant="icon" size="icon">
        <Search size={20} />
      </Button>
    </div>
  );
};

// Button with custom styles
<Button 
  className="bg-gradient-to-r from-primary-purple to-accent-indigo"
>
  Gradient Button
</Button>
```

## Card Component

The Card component provides a container for content with consistent styling and hover effects.

### Basic Usage

```jsx
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent,
  CardFooter 
} from '../components/ui/card';

const MyCard = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card description or subtitle</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Main content area of the card</p>
      </CardContent>
      <CardFooter>
        <Button>Action</Button>
      </CardFooter>
    </Card>
  );
};
```

### Card Components

- `Card` - Main container
- `CardHeader` - Header section (typically contains title and description)
- `CardTitle` - Title element (h3)
- `CardDescription` - Subtitle or description text
- `CardContent` - Main content area
- `CardFooter` - Footer section (typically contains actions)

### Customizing Cards

```jsx
// Card with custom background
<Card className="bg-secondary-lilac border border-primary-purple">
  {/* Card content */}
</Card>

// Card with icon in title
import { Settings } from 'lucide-react';

<CardTitle className="flex items-center gap-2">
  <Settings size={20} className="text-primary-purple" />
  Settings
</CardTitle>
```

## Input Component

The Input component provides a styled text input field with support for different states.

### Basic Usage

```jsx
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/typography';

const MyInput = () => {
  return (
    <div className="space-y-2">
      <Label htmlFor="my-input">Email</Label>
      <Input 
        id="my-input"
        type="email"
        placeholder="Enter your email"
      />
    </div>
  );
};
```

### Input States

- Default - Regular input state
- Error - Red border (pass `error={true}`)
- Success - Green border (pass `success={true}`)
- Disabled - Grayed out (pass `disabled`)

### Input Types

The Input component supports all standard HTML input types:

```jsx
// Text input (default)
<Input placeholder="Enter text" />

// Password input
<Input type="password" placeholder="Enter password" />

// Email input
<Input type="email" placeholder="Enter email" />

// Number input
<Input type="number" placeholder="Enter amount" />
```

### Form Integration

```jsx
import { useState } from 'react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Label, BodySmall } from '../components/ui/typography';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

const FormExample = () => {
  const [value, setValue] = useState('');
  const [error, setError] = useState(false);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!value.trim()) {
      setError(true);
    } else {
      setError(false);
      // Process form
      console.log('Submitted:', value);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="username">Username</Label>
        <Input 
          id="username"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          error={error}
          placeholder="Enter username"
        />
        {error && (
          <BodySmall className="text-error flex items-center gap-1">
            <AlertCircle size={14} /> Username is required
          </BodySmall>
        )}
      </div>
      <Button type="submit">Submit</Button>
    </form>
  );
};
```

## Component Composition

These components are designed to work together seamlessly:

```jsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { H2, Label, BodySmall } from '../components/ui/typography';

const LoginForm = () => {
  return (
    <div className="w-full max-w-md mx-auto">
      <H2 className="mb-4 text-center">Login</H2>
      
      <Card>
        <CardHeader>
          <CardTitle>Welcome Back</CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input 
              id="email" 
              type="email" 
              placeholder="Enter your email"
              className="w-full"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input 
              id="password" 
              type="password" 
              placeholder="Enter your password"
              className="w-full"
            />
            <BodySmall className="text-neutral">
              Forgot password? <Button variant="link" className="p-0 h-auto">Reset it</Button>
            </BodySmall>
          </div>
        </CardContent>
        
        <CardFooter>
          <Button className="w-full">Login</Button>
        </CardFooter>
      </Card>
    </div>
  );
};
```

## Best Practices

1. Use appropriate button variants for different actions (primary for main actions, secondary for alternative actions)
2. Maintain consistent spacing with the spacing system
3. Use typography components for consistent text styling
4. Always use Labels with Input fields
5. Group related form fields in Card components
6. Use appropriate visual feedback for form states (error, success)
7. Consider mobile responsiveness in your layouts
