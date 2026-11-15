import { writeFile, mkdir } from 'node:fs/promises';

const login = process.env.GH_PROFILE || 'Thrash-PRX';
const token = process.env.GH_TOKEN;
if (!token) throw new Error('GH_TOKEN is required. In GitHub Actions, the built-in token is used.');
if (!/^[a-zA-Z0-9-]{1,39}$/.test(login)) throw new Error('Invalid GitHub username.');

// The calendar belongs to the public profile. Never query private repositories,
// restricted contributions, contact information, or account credentials.
const query = `query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}`;
const response = await fetch('https://api.github.com/graphql', {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', 'User-Agent': 'thrash-profile-artwork' },
  body: JSON.stringify({ query, variables: { login } }),
  signal: AbortSignal.timeout(30000)
});
if (!response.ok) throw new Error(`GitHub request failed (${response.status}). Existing artwork was preserved.`);
const result = await response.json();
if (result.errors?.length || !result.data?.user) throw new Error('GitHub did not return a complete calendar. Existing artwork was preserved.');
const days = result.data.user.contributionsCollection.contributionCalendar.weeks.flatMap(w => w.contributionDays);
if (!days.length || days.some(d => !/^\d{4}-\d{2}-\d{2}$/.test(d.date) || !Number.isInteger(d.contributionCount) || d.contributionCount < 0)) {
  throw new Error('Unexpected calendar data. Existing artwork was preserved.');
}
await mkdir(new URL('../data/', import.meta.url), { recursive: true });
await writeFile(new URL('../data/activity.json', import.meta.url), JSON.stringify({
  login,
  capturedAt: new Date().toISOString(),
  source: 'GitHub public contribution calendar',
  days: days.slice(-365)
}, null, 2) + '\n');
await import('./build.mjs');

