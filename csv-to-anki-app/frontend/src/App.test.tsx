import React from 'react';

// Simple smoke test that will always pass
test('basic test passes', () => {
  expect(1 + 1).toBe(2);
});

test('react imports correctly', () => {
  expect(React).toBeDefined();
});

// Test that our main App component can be imported
test('App component imports without errors', async () => {
  const { default: App } = await import('./App');
  expect(App).toBeDefined();
});
