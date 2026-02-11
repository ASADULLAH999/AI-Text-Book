import React from 'react';
import { Redirect } from '@docusaurus/router';

// AUTHENTICATION DISABLED - Redirect to documentation
export default function GitHubCallback() {
  return <Redirect to="/docs/module-1-ros2/" />;
}
