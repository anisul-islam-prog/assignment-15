import http from 'k6/http';
import { check, sleep } from 'k6';

// Test configuration: ramp up to 100 VUs over 2 minutes
export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Ramp up to 50 users
    { duration: '1m', target: 100 },   // Ramp up to 100 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% of requests under 500ms
    http_req_failed: ['rate<0.05'],     // Error rate under 5%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export default function () {
  // Test 1: Health check
  let healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
    'health response time < 200ms': (r) => r.timings.duration < 200,
  });

  // Test 2: Create a task
  let payload = JSON.stringify({ title: `Task ${__VU}-${__ITER}`, done: false });
  let headers = { 'Content-Type': 'application/json' };
  let createRes = http.post(`${BASE_URL}/tasks`, payload, { headers });
  check(createRes, {
    'create status is 201': (r) => r.status === 201,
    'create response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test 3: Get all tasks
  let getRes = http.get(`${BASE_URL}/tasks`);
  check(getRes, {
    'get status is 200': (r) => r.status === 200,
    'get response time < 300ms': (r) => r.timings.duration < 300,
  });

  sleep(1); // Think time between iterations
}