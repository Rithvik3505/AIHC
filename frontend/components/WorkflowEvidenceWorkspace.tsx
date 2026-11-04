"use client";

import {useEffect, useMemo, useState} from "react";
import {CheckCircle2, Download, FileJson, Plus, Play, Trash2, Upload, XCircle} from "lucide-react";
import {Button, Card} from "@/components/ui";
import {getEvidenceContract, runWorkflow, uploadWorkflowEvidence, validateWorkflowEvidence} from "@/services/api";
import type {EvidenceContract, EvidenceField, EvidenceMode, EvidenceValidation, WorkflowDefinition, WorkflowRun} from "@/schemas/types";

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function recordsFrom(payload: Record<string, unknown>): Record<string, unknown>[] {
  return Array.isArray(payload.records) ? payload.records.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object") : [];
}

function inputValue(value: unknown): string | number {
  if (value === null || value === undefined) return "";
  if (Array.isArray(value)) return value.join("; ");
  if (typeof value === "number" || typeof value === "string") return value;
  return JSON.stringify(value);
}

function csvCell(value: unknown): string {
  const text = Array.isArray(value) ? value.join(";") : String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function download(filename: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], {type}));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function statusTone(status: string): string {
  if (status === "Ready") return "border-trust/30 bg-trust/10 text-trust";
  if (status === "Optional evidence unavailable") return "border-signal/30 bg-signal/10 text-signal";
  return "border-risk/30 bg-risk/10 text-risk";
}

function FieldInput({field, value, onChange}: {field: EvidenceField; value: unknown; onChange: (value: unknown) => void}) {
  const className = "focus-ring min-w-36 rounded-md border border-white/10 bg-surface px-2 py-2 text-sm text-ink";
  if (field.type === "boolean") {
    return <select className={className} value={value === true ? "true" : value === false ? "false" : ""} onChange={(event) => onChange(event.target.value)}><option value="">Unknown</option><option value="true">True</option><option value="false">False</option></select>;
  }
  if (field.type === "binary") {
    return <select className={className} value={inputValue(value)} onChange={(event) => onChange(event.target.value)}><option value="">Missing</option><option value="1">1 / positive</option><option value="0">0 / negative</option></select>;
  }
  if (field.type === "select") {
    return <select className={className} value={inputValue(value)} onChange={(event) => onChange(event.target.value)}><option value="">Select</option>{field.options.map((item) => <option value={item} key={item}>{item}</option>)}</select>;
  }
  if (field.type === "textarea") {
    return <textarea className={`${className} min-h-24 min-w-72`} value={inputValue(value)} onChange={(event) => onChange(event.target.value)} />;
  }
  return <input className={className} type={field.type === "number" ? "number" : "text"} step={field.type === "number" ? "any" : undefined} value={inputValue(value)} onChange={(event) => onChange(event.target.value)} />;
}

