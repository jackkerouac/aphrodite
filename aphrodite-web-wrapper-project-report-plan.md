# Aphrodite Web Wrapper Project Report Plan

## 1. Analyze the Existing Codebase:

*   **Frontend (Vue.js):**
    *   Examine the structure of the settings components (`ApiSettings.vue`, `AudioSettings.vue`, `ResolutionSettings.vue`, `ReviewSettings.vue`) to understand how the settings data is currently managed.
    *   Identify the events or methods that trigger when a user changes a setting.
*   **Backend (Flask):**
    *   Inspect the existing Flask API (`aphrodite-web/app/__init__.py`) to understand how it handles requests and interacts with the configuration files.
    *   Determine the best way to add new API endpoints for saving the settings.
    *   Identify the functions responsible for reading and writing the YAML configuration files.

## 2. Implement Backend API Endpoints (Flask):

*   Create four new API endpoints in the Flask backend:
    *   `/api/settings/api` to save API settings to `settings.yaml`.
    *   `/api/settings/audio` to save audio settings to `badge_settings_audio.yml`.
    *   `/api/settings/resolution` to save resolution settings to `badge_settings_resolution.yml`.
    *   `/api/settings/review` to save review settings to `badge_settings_review.yml`.
*   Each endpoint will:
    *   Receive the settings data from the frontend as a JSON payload.
    *   Load the corresponding YAML file.
    *   Update the YAML file with the received settings data.
    *   Save the updated YAML file.
    *   Return a success or error response to the frontend.

## 3. Implement Frontend Logic (Vue.js):

*   Modify the settings components to trigger an API call when the user saves the settings.
*   Each component will:
    *   Capture the current state of the settings.
    *   Send a POST request to the corresponding Flask API endpoint with the settings data as a JSON payload.
    *   Handle the success or error response from the API.
    *   Display a success or error message to the user.

## 4. Update Configuration Files:

*   Modify the Flask backend to correctly read and write the `settings.yaml` file.
*   Ensure that the backend can handle the different data structures in each YAML file.

## 5. Testing:

*   Test each settings component to ensure that the settings are saved correctly.
*   Verify that the settings are loaded correctly when the application starts.
*   Test error handling to ensure that the application gracefully handles errors.

## 6. Modify Vue Components:

*   Add `getSettings` method to `ApiSettings.vue` to return the settings data.
*   Modify `saveSettings` method in `SettingsView.vue` to call the API endpoints.
*   Add `getSettings` method to `AudioSettings.vue` to return the settings data.
*   Modify `saveSettings` method in `AudioSettings.vue` to call the API endpoint.
*   Add `getSettings` method to `ResolutionSettings.vue` to return the settings data.
*   Modify `saveSettings` method in `ResolutionSettings.vue` to call the API endpoint.
*   Add `getSettings` method to `ReviewSettings.vue` to return the settings data.
*   Modify `saveSettings` method in `ReviewSettings.vue` to call the API endpoint.

## 7. Modify Flask Backend:

*   Add new routes to the `config.py` file to handle the new API endpoints.
*   Modify the `update_config` method to handle the different data structures in each YAML file.