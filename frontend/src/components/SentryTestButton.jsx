import React from 'react';
import * as Sentry from '@sentry/react';

/**
 * Test button component to verify Sentry error tracking
 * This component can be added temporarily to any page to test Sentry integration
 */
function SentryTestButton() {
  const handleTestError = () => {
    try {
      // This intentional error will be captured by Sentry
      throw new Error('🧪 Sentry Frontend Test Error - This is your first error!');
    } catch (error) {
      // Manually capture the error to ensure it's sent to Sentry
      Sentry.captureException(error);
      console.error('Test error thrown and captured by Sentry:', error);
    }
  };

  return (
    <button
      onClick={handleTestError}
      className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg shadow-md transition-colors duration-200 flex items-center gap-2"
      title="Click to test Sentry error tracking"
    >
      🐛 Test Sentry Error Tracking
    </button>
  );
}

export default SentryTestButton;
