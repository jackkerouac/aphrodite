import React from "react";
import { Progress } from "@/components/ui";
import { useRunAphrodite } from "./RunAphroditeContext";

export const WorkflowSteps: React.FC = () => {
  const { currentStep, workflowSteps } = useRunAphrodite();
  
  // Calculate progress percentage
  const progressPercentage = ((currentStep + 1) / workflowSteps.length) * 100;

  return (
    <>
      {/* Progress indicator */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Step {currentStep + 1} of {workflowSteps.length}</span>
          <span>{progressPercentage}% Complete</span>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Step indicators */}
      <div className="flex justify-between items-center">
        {workflowSteps.map((step, index) => {
          const StepIcon = step.icon;
          const isActive = index === currentStep;
          const isCompleted = index < currentStep;
          
          return (
            <div key={step.id} className="flex-1">
              <div className={`flex flex-col items-center relative ${index < workflowSteps.length - 1 ? "after:content-[''] after:absolute after:top-6 after:left-[60%] after:right-[-40%] after:h-px after:bg-border" : ""}`}>
                <div className={`
                  rounded-full w-12 h-12 flex items-center justify-center mb-2
                  ${isActive ? "bg-primary text-primary-foreground" : ""}
                  ${isCompleted ? "bg-primary/80 text-primary-foreground" : ""}
                  ${!isActive && !isCompleted ? "bg-muted text-muted-foreground" : ""}
                `}>
                  <StepIcon className="h-6 w-6" />
                </div>
                <span className={`text-sm font-medium ${isActive ? "text-primary" : "text-muted-foreground"}`}>
                  {step.title}
                </span>
                <span className="text-xs text-muted-foreground text-center mt-1 max-w-[100px]">
                  {step.description}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
};
