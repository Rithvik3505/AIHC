import {ReportViewer} from "@/components/ReportViewer";
import {SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";

export default function ReportsPage() {
  return (
    <div>
      <SectionTitle title="Reports" subtitle="Founder-readable, advisor-usable AI Health reports." />
      <ReportViewer run={demoRun} />
    </div>
  );
}
