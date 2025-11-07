# CrewAI Runner Frontend

React/Vite frontend for the CrewAI Runner application.

## 🚀 Quick Start

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file to configure the frontend:

```env
VITE_CREWAI_RUNNER_API_HOST=http://localhost:8000/api
VITE_CREWAI_API_TOKEN=your-api-token-here
```

**Configuration Options:**
- **`VITE_CREWAI_RUNNER_API_HOST`**: API endpoint URL (required)
- **`VITE_CREWAI_API_TOKEN`**: Bearer token for authentication (optional)

**Authentication:**
The frontend supports multiple ways to set the API token:
1. **Environment Variable**: Set `VITE_CREWAI_API_TOKEN` during build
2. **Runtime UI**: Use the AuthTokenManager component to set token at runtime
3. **Auto-detection**: Token is automatically loaded from localStorage on app start

Tokens set via the UI are stored in localStorage and persist across browser sessions.

## 🔧 Configuration Menu

The frontend includes a built-in **Configuration Menu** component that provides:

### Runtime Configuration
- **API Endpoint Management**: Change server URLs without rebuilding the application
- **Authentication Token Management**: Set, test, and clear Bearer tokens
- **Connection Monitoring**: Real-time connectivity status with latency metrics
- **Settings Persistence**: All configuration is saved to localStorage

### Usage

Import and use the `ConfigurationMenu` component:

```tsx
import { ConfigurationMenu } from "@/components/ConfigurationMenu";

function App() {
  return (
    <div>
      <ConfigurationMenu />
    </div>
  );
}
```

### Features

- ⚙️ **Live Configuration**: Change settings without restarting the application
- 🔗 **Connection Testing**: Test API connectivity with custom endpoints
- 🔐 **Token Validation**: Real-time authentication testing
- 💾 **Automatic Persistence**: Settings saved to browser localStorage
- 🔄 **Reset Functionality**: Easily revert unsaved changes
- 📊 **Status Monitoring**: Visual connection status with latency display

### Development

For local development, the default configuration points to `http://localhost:8000/api`.

### Production

For production builds, set `CREWAI_RUNNER_API_HOST` in your main `.env` file. The Docker build process will use this value automatically.

## 🏗️ Build

```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

## 🐳 Docker

The frontend is containerized and configured to work with the CrewAI Runner API through environment variables.
