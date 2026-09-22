import {ReportViewer} from "@/components/ReportViewer";
import {SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";

export default function ReportsPage() {
  return (
    <div>
      <SectionTitle title="Reports" subtitle="Static synthetic demo report; live workflow reports are generated from the Evaluate page." />
      <ReportViewer run={demoRun} />
    </div>
  );
}
