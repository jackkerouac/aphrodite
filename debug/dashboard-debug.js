/**
 * Debug script to test dashboard API endpoints
 * Run this to see what data is actually being returned
 */

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

async function testEndpoint(name, url) {
  console.log(`\n=== Testing ${name} ===`);
  console.log(`URL: ${url}`);
  
  try {
    const response = await fetch(url);
    console.log(`Status: ${response.status}`);
    
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`);
      const text = await response.text();
      console.log(`Response body: ${text}`);
      return null;
    }
    
    const data = await response.json();
    console.log('Response data:');
    console.log(JSON.stringify(data, null, 2));
    return data;
  } catch (error) {
    console.log(`Error: ${error.message}`);
    return null;
  }
}

async function runTests() {
  console.log('Dashboard API Debug Tests');
  console.log('========================');
  
  // Test all relevant endpoints
  await testEndpoint('Analytics Overview', `${API_BASE_URL}/api/v1/analytics/overview`);
  await testEndpoint('System Health', `${API_BASE_URL}/health/detailed`);
  await testEndpoint('Recent Jobs', `${API_BASE_URL}/api/v1/jobs?page=1&per_page=5`);
  await testEndpoint('All Jobs Today', `${API_BASE_URL}/api/v1/jobs?page=1&per_page=50&status=completed`);
  
  console.log('\n=== Tests Complete ===');
}

// Run if this is the main module
if (typeof window === 'undefined') {
  runTests();
}
