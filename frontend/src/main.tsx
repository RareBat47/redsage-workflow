import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import AssetsView from './pages/AssetsView';
import EvidenceLibrary from './pages/EvidenceLibrary';
import FindingsPanel from './components/FindingsPanel';
import HistoryDrawer from './components/HistoryDrawer';
import MentorPanel from './components/MentorPanel';
import ProjectBriefPanel from './components/ProjectBriefPanel';
import WorkflowPlannerPanel from './components/WorkflowPlannerPanel';
import TaskStepsPanel from './components/TaskStepsPanel';
import BossBrainPanel from './components/BossBrainPanel';
import ReadinessPanel from './components/ReadinessPanel';
import ScopeAmendModal from './components/ScopeAmendModal';
import SearchModal from './components/SearchModal';
import ErrorBoundary from './components/ErrorBoundary';
import { API, apiCall } from './services/api';
import { defaultScopeTarget, targetMatchesWhitelist } from './services/scope';
import type { EvidenceItem } from './types';
import './index.css';
import './day2.css';
import './day3.css';
import './brief.css';
import './steps.css';
import './planner.css';
import './boss.css';

type View = 'roadmap' | 'evidence' | 'assets' | 'report' | 'boss';

export default function App() {
  const [projects, setProjects] = useState<any[]>([]);
  const [project, setProject] = useState<any>();
  const [scope, setScope] = useState<any>();
  const [tasks, setTasks] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>();
  const [rawEvidence, setRawEvidence] = useState('');
  const [verdict, setVerdict] = useState<any>();
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [proposals, setProposals] = useState<any[]>([]);
  const [findings, setFindings] = useState<any[]>([]);
  const [report, setReport] = useState('');
  const [view, setView] = useState<View>('roadmap');
  const [error, setError] = useState('');
  const [amendOpen, setAmendOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [importing, setImporting] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [notice, setNotice] = useState('');
  const [activeTarget, setActiveTarget] = useState('');
  const [mentorOpen, setMentorOpen] = useState(false);
  const [selectedStep, setSelectedStep] = useState<any>();
  const [briefOpen, setBriefOpen] = useState(false);
  const [plannerOpen, setPlannerOpen] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const refresh = async (current = project, preferredTarget = activeTarget) => {
    if (!current) return;
    const id = current.id;
    try {
      const nextScope = await apiCall<any>(`/projects/${id}/scope`);
      const whitelist: string[] = nextScope?.in_scope_whitelist ?? [];
      const effective = preferredTarget && targetMatchesWhitelist(preferredTarget, whitelist)
        ? preferredTarget
        : defaultScopeTarget(whitelist);
      if (effective !== preferredTarget) setActiveTarget(effective);
      const [nextTasks, nextProposals, nextFindings, nextEvidence] = await Promise.all([
        apiCall(`/projects/${id}/tasks${effective ? `?target_host=${encodeURIComponent(effective)}` : ''}`),
        apiCall(`/projects/${id}/proposals`), apiCall(`/projects/${id}/findings`),
        apiCall<EvidenceItem[]>(`/projects/${id}/evidence`),
      ]);
       setScope(nextScope); setTasks(nextTasks); setProposals(nextProposals);
       if (selected) {
         const refreshedSelected = nextTasks.flatMap((phase: any) => phase.tasks).find((task: any) => task.id === selected.id);
         setSelected(refreshedSelected);
       }
      setFindings(nextFindings); setEvidence(nextEvidence);
    } catch (err: any) { setError(err.message); }
  };

  useEffect(() => { apiCall<any[]>('/projects').then(setProjects).catch((err) => setError(err.message)); }, []);
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); setSearchOpen(true); }
      if (event.key === 'Escape') { setSearchOpen(false); setHistoryOpen(false); setAmendOpen(false); }
    };
    window.addEventListener('keydown', onKeyDown); return () => window.removeEventListener('keydown', onKeyDown);
  }, []);
  useEffect(() => {
    const preventVerifyDoubleSubmit = (event: MouseEvent) => {
      const target = event.target;
      if (target instanceof HTMLButtonElement && target.textContent?.includes('Verify Evidence')) target.disabled = true;
    };
    document.addEventListener('click', preventVerifyDoubleSubmit, true);
    return () => document.removeEventListener('click', preventVerifyDoubleSubmit, true);
  }, []);
  useEffect(() => {
    if (!verifying) {
      document.querySelectorAll('button').forEach((button) => {
        if (button.textContent?.includes('Verify Evidence')) button.disabled = false;
      });
    }
  }, [verifying]);

  async function createProject() {
    const name = window.prompt('Project name', 'OWASP Juice Shop Audit'); if (!name) return;
    try { const created = await apiCall<any>('/projects', { method: 'POST', body: JSON.stringify({ name }) }); setProjects((current) => [created, ...current]); setProject(created); setActiveTarget(''); await refresh(created, ''); }
    catch (err: any) { setError(err.message); }
  }

  async function configureScope() {
    const targets = window.prompt('Whitelist target (domain/IP)', 'juice-shop.local'); if (!targets || !project) return;
    try { await apiCall(`/projects/${project.id}/scope`, { method: 'PUT', body: JSON.stringify({ in_scope_whitelist: targets.split(',').map((item) => item.trim()), out_of_scope_blacklist: [], max_rate_limit: 10 }) }); await apiCall(`/projects/${project.id}/scope/lock`, { method: 'POST' }); await refresh(); }
    catch (err: any) { setError(err.message); }
  }

  async function verify() {
    if (!project || !selected || verifying) return;
    setVerifying(true);
    try { const result = await apiCall<any>(`/projects/${project.id}/tasks/${selected.id}/verify`, { method: 'POST', body: JSON.stringify({ raw_content: rawEvidence }) }); setVerdict(result); setRawEvidence(''); await refresh(); }
    catch (err: any) { setError(err.message); }
    finally { setVerifying(false); }
  }

  async function loadReport() {
    if (!project) return;
    try { setReport((await apiCall<{ markdown: string }>(`/projects/${project.id}/report`)).markdown); setView('report'); }
    catch (err: any) { setError(err.message); }
  }

  async function approve(proposal: any) { try { await apiCall(`/projects/${project.id}/proposals/${proposal.id}/approve`, { method: 'POST' }); await refresh(); } catch (err: any) { setError(err.message); } }
  async function dismiss(proposal: any) { try { await apiCall(`/projects/${project.id}/proposals/${proposal.id}/dismiss`, { method: 'POST' }); await refresh(); } catch (err: any) { setError(err.message); } }

  async function exportProject() {
    if (!project) return;
    try {
      const response = await fetch(`${API}/projects/${project.id}/export`);
      if (!response.ok) throw Error('Export failed');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `redsage_project_${project.id}.zip`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setNotice('Project archive exported.');
    } catch (err: any) { setError(err.message); }
  }

  async function importProject(file: File) {
    setImporting(true); setNotice(''); setError('');
    try {
      const form = new FormData();
      form.append('file', file);
      const response = await fetch(`${API}/projects/import`, { method: 'POST', body: form });
      if (!response.ok) throw Error((await response.json()).detail || 'Import failed');
      const result = await response.json();
      const list = await apiCall<any[]>('/projects');
      setProjects(list);
      const imported = list.find((item) => item.id === result.project_id) || { id: result.project_id, name: 'Imported Project' };
      setProject(imported); setView('roadmap'); setActiveTarget(''); await refresh(imported, '');
      setNotice('Project imported successfully.');
    } catch (err: any) { setError(err.message); }
    finally { setImporting(false); }
  }

  const downloadUrl = project ? `${API}/projects/${project.id}/report/download` : '#';
  const headerBrand = 'v2 / V1.1';
  return <main>
     <header><b>REDSAGE <small>{headerBrand}</small></b><span>{project ? project.name : 'No engagement selected'}</span><button onClick={createProject}>+ New Project</button><button onClick={() => fileInput.current?.click()} disabled={importing}>{importing ? 'Importing...' : 'Import Project'}</button>{project && <button onClick={exportProject}>Export Project</button>}{project && <button onClick={() => setBriefOpen(true)}>Brief</button>}{project && <button onClick={() => setPlannerOpen(true)}>Planner</button>}{project && selected && <button onClick={() => setMentorOpen((open) => !open)}>AI Mentor</button>}<input ref={fileInput} type="file" accept=".zip" hidden onChange={(event) => { const file = event.target.files?.[0]; if (file) importProject(file); event.target.value = ''; }} /><select value={project?.id || ''} onChange={(event) => { const next = projects.find((item) => item.id === event.target.value); setProject(next); setView('roadmap'); setActiveTarget(''); refresh(next, ''); }}><option value="">Project hub</option>{projects.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><i className={scope?.is_locked ? 'locked' : ''}>{scope?.is_locked ? 'SCOPE LOCKED' : 'SCOPE UNLOCKED'}</i>{project && <><button onClick={() => setAmendOpen(true)} disabled={!scope?.is_locked}>Amend Scope</button><button onClick={() => setHistoryOpen(true)}>History</button><button className="search-trigger" onClick={() => setSearchOpen(true)}>Search <kbd>Ctrl K</kbd></button></>}</header>
    {project && <nav className="tabs"><button className={view === 'roadmap' ? 'selected-tab' : ''} onClick={() => setView('roadmap')}>Roadmap Canvas</button><button className={view === 'evidence' ? 'selected-tab' : ''} onClick={() => setView('evidence')}>Evidence Library ({evidence.length})</button><button className={view === 'assets' ? 'selected-tab' : ''} onClick={() => setView('assets')}>Assets</button><button className={view === 'report' ? 'selected-tab' : ''} onClick={loadReport}>Report Studio</button><button className={view === 'boss' ? 'selected-tab' : ''} onClick={() => setView('boss')}>Boss Brain</button></nav>}
    {error && <div className="error">{error}<button onClick={() => setError('')}>Dismiss</button></div>}
     {notice && <div className="notice">{notice}<button onClick={() => setNotice('')}>Dismiss</button></div>}
    {!project ? <section className="welcome"><h1>Authorized testing, documented.</h1><p>Create an engagement to begin the paste-only evidence workflow.</p></section> : view === 'evidence' ? <EvidenceLibrary evidence={evidence} projectId={project.id} /> : view === 'assets' ? <AssetsView projectId={project.id} onChanged={() => refresh()} /> : view === 'report' ? <section className="report-studio"><label>REPORT STUDIO</label><h1>Formal engagement report</h1><div className="report-grid"><div><button onClick={loadReport}>Refresh Preview</button> <a href={downloadUrl}>Download Report (.md)</a><pre className="report">{report || 'Click Refresh Preview to load the report.'}</pre></div><ReadinessPanel projectId={project.id} /></div></section> : view === 'boss' ? <BossBrainPanel projectId={project.id} tasks={tasks} onError={setError} /> : <div className={mentorOpen && selected ? 'layout with-mentor' : 'layout'}><aside>{(scope?.in_scope_whitelist ?? []).length > 0 && <div className="target-picker"><label>ACTIVE TARGET</label><input list="scope-target-options" value={activeTarget} placeholder="host in scope" onChange={(event) => { const value = event.target.value; setActiveTarget(value); if (scope.in_scope_whitelist.some((item: string) => item.toLowerCase() === value.toLowerCase())) refresh(project, value); }} onKeyDown={(event) => { if (event.key === 'Enter') refresh(project, (event.target as HTMLInputElement).value); }} onBlur={(event) => refresh(project, event.target.value)} /><datalist id="scope-target-options">{scope.in_scope_whitelist.filter((item: string) => !item.trim().startsWith('*.')).map((item: string) => <option key={item} value={item} />)}</datalist><small>Commands and scope safety are computed for this target. Wildcard entries (*.example.com) cover the apex and any subdomain — type the exact host.</small></div>}<h3>Task tree</h3>{tasks.map((phase) => <section key={phase.id}><strong>{phase.name}</strong>{phase.tasks.map((task: any) => <button className={selected?.id === task.id ? 'active' : ''} onClick={() => { setSelected(task); setVerdict(undefined); setSelectedStep(undefined); }} key={task.id}>{task.status === 'COMPLETED' ? '✓' : '○'} {task.title}</button>)}</section>)}<button onClick={configureScope}>{scope?.is_locked ? 'Scope locked' : 'Configure & Lock Scope'}</button><h3>Proposals ({proposals.length})</h3>{proposals.map((proposal) => <div className="proposal" key={proposal.id}>{proposal.title}<button onClick={() => approve(proposal)}>Approve</button><button onClick={() => dismiss(proposal)}>Dismiss</button></div>)}</aside><article>{selected ? <><label>ACTIVE TASK</label><button className="mentor-toggle" onClick={() => setMentorOpen(!mentorOpen)}>{mentorOpen ? 'Hide Mentor' : 'AI Mentor'}</button><h1>{selected.title}</h1><p>{selected.objective}</p><pre>{selected.resolved_command || 'Lock scope to resolve command'}</pre><h2>Evidence tray</h2><textarea value={rawEvidence} onChange={(event) => setRawEvidence(event.target.value)} placeholder="Paste untrusted tool output here. RedSage never executes it."/><button disabled={!scope?.is_locked || !rawEvidence} onClick={verify}>Verify Evidence</button>{verdict && <div className="verdict"><b>{verdict.verdict}</b><p>{verdict.summary}</p><p className="saved">Saved as {verdict.evidence_id} <button onClick={() => setView('evidence')}>View in Evidence Library</button></p>{verdict.grounded_quotations.map((quote: string) => <blockquote key={quote}>{quote}</blockquote>)}<p>{verdict.extracted_assets.map((asset: any) => <mark key={asset.value}>{asset.type}: {asset.value}</mark>)}</p></div>}</> : <p>Select a task from the tree.</p>}<hr /><FindingsPanel projectId={project.id} findings={findings} evidence={evidence} onChanged={() => refresh()} onError={setError} /></article>{mentorOpen && selected && <MentorPanel projectId={project.id} task={selected} targetHost={activeTarget} onError={setError} />}</div>}
     {project && selected && view === 'roadmap' && <TaskStepsPanel projectId={project.id} task={selected} locked={!!scope?.is_locked} onChanged={() => refresh()} onOpenMentor={(step) => { setSelectedStep(step); setMentorOpen(true); }} onError={setError} />}
     {mentorOpen && project && selected && <MentorPanel projectId={project.id} task={selected} step={selectedStep} targetHost={activeTarget} onError={setError} />}
     {plannerOpen && project && <WorkflowPlannerPanel project={project} onClose={() => setPlannerOpen(false)} onApplied={() => refresh()} onError={setError} />}
     {briefOpen && project && <ProjectBriefPanel project={project} onClose={() => setBriefOpen(false)} onSaved={(brief) => { setProject((current: any) => current ? { ...current, brief } : current); setProjects((current) => current.map((item) => item.id === project.id ? { ...item, brief } : item)); }} onError={setError} />}
    {amendOpen && <ScopeAmendModal projectId={project.id} onClose={() => setAmendOpen(false)} onSaved={() => refresh()} />}
    {historyOpen && <HistoryDrawer projectId={project.id} onClose={() => setHistoryOpen(false)} onChanged={() => refresh()} />}
    {searchOpen && <SearchModal projectId={project.id} onClose={() => setSearchOpen(false)} onNavigate={(next) => setView(next === 'assets' ? 'assets' : next === 'evidence' ? 'evidence' : 'roadmap')} />}
  </main>;
}

createRoot(document.getElementById('root')!).render(<ErrorBoundary><App /></ErrorBoundary>);
