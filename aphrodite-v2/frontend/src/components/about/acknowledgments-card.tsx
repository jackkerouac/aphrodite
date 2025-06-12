import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart, Github, Award, ExternalLink } from 'lucide-react';
import { AcknowledgmentItem, defaultAcknowledgments } from './types';

interface AcknowledgmentsCardProps {
  acknowledgments?: AcknowledgmentItem[];
}

function AcknowledgmentItemComponent({ item }: { item: AcknowledgmentItem }) {
  return (
    <div className="p-4 bg-muted rounded-lg">
      <div className="flex items-start gap-3">
        <Award className="h-6 w-6 mt-1 text-primary" />
        <div className="flex-1">
          <div className="font-semibold">{item.title}</div>
          <div className="text-sm text-muted-foreground mb-2">
            {item.description}
          </div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm">by</span>
            <a
              href={item.authorUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-primary hover:underline"
            >
              {item.author}
            </a>
          </div>
          <Button variant="outline" size="sm" asChild>
            <a
              href={item.repositoryUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="gap-2"
            >
              <Github className="h-3 w-3" />
              View Repository
            </a>
          </Button>
        </div>
      </div>
    </div>
  );
}

export function AcknowledgmentsCard({ acknowledgments = defaultAcknowledgments }: AcknowledgmentsCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="h-6 w-6" />
          Acknowledgments
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {acknowledgments.map((item, index) => (
            <AcknowledgmentItemComponent key={index} item={item} />
          ))}
          
          <div className="text-center text-sm text-muted-foreground mt-4">
            <p>I appreciate the open-source community and the creators who make their work freely available.</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
