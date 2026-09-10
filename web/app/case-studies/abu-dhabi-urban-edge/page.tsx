import { CaseExplorer } from "../../../components/CaseExplorer";
import type { CaseStudy } from "../../../lib/types";
import caseStudy from "../../../public/data/abu-dhabi-urban-edge/case-study.json";

export default function AbuDhabiCasePage() {
  return <CaseExplorer data={caseStudy as CaseStudy} />;
}
