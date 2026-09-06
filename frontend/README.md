# Trizen Challenge Frontend

This is the frontend for the Trizen Challenge photo-sharing platform built with React and TypeScript.

## Getting Started

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

3. The app will be available at http://localhost:3000

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm build`: Builds the app for production
- `npm test`: Runs the test suite
- `npm eject`: Ejects from Create React App

## Project Structure

- `src/components`: Reusable UI components
- `src/pages`: Page components
- `src/services`: API service layers
- `src/contexts`: React contexts (Auth)
- `src/styles`: CSS files
- `src/utils`: Utility functions
- `src/hooks`: Custom React hooks
- `public`: Static assets

## Features

- User authentication (login/register)
- Event management (create, view, list)
- Photo upload functionality
- Membership management
- PIN-protected gallery access
- Responsive design

## API Integration

The frontend communicates with the backend API at `http://localhost:8000/api` by default. This can be configured via the `REACT_APP_API_URL` environment variable.

