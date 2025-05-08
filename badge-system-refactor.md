# Badge System Refactor - LLM Context Document

This document provides context for an LLM to understand the current state of the badge system refactor.

## Overview

The goal of this refactor is to improve the modularity and maintainability of the badge system. This includes:

*   Creating modular components for different badge types.
*   Updating the preview page to dynamically render these components.
*   Adding unit tests to ensure the stability of the badge system.

## Completed Tasks

The following tasks have been completed:

1.  **Created a feature branch:** A new branch named `feature/badge-system-refactor` has been created.
2.  **Created a folder structure:** A new directory `src/components/badges` has been created to house the new modular components.
3.  **Set up basic unit tests:** A basic test file `tests/components/badges/Badge.test.jsx` with a simple test case has been created.

## File Structure

The following files are relevant to the badge system refactor:

*   `src/components/badges/`: This directory contains the new modular components for different badge types.
*   `src/components/badges/BadgePreview.tsx`: This component is responsible for rendering the badge preview.
*   `src/components/badges/BadgeControls.tsx`: This component provides controls for configuring the badge settings.
*   `src/pages/preview.tsx`: This page displays the badge preview and allows users to configure the badge settings.
*   `src/pages/settings/audio-badge/`: This directory contains the components and hooks for the audio badge settings.
*   `src/pages/settings/resolution-badge/`: This directory contains the components and hooks for the resolution badge settings.
*   `src/pages/settings/review-badge/`: This directory contains the components and hooks for the review badge settings.
*   `src/hooks/useBadgeSettings.ts`: This hook provides access to the badge settings.
*   `src/services/badgeRenderer.ts`: This service is responsible for rendering the badge.
*   `src/services/badgeStorageService.ts`: This service is responsible for storing the badge settings.
*   `tests/components/badges/Badge.test.jsx`: This file contains the basic unit tests for the badge system.

## Next Steps

The next steps in the badge system refactor include:

*   Implementing the modular components for different badge types.
*   Updating the preview page to dynamically render these components.
*   Adding more unit tests to ensure the stability of the badge system.