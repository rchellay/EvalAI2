import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";
import App from "./App";
import "./styles-tailwind.css"; // tailwind base first
import "./styles.css"; // custom overrides

Sentry.init({
  dsn: "https://1cb748bb65122ab361607892eca4d04f@o4510346772938752.ingest.de.sentry.io/4510346831986768",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  // Performance Monitoring
  tracesSampleRate: 1.0, // Capture 100% of transactions
  // Session Replay
  replaysSessionSampleRate: 0.1, // Sample 10% of sessions
  replaysOnErrorSampleRate: 1.0, // Sample 100% of sessions with errors
  // Setting this option to true will send default PII data to Sentry.
  sendDefaultPii: true,
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
