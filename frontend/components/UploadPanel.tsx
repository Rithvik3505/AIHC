import {Upload} from "lucide-react";
import {Card} from "@/components/ui";

export function UploadPanel() {
  return (
    <Card className="border-dashed">
      <div className="flex items-center gap-3">
        <Upload className="text-trust" />
        <div>
          <div className="text-sm font-semibold">Upload Diagnostic Evidence</div>
          <div className="text-sm text-muted">CSV, JSON, prompts, outputs, predictions, or sample records</div>
        </div>
      </div>
    </Card>
  );
}
