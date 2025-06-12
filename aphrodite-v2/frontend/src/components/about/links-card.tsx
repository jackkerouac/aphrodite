import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ExternalLink, Link, Github } from 'lucide-react';
import { LinkItem, defaultLinks } from './types';

interface LinksCardProps {
  links?: LinkItem[];
}

function LinkItemComponent({ link }: { link: LinkItem }) {
  const getIcon = (iconType: string) => {
    switch (iconType) {
      case 'github':
        return <Github className="h-6 w-6" />;
      case 'website':
        return <Link className="h-6 w-6" />;
      default:
        return <Link className="h-6 w-6" />;
    }
  };

  return (
    <a
      href={link.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center justify-between p-4 bg-muted rounded-lg hover:bg-muted/80 transition-colors group"
    >
      <div className="flex items-center gap-3">
        {getIcon(link.icon)}
        <div>
          <div className="font-semibold">{link.title}</div>
          <div className="text-sm text-muted-foreground">{link.description}</div>
        </div>
      </div>
      <ExternalLink className="h-5 w-5 text-muted-foreground group-hover:text-foreground transition-colors" />
    </a>
  );
}

export function LinksCard({ links = defaultLinks }: LinksCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Link className="h-6 w-6" />
          Links
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {links.map((link, index) => (
            <LinkItemComponent key={index} link={link} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
