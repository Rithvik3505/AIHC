import {DatabaseZap} from "lucide-react";
import {Card} from "@/components/ui";
import type {WorkflowDefinition} from "@/schemas/types";

export function UploadPanel({workflow}: {workflow: WorkflowDefinition | null}) {
  return (
    <Card className="border-dashed">
      <div className="flex items-start gap-3">
        <DatabaseZap className="mt-1 text-trust" />
        <div>
          <div className="text-sm font-semibold">Structured Evidence</div>
          <p className="mt-1 text-sm text-muted">
            The evaluation workspace supports deterministic demo evidence plus ephemeral manual, CSV, and JSON evidence for the selected Golden Workflow.
          </p>
          <p className="mt-2 text-xs text-muted">
            Operational formats: {workflow?.supported_uploads?.join(", ") || "csv, json"}. Raw PDF/image extraction remains unavailable.
          </p>
        </div>
      </div>
    </Card>
  );
}
