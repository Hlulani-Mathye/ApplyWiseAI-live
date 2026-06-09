import React, {useEffect, useState} from 'react';
import { createRoot } from 'react-dom/client';
import { Briefcase, User, FileText, Target, Send, RefreshCw, ExternalLink, CheckCircle2 } from 'lucide-react';
import { api } from './lib/api';
import './style.css';

const defaultProfile = {
  full_name:'Hlulani Isaac Mathye', email:'', phone:'', location:'Pretoria / Johannesburg, South Africa',
  target_roles:'WIL Placement, IT Internship, Cloud Support, Data Analyst, Business Analyst, Software Developer Intern',
  skills:'Python, SQL, Java, HTML, CSS, JavaScript, React, FastAPI, AWS, Huawei Cloud, Linux, Systems Analysis, Business Analysis',
  education:'Diploma in Informatics, Tshwane University of Technology',
  experience:'Student projects in web systems, cloud training, database systems, systems analysis and job application automation idea.',
  certifications:'Huawei Cloud training, AWS learning, OCI roadmap, Huawei ICT Competition regional finalist'
};
function Badge({children}){ return <span className="badge">{children}</span> }
function Card({title, icon, children}){ return <section className="card"><h2>{icon}{title}</h2>{children}</section> }
function App(){
  const [profile,setProfile]=useState(defaultProfile); const [docs,setDocs]=useState([]); const [jobs,setJobs]=useState([]); const [matches,setMatches]=useState([]); const [apps,setApps]=useState([]); const [keyword,setKeyword]=useState('IT internship WIL'); const [loading,setLoading]=useState(''); const [message,setMessage]=useState('');
  const load=async()=>{ try{ const p=await api.profile(); if(p) setProfile(p); setDocs(await api.docs()); setJobs(await api.jobs()); setApps(await api.applications()); }catch(e){} };
  useEffect(()=>{load()},[]);
  async function saveProfile(e){e.preventDefault(); setLoading('profile'); try{await api.saveProfile(profile); setMessage('Profile saved.'); await load();}catch(e){setMessage(e.message)} setLoading('');}
  async function upload(e){ const file=e.target.files[0]; if(!file) return; setLoading('doc'); try{await api.uploadDoc(file,'CV'); setMessage('Document uploaded and text extracted.'); await load();}catch(e){setMessage(e.message)} setLoading('');}
  async function fetchJobs(){ setLoading('jobs'); try{ const r=await api.fetchJobs(keyword); setJobs(r.jobs); setMessage(`Fetched ${r.count} live jobs from Graduates24 and Careers24.`); }catch(e){setMessage('Could not fetch some jobs. '+e.message)} setLoading('');}
  async function runMatch(){ setLoading('match'); try{ setMatches(await api.matches(40)); setMessage('Matching completed.'); }catch(e){setMessage(e.message)} setLoading('');}
  async function createApp(jobId){ setLoading('apply'); try{await api.apply(jobId); setApps(await api.applications()); setMessage('Application pack created. Review before submitting on the original website.');}catch(e){setMessage(e.message)} setLoading('');}
  return <main>
    <header className="hero"><div><p className="eyebrow">ApplyWise AI Live</p><h1>AI-powered job matching and application assistant</h1><p>Fetches real opportunities from Graduates24 and Careers24, matches them to your profile, generates application packs, and tracks progress with human approval.</p></div><div className="stats"><b>{jobs.length}</b><span>Live jobs saved</span><b>{matches.length}</b><span>Matches</span><b>{apps.length}</b><span>Applications tracked</span></div></header>
    {message && <div className="notice">{message}</div>}
    <div className="grid two">
      <Card title="Candidate Profile" icon={<User/>}><form onSubmit={saveProfile} className="form">{['full_name','email','phone','location','target_roles','skills','education','experience','certifications'].map(k=><label key={k}>{k.replaceAll('_',' ')}<textarea rows={k==='skills'||k==='experience'?3:1} value={profile[k]||''} onChange={e=>setProfile({...profile,[k]:e.target.value})}/></label>)}<button disabled={loading==='profile'}><CheckCircle2/> Save Profile</button></form></Card>
      <Card title="CV & Document Management" icon={<FileText/>}><p>Upload your CV, transcript, certificates, WIL letter, or cover letter templates. The backend extracts text for matching.</p><input type="file" onChange={upload} accept=".pdf,.doc,.docx,.txt,.md" /> <div className="list">{docs.map(d=><div className="row" key={d.id}><b>{d.filename}</b><Badge>{d.doc_type}</Badge><small>{d.extracted_text?.slice(0,120)}</small></div>)}</div></Card>
    </div>
    <Card title="Live Job Fetching" icon={<RefreshCw/>}><div className="inline"><input value={keyword} onChange={e=>setKeyword(e.target.value)} placeholder="e.g. IT internship, WIL, data analyst"/><button onClick={fetchJobs} disabled={loading==='jobs'}><RefreshCw/> Fetch Live Jobs</button><button onClick={runMatch} disabled={loading==='match'}><Target/> Match Jobs</button></div><p className="muted">Sources: Graduates24 internships/graduate/learnership/entry pages and Careers24 keyword searches.</p></Card>
    <Card title="Best Matches" icon={<Target/>}><div className="jobs">{matches.map(({job,score,matched_keywords,missing_keywords})=><article className="job" key={job.id}><div><h3>{job.title}</h3><p>{job.source} • {job.location} • {job.closing_date||job.posted_date}</p><p>{job.description?.slice(0,220)}...</p><div>{matched_keywords.slice(0,8).map(x=><Badge key={x}>{x}</Badge>)}</div></div><div className="actions"><strong>{score}%</strong><a href={job.url} target="_blank">Open <ExternalLink size={14}/></a><button onClick={()=>createApp(job.id)}><Send/> Prepare</button></div></article>)}</div></Card>
    <Card title="All Saved Jobs" icon={<Briefcase/>}><div className="jobs compact">{jobs.slice(0,40).map(job=><article className="job" key={job.id}><div><h3>{job.title}</h3><p>{job.source} • {job.location}</p></div><div className="actions"><a href={job.url} target="_blank">Open</a><button onClick={()=>createApp(job.id)}>Track</button></div></article>)}</div></Card>
    <Card title="Application Tracker" icon={<Send/>}><div className="jobs">{apps.map(({application,job})=><article className="job" key={application.id}><div><h3>{job?.title}</h3><p>Status: <Badge>{application.status}</Badge> Match: {application.match_score}%</p><details><summary>Cover letter draft</summary><pre>{application.cover_letter}</pre></details></div><div className="actions"><a href={job?.url} target="_blank">Apply site</a><button onClick={()=>api.updateApp(application.id,'Submitted').then(load)}>Mark submitted</button><button onClick={()=>api.updateApp(application.id,'Interview').then(load)}>Interview</button></div></article>)}</div></Card>
  </main>
}
createRoot(document.getElementById('root')).render(<App/>);
