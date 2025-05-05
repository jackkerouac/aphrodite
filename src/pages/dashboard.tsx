import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Database, Film, Tv, Book, Music } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import useJellyfinLibraries from "@/hooks/useJellyfinLibraries";

// Function to get an icon based on library type/name
const getLibraryIcon = (name: string) => {
  name = name.toLowerCase();
  
  if (name.includes("movie") || name.includes("film")) return Film;
  if (name.includes("tv") || name.includes("show") || name.includes("series")) return Tv;
  if (name.includes("book") || name.includes("audio")) return Book;
  if (name.includes("music")) return Music;
  
  return Database; // Default icon
};

// Library Card Component
const LibraryCard = ({ name, itemCount }: { name: string, itemCount: number }) => {
  const Icon = getLibraryIcon(name);
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center">
          <Icon className="h-5 w-5 mr-2 text-muted-foreground" />
          <CardTitle className="text-lg">{name}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{itemCount.toLocaleString()}</div>
        <p className="text-xs text-muted-foreground mt-1">Total Items</p>
        <Progress className="h-2 mt-3" value={100} />
      </CardContent>
    </Card>
  );
};

// Library Status Card Component
const LibraryStatusCard = ({ libraries, isLoading, error }: { 
  libraries: any[], 
  isLoading: boolean, 
  error: string | null 
}) => {
  const totalItems = libraries.reduce((sum, lib) => sum + lib.itemCount, 0);
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Library Status
          </CardTitle>
          <CardDescription>Overview of your media library</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Library Status</CardTitle>
          <CardDescription>Overview of your media library</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (libraries.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Library Status</CardTitle>
          <CardDescription>Overview of your media library</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>
              No libraries found. Please configure your Jellyfin connection in settings.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Database className="h-5 w-5 mr-2" />
          Library Status
        </CardTitle>
        <CardDescription>Overview of your media library</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{totalItems.toLocaleString()}</div>
        <p className="text-sm text-muted-foreground mt-1 mb-4">Total items across all libraries</p>
        
        <div className="space-y-1">
          {libraries.map((library) => (
            <div key={library.id} className="flex justify-between items-center">
              <div className="flex items-center">
                {React.createElement(getLibraryIcon(library.name), { className: "h-4 w-4 mr-2 text-muted-foreground" })}
                <span>{library.name}</span>
              </div>
              <span className="text-muted-foreground">{library.itemCount.toLocaleString()} items</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default function Dashboard() {
  const { libraries, isLoading, error } = useJellyfinLibraries();
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      
      {/* Library Status Card */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <LibraryStatusCard 
          libraries={libraries} 
          isLoading={isLoading} 
          error={error} 
        />
        
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest jobs and processing</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Recent activity will appear here.</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Connection and resource metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <p>System status information will appear here.</p>
          </CardContent>
        </Card>
      </div>
      
      {/* Individual Library Cards */}
      {!isLoading && !error && libraries.length > 0 && (
        <>
          <h2 className="text-2xl font-bold tracking-tight mt-8">Libraries</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {libraries.map((library) => (
              <LibraryCard 
                key={library.id} 
                name={library.name} 
                itemCount={library.itemCount} 
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
