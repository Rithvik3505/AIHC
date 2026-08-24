"use client";

import {useState} from "react";
import {EvaluationRunner} from "@/components/EvaluationRunner";
import {ReportViewer} from "@/components/ReportViewer";
import {TaxonomySelector} from "@/components/TaxonomySelector";
import {UploadPanel} from "@/components/UploadPanel";
import {SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";
import type {WorkflowRun} from "@/schemas/types";

export default function EvaluatePage() {
  const [run, setRun] = useState<WorkflowRun>(demoRun);
  return (
    <div>
      <SectionTitle title="Run Diagnostics" subtitle="Select a Lendingtech AI system, attach evidence, and run an assurance workflow." />
      <div className="grid gap-5 lg:grid-cols-[.9fr_1.1fr]">
        <div className="space-y-5">
          <TaxonomySelector />
          <UploadPanel />
          <EvaluationRunner onResult={setRun} />
        </div>
        <ReportViewer run={run} />
      </div>
    </div>
  );
}
