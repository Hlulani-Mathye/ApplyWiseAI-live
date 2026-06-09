export const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
async function req(path, options={}){
  const res = await fetch(`${API}${path}`, options);
  if(!res.ok){ throw new Error(await res.text()); }
  return res.json();
}
export const api = {
  profile: () => req('/profile'),
  saveProfile: (data) => req('/profile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}),
  uploadDoc: (file, type='CV') => { const fd = new FormData(); fd.append('file', file); return req(`/documents?doc_type=${encodeURIComponent(type)}`, {method:'POST', body: fd}); },
  docs: () => req('/documents'),
  fetchJobs: (keyword) => req(`/jobs/fetch?keyword=${encodeURIComponent(keyword)}`, {method:'POST'}),
  jobs: () => req('/jobs'),
  matches: (threshold=50) => req(`/matches?threshold=${threshold}`),
  apply: (jobId) => req(`/applications/${jobId}?status=Ready%20to%20Apply`, {method:'POST'}),
  applications: () => req('/applications'),
  updateApp: (id,status,notes='') => req(`/applications/${id}?status=${encodeURIComponent(status)}&notes=${encodeURIComponent(notes)}`, {method:'PATCH'})
}
