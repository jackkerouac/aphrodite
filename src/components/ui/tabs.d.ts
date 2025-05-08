import * as React from "react";

export interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  defaultValue?: string;
  className?: string;
  children: React.ReactNode;
}

export const Tabs: React.ForwardRefExoticComponent<
  TabsProps & React.RefAttributes<HTMLDivElement>
>;

export interface TabsListProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
  children: React.ReactNode;
}

export const TabsList: React.ForwardRefExoticComponent<
  TabsListProps & React.RefAttributes<HTMLDivElement>
>;

export interface TabsTriggerProps extends React.HTMLAttributes<HTMLButtonElement> {
  value: string;
  className?: string;
  children: React.ReactNode;
}

export const TabsTrigger: React.ForwardRefExoticComponent<
  TabsTriggerProps & React.RefAttributes<HTMLButtonElement>
>;

export interface TabsContentProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
  className?: string;
  children: React.ReactNode;
}

export const TabsContent: React.ForwardRefExoticComponent<
  TabsContentProps & React.RefAttributes<HTMLDivElement>
>;