# Aphrodite Badge System Refactoring Plan - Phase 1 Audit

**Overview:**

This document summarizes the findings of the audit of the existing badge settings pages (Audio, Resolution, Review). The goal of this audit is to identify components, data structures, and state management techniques used in each page to inform the refactoring process.

**1. Information Gathering:**

*   Use `list_files` to get a list of files in the `src/pages/settings` directory.
*   Use `read_file` to read the contents of the `src/pages/settings/audio-badge/index.tsx`, `src/pages/settings/resolution-badge/index.tsx`, and `src/pages/settings/review-badge/index.tsx` files.

**2. Analysis:**

*   Analyze the code to identify components, data structures, and state management techniques used in each badge settings page.

**3. Documentation:**

*   Create a document summarizing the findings, including reusable components, components to be deprecated, data structures, and state management for each badge type.

**4. Clarification:**

*   Ask clarifying questions to ensure a clear understanding of the requirements and scope of the refactoring.

**5. Presentation:**

*   Present the plan to the user for review and approval.

**6. Write to File:**

*   Write the plan to a markdown file.

**7. Switch Mode:**

*   Use the `switch_mode` tool to request that the user switch to another mode to implement the solution.

**Findings:**

*   **Common Components:** `SettingsForm`, `PreviewPanel`, `Alert`, `AlertDescription`
*   **Data Structures:** Each badge settings page uses a `settings` object and constants for options.
*   **State Management:** Each badge settings page uses `useState` and a custom hook (`useAudioBadgeSettings`, `useResolutionBadgeSettings`, `useReviewBadgeSettings`).
*   **Reusable Components:** `SettingsForm`, `PreviewPanel`
*   **Components to be Deprecated:** Specific components within each badge settings page (e.g., `AppearanceControls`, `AudioCodecSelector`, `PositionSelector`, `ShadowControls`, `SizeControls` in `audio-badge`).

The unified Preview page must use React and TypeScript.

**Database Schema Updates:**

```sql
-- Create the badges table
CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    media_item_id VARCHAR(255) NOT NULL, -- e.g., Jellyfin item ID
    badge_type VARCHAR(255) NOT NULL, -- e.g., "resolution", "audio", "review"
    position_x NUMERIC(5, 2) NOT NULL, -- Percentage of poster width (0.00 - 100.00)
    position_y NUMERIC(5, 2) NOT NULL, -- Percentage of poster height (0.00 - 100.00)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add a trigger to update the updated_at column
CREATE TRIGGER update_badges_modtime
BEFORE UPDATE ON badges
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();
```