const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function analyzeCSV(file, nSimulations = 1000, noiseStd = 0.05) {
  const formData = new FormData();
  formData.append('file', file);

  const params = new URLSearchParams({
    n_simulations: nSimulations,
    noise_std: noiseStd,
  });

  const res = await fetch(`${API_BASE}/api/analyze?${params}`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.errors?.join(', ') || 'Analysis failed');
  }
  return res.json();
}

export async function analyzeSynthetic({
  business_type = 'stable',
  n_months = 12,
  base_revenue = 500000,
  seed = 42,
  n_simulations = 1000,
  noise_std = 0.05,
} = {}) {
  const res = await fetch(`${API_BASE}/api/synthetic`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ business_type, n_months, base_revenue, seed, n_simulations, noise_std }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.errors?.join(', ') || 'Synthetic analysis failed');
  }
  return res.json();
}

export async function getShocks() {
  const res = await fetch(`${API_BASE}/api/shocks`);
  return res.json();
}

export function formatINR(value) {
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(1)}Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`;
  if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return `₹${value.toFixed(0)}`;
}

export function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}

export async function chatWithData(question, context = {}) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, context }),
  });
  if (!res.ok) {
    throw new Error('Chat request failed');
  }
  return res.json();
}
