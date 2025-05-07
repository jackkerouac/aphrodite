# Typography System Usage Guide

This document explains how to use the Aphrodite typography system in your components.

## Available Components

The typography system provides the following components:

- `H1` - Page titles, overlays (30px, Bold)
- `H2` - Section headers, cards (24px, Semibold)
- `H3` - Subsection headings (20px, Medium)
- `BodyLarge` - Dialog content, modals (16px, Regular)
- `Body` - Primary UI content (14px, Regular) 
- `BodySmall` - Labels, metadata, table headers (12px, Medium)
- `CodeText` - Metadata tags, IDs (13px, Medium, Monospace)
- `Label` - Form field labels (12px, Medium)
- `Subtitle` - Descriptive text under headings (14px, Regular, Neutral color)

## Basic Usage

Import the typography components in your React component:

```jsx
import { H1, H2, Body, BodySmall } from '../components/ui/typography';

const MyComponent = () => {
  return (
    <div>
      <H1>Page Title</H1>
      <H2>Section Header</H2>
      <Body>This is the main content text.</Body>
      <BodySmall>Last updated: May 7, 2025</BodySmall>
    </div>
  );
};
```

## Customizing Styles

All typography components accept a `className` prop for additional styling:

```jsx
<H1 className="mb-4 text-primary-purple">Custom Heading</H1>
<Body className="italic text-neutral">Custom body text</Body>
```

## Typography with Tailwind Utilities

You can also use Tailwind's typography utilities directly:

```jsx
<h1 className="text-h1 text-dark dark:text-[#F3F4F6]">Heading One</h1>
<p className="text-body-large text-dark dark:text-[#F3F4F6]">Large paragraph</p>
```

## Dynamic Text Styling

For conditional styling:

```jsx
<Body className={status === 'error' ? 'text-error' : 'text-success'}>
  Status message
</Body>
```

## Typography in Cards

Example of using typography in a card component:

```jsx
import { Card } from '../components/ui/card';
import { H3, Body, BodySmall } from '../components/ui/typography';

const InfoCard = ({ title, content, date }) => (
  <Card>
    <H3 className="mb-2">{title}</H3>
    <Body className="mb-4">{content}</Body>
    <BodySmall className="text-neutral">{date}</BodySmall>
  </Card>
);
```

## Form Labels

Example of using the Label component with form fields:

```jsx
import { Label, BodySmall } from '../components/ui/typography';

const FormField = ({ id, label, error, children }) => (
  <div className="mb-4">
    <Label htmlFor={id}>{label}</Label>
    {children}
    {error && (
      <BodySmall className="mt-1 text-error">{error}</BodySmall>
    )}
  </div>
);
```

## Text Truncation

Use with Tailwind's truncation utilities:

```jsx
<H2 className="truncate max-w-md">
  This is a very long heading that will be truncated
</H2>

<Body className="line-clamp-2">
  This text will be limited to two lines maximum, and any additional content
  will be truncated with an ellipsis at the end of the second line.
</Body>
```

## Best Practices

1. Use the appropriate component for each context (H1 for page titles, H2 for sections, etc.)
2. Maintain hierarchy - don't skip levels (e.g., don't jump from H1 to H3)
3. Use dark mode compatible components (they already include dark mode classes)
4. For form labels, always use the `Label` component and associate it with inputs
5. For metadata or secondary information, use `BodySmall` or `Subtitle` components
6. For code or technical information, use the `CodeText` component