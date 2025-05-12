import React from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface UnsavedChangesAlertProps {
  isOpen: boolean;
  onCancel: () => void;
  onContinue: () => void;
}

/**
 * Alert dialog shown when there are unsaved changes and user attempts to navigate away
 */
export const UnsavedChangesAlert: React.FC<UnsavedChangesAlertProps> = ({
  isOpen,
  onCancel,
  onContinue,
}) => {
  return (
    <AlertDialog open={isOpen}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Unsaved Changes</AlertDialogTitle>
          <AlertDialogDescription>
            You have unsaved changes that will be lost if you continue.
            Would you like to save your changes first?
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={onCancel}>
            Save Changes
          </AlertDialogCancel>
          <AlertDialogAction onClick={onContinue}>
            Discard Changes
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default UnsavedChangesAlert;