export function WorkflowEvidenceWorkspace({workflow, onResult}: {workflow: WorkflowDefinition | null; onResult: (result: WorkflowRun) => void}) {
  const [contract, setContract] = useState<EvidenceContract | null>(null);
  const [mode, setMode] = useState<EvidenceMode>("demo");
  const [payload, setPayload] = useState<Record<string, unknown>>({records: []});
  const [scope, setScope] = useState("all");
  const [validation, setValidation] = useState<EvidenceValidation | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setContract(null);
    setValidation(null);
    setMode("demo");
    setScope("all");
    setError(null);
    if (!workflow) return () => { active = false; };
    getEvidenceContract(workflow.id)
      .then((item) => {
        if (!active) return;
        setContract(item);
        setPayload(clone(item.example_payload));
      })
      .catch((reason) => active && setError(reason instanceof Error ? reason.message : "Unable to load the evidence contract."));
    return () => { active = false; };
  }, [workflow]);

  const selectedTestIds = useMemo(() => {
    if (!contract) return [];
    return scope === "all" ? contract.tests.map((test) => test.id) : [scope];
  }, [contract, scope]);

  function markDirty() {
    setValidation(null);
    setError(null);
  }

  function changeMode(next: EvidenceMode) {
    setMode(next);
    setValidation(null);
    setError(null);
    if (contract && next === "manual") setPayload(clone(contract.example_payload));
    if (next === "upload") setPayload({records: []});
  }

  function setRecordValue(index: number, key: string, value: unknown) {
    const records = recordsFrom(payload).map((record) => ({...record}));
    records[index] = {...records[index], [key]: value};
    setPayload({...payload, records});
    markDirty();
  }

  function addRow() {
    if (!contract) return;
    const empty = Object.fromEntries(contract.record_fields.map((field) => [field.key, ""]));
    setPayload({...payload, records: [...recordsFrom(payload), empty]});
    markDirty();
  }

  function removeRow(index: number) {
    setPayload({...payload, records: recordsFrom(payload).filter((_, rowIndex) => rowIndex !== index)});
    markDirty();
  }

  async function validate() {
    if (!workflow) return;
    setBusy(true);
    setError(null);
    try {
      const result = await validateWorkflowEvidence(workflow.id, {evidence_mode: mode, payload, selected_test_ids: selectedTestIds});
      setValidation(result);
      if (mode !== "demo") setPayload(result.normalized_payload);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Evidence validation failed.");
    } finally {
      setBusy(false);
    }
  }

  async function uploadFile(file: File) {
    if (!workflow || !contract) return;
    if (file.size > contract.limits.maximum_file_bytes) {
      setError(`File exceeds the ${contract.limits.maximum_file_bytes.toLocaleString()} byte limit.`);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await uploadWorkflowEvidence(workflow.id, file);
      setPayload(result.normalized_payload);
      setValidation(result);
      setScope("all");
    } catch (reason) {
      setValidation(null);
      setError(reason instanceof Error ? reason.message : "Evidence upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function run() {
    if (!workflow || !validation?.can_run) return;
    setBusy(true);
    setError(null);
    try {
      onResult(await runWorkflow(workflow.id, {
        evidence_mode: mode,
        payload: mode === "demo" ? undefined : validation.normalized_payload,
        selected_test_ids: selectedTestIds
      }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Workflow execution failed.");
    } finally {
      setBusy(false);
    }
  }

  if (!workflow) return <Card><p className="text-sm text-muted">Select a Golden Workflow to configure evidence.</p></Card>;
  if (!contract) return <Card><p className="text-sm text-muted">Loading workflow evidence contract...</p>{error ? <p className="mt-2 text-sm text-risk">{error}</p> : null}</Card>;

  const records = recordsFrom(payload);
  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><div className="text-sm font-semibold">Evidence And Execution</div><p className="mt-1 text-sm text-muted">Validate evidence before running any of the existing four evaluators.</p></div>
        <div className="grid w-full grid-cols-3 rounded-md border border-white/10 p-1 sm:w-auto" aria-label="Evidence mode">
          {(["demo", "manual", "upload"] as EvidenceMode[]).map((item) => <button className={`rounded px-3 py-2 text-xs font-semibold ${mode === item ? "bg-trust text-[#09231d]" : "text-muted hover:text-ink"}`} key={item} onClick={() => changeMode(item)}>{item === "demo" ? "Demo / Synthetic" : item === "manual" ? "Manual Input" : "File Upload"}</button>)}
        </div>
      </div>

      {mode === "demo" ? <div className="mt-4 rounded-md border border-signal/30 bg-signal/10 p-3 text-sm"><div className="font-semibold text-signal">Deterministic synthetic evidence</div><p className="mt-1 text-muted">Generated by the backend for demonstration and regression testing. It is not customer evidence.</p></div> : null}

      {mode === "upload" ? (
        <div className="mt-4 rounded-md border border-dashed border-white/20 p-4">
          <label className="flex cursor-pointer items-center gap-3 text-sm font-semibold"><Upload size={18} /><span>Choose CSV or JSON evidence</span><input className="sr-only" type="file" accept=".csv,.json,application/json,text/csv" onChange={(event) => {const file = event.target.files?.[0]; if (file) void uploadFile(file);}} /></label>
          <p className="mt-2 text-xs text-muted">Maximum {contract.limits.maximum_file_bytes.toLocaleString()} bytes and {contract.limits.maximum_records} records. PDF and image documents are not accepted.</p>
        </div>
      ) : null}

      {mode !== "demo" ? (
        <div className="mt-5 space-y-4">
          {contract.top_level_fields.length ? <div><div className="mb-2 text-sm font-semibold">Workflow-Level Evidence</div><div className="grid gap-3 md:grid-cols-2">{contract.top_level_fields.map((field) => field.type === "json" ? <label className="text-xs text-muted" key={`${field.key}-${JSON.stringify(payload[field.key] ?? [])}`}><span className="mb-1 block">{field.label}</span><textarea className="focus-ring min-h-32 w-full rounded-md border border-white/10 bg-surface p-2 font-mono text-xs text-ink" defaultValue={JSON.stringify(payload[field.key] ?? [], null, 2)} onBlur={(event) => {try {setPayload({...payload, [field.key]: JSON.parse(event.target.value)}); markDirty();} catch {setError(`${field.label} must be valid JSON.`);}}} /></label> : <label className="text-xs text-muted" key={field.key}><span className="mb-1 block">{field.label}</span><FieldInput field={field} value={payload[field.key]} onChange={(value) => {setPayload({...payload, [field.key]: value}); markDirty();}} /></label>)}</div></div> : null}
          <div className="flex flex-wrap items-center justify-between gap-2"><div><div className="text-sm font-semibold">Evidence Records</div><p className="text-xs text-muted">{records.length} records. Hover field labels for contract descriptions.</p></div><Button className="inline-flex items-center gap-2" onClick={addRow}><Plus size={16} />Add Row</Button></div>
          <div className="overflow-x-auto rounded-md border border-white/10">
            <table className="min-w-full border-collapse text-left"><thead className="bg-white/[0.04]"><tr><th className="p-2 text-xs text-muted">#</th>{contract.record_fields.map((field) => <th className="min-w-40 p-2 text-xs text-muted" title={field.description} key={field.key}>{field.label}</th>)}<th className="p-2"><span className="sr-only">Actions</span></th></tr></thead><tbody>{records.map((record, index) => <tr className="border-t border-white/10 align-top" key={index}><td className="p-2 text-xs text-muted">{index + 1}</td>{contract.record_fields.map((field) => <td className="p-2" key={field.key}><FieldInput field={field} value={record[field.key]} onChange={(value) => setRecordValue(index, field.key, value)} /></td>)}<td className="p-2"><button className="focus-ring rounded p-2 text-muted hover:bg-risk/10 hover:text-risk" title="Remove row" onClick={() => removeRow(index)}><Trash2 size={16} /></button></td></tr>)}</tbody></table>
          </div>
        </div>
      ) : null}

      <div className="mt-5 grid gap-4 border-t border-white/10 pt-5 md:grid-cols-2">
        <div className="min-w-0"><div className="mb-2 text-sm font-semibold">Test Selection</div><select className="focus-ring min-w-0 max-w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-sm" value={scope} onChange={(event) => {setScope(event.target.value); setValidation(null);}}><option value="all">Run all four tests</option>{contract.tests.map((test) => <option value={test.id} key={test.id}>{test.test_type === "strong" ? "Strong Test" : test.id.toUpperCase().endsWith("LT1") ? "LT1" : test.id.toUpperCase().endsWith("LT2") ? "LT2" : "LT3"} - {test.name}</option>)}</select><p className="mt-2 break-words text-xs text-muted">{scope === "all" ? "Runs LT1, LT2, LT3, and ST1." : contract.tests.find((test) => test.id === scope)?.purpose}</p></div>
        <div><div className="mb-2 text-sm font-semibold">Sample Templates</div><div className="flex flex-wrap gap-2"><Button className="inline-flex items-center gap-2 bg-signal text-white hover:bg-[#438bd8]" onClick={() => download(`${workflow.id}.json`, JSON.stringify(contract.example_payload, null, 2), "application/json")}><FileJson size={16} />JSON</Button><Button className="inline-flex items-center gap-2 bg-signal text-white hover:bg-[#438bd8]" onClick={() => {const keys=contract.record_fields.map((field)=>field.key); const rows=recordsFrom(contract.example_payload); download(`${workflow.id}.csv`, [keys.map(csvCell).join(","), ...rows.map((row)=>keys.map((key)=>csvCell(row[key])).join(","))].join("\n"), "text/csv");}}><Download size={16} />CSV</Button></div></div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2"><Button className="inline-flex items-center gap-2 bg-signal text-white hover:bg-[#438bd8]" disabled={busy} onClick={() => void validate()}><CheckCircle2 size={16} />{busy ? "Checking..." : "Validate Evidence"}</Button><Button className="inline-flex items-center gap-2" disabled={busy || !validation?.can_run} onClick={() => void run()}><Play size={16} />{busy ? "Working..." : "Run Evaluation"}</Button></div>

      {error ? <div className="mt-4 flex gap-2 rounded-md border border-risk/30 bg-risk/10 p-3 text-sm text-risk"><XCircle className="shrink-0" size={18} /><span>{error}</span></div> : null}
      {validation ? <div className="mt-5"><div className="mb-2 text-sm font-semibold">Evidence Validation</div><div className="grid gap-2">{validation.tests.map((test) => <div className={`rounded-md border p-3 text-sm ${statusTone(test.status)}`} key={test.test_id}><div className="font-semibold">{test.test_id} - {test.status}</div><p className="mt-1 text-xs opacity-90">{test.message}</p></div>)}</div>{validation.issues.length ? <div className="mt-3 space-y-1 text-xs text-muted">{validation.issues.map((issue, index) => <p key={`${issue.field}-${issue.row}-${index}`}>{issue.severity.toUpperCase()}: {issue.row ? `Row ${issue.row}, ` : ""}{issue.field ? `${issue.field}: ` : ""}{issue.message}</p>)}</div> : <p className="mt-3 text-xs text-trust">No structural evidence issues found.</p>}</div> : null}

      <div className="mt-5 rounded-md border border-white/10 bg-white/[0.03] p-3 text-xs text-muted"><div className="font-semibold text-ink">Privacy And Scope</div><p className="mt-1">{contract.privacy.processing} {contract.privacy.replay} {contract.privacy.benchmark}</p><p className="mt-2">Raw PDF/image document extraction: {contract.raw_document_upload.status}. {contract.raw_document_upload.reason}</p></div>
    </Card>
  );
}
