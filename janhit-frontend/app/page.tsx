'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  Users,
  FileSearch,
  ClipboardList,
  ChevronRight,
  CheckCircle2,
  Clock,
  AlertCircle,
  Play,
  Plus,
  LogIn,
  ArrowRight,
  TrendingUp,
  BarChart3,
  MapPin,
  Calendar,
  Phone,
  Home as HomeIcon,
  Settings,
  Search,
  Filter,
  ChevronDown,
  Printer,
  Share2,
  UserCheck,
  ShieldCheck,
  Banknote,
  HeartPulse,
  FileText,
} from 'lucide-react';
import {
  DEMO_BENEFICIARY,
  DEMO_SCHEMES,
  DEMO_ACTION_PLAN,
  DEMO_CASES,
  DISTRICT_STATS,
  type Beneficiary,
  type ActionStep,
  type Scheme,
  type Case,
} from '@/lib/demo-data';
import {
  createAssessment,
  runEligibility,
  generateActionPlan,
  createShareLink,
  getCitizenRecord,
  listCases,
  getDistrictStats,
  type ApiEligibilityResult,
  type ApiActionStep,
} from '@/lib/api';

// Map backend snake_case eligibility results onto the same Scheme shape
// the (unchanged) UI already renders, so no screen markup has to change.
function toUiSchemes(results: ApiEligibilityResult[]): Scheme[] {
  return results.map((r) => ({
    id: r.scheme_id,
    name: r.scheme_name,
    department: r.department,
    whyEligible: r.why_eligible,
    missingDocuments: r.missing_documents,
    nextStep: r.next_step,
    benefitAmount: r.benefit_amount,
    status: r.status,
  }));
}

function toUiActionSteps(steps: ApiActionStep[]): ActionStep[] {
  return steps.map((s) => ({
    id: s.id,
    title: s.title,
    description: s.description,
    status: s.status,
    owner: s.owner,
    dueDate: s.due_date || '',
  }));
}

type Screen =
  | 'landing'
  | 'assessment'
  | 'eligibility'
  | 'action-plan'
  | 'citizen-record'
  | 'workspace'
  | 'district'
  | 'settings';

export default function Home() {
  const [screen, setScreen] = useState<Screen>('landing');
  const [isDemo, setIsDemo] = useState(false);

  // Real-mode state populated by the backend as the worker moves through
  // the flow. Demo mode never touches these — it keeps using DEMO_* data.
  const [beneficiary, setBeneficiary] = useState<Beneficiary | null>(null);
  const [caseId, setCaseId] = useState<string | null>(null);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [actionPlan, setActionPlan] = useState<ActionStep[]>([]);
  const [shareToken, setShareToken] = useState<string | null>(null);

  const navigate = (s: Screen, demo = false) => {
    setIsDemo(demo);
    setScreen(s);
  };

  return (
    <div className="min-h-screen bg-janhit-gray">
      {screen === 'landing' && <LandingScreen navigate={navigate} />}
      {screen === 'assessment' && (
        <AssessmentScreen
          navigate={navigate}
          isDemo={isDemo}
          onSubmitted={(b, cId, aId, s) => {
            setBeneficiary(b);
            setCaseId(cId);
            setAssessmentId(aId);
            setSchemes(s);
          }}
        />
      )}
      {screen === 'eligibility' && (
        <EligibilityScreen
          navigate={navigate}
          isDemo={isDemo}
          schemes={schemes}
          caseId={caseId}
          onPlanGenerated={(steps) => setActionPlan(steps)}
        />
      )}
      {screen === 'action-plan' && (
        <ActionPlanScreen
          navigate={navigate}
          isDemo={isDemo}
          steps={actionPlan}
          caseId={caseId}
          onShared={(token) => setShareToken(token)}
        />
      )}
      {screen === 'citizen-record' && (
        <CitizenRecordScreen
          navigate={navigate}
          isDemo={isDemo}
          shareToken={shareToken}
        />
      )}
      {screen === 'workspace' && <WorkspaceScreen navigate={navigate} />}
      {screen === 'district' && <DistrictScreen navigate={navigate} />}
      {screen === 'settings' && <SettingsScreen navigate={navigate} />}
    </div>
  );
}

/* ================================================================
   LANDING SCREEN
   ================================================================ */

function LandingScreen({
  navigate,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
}) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-janhit-blue text-white py-10 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight">JanHit</h1>
          </div>
          <p className="text-xl text-blue-100 leading-relaxed">
            Helping Frontline Workers<br />
            Deliver Welfare
          </p>
        </div>
      </header>

      <main className="flex-1 px-4 py-8 max-w-3xl mx-auto w-full">
        {/* Primary Actions */}
        <div className="space-y-3 mb-10">
          <Button
            size="lg"
            className="w-full h-14 text-lg bg-janhit-green hover:bg-janhit-green-dark text-white justify-between rounded-xl"
            onClick={() => navigate('assessment', true)}
          >
            <span className="flex items-center gap-3">
              <Play className="w-6 h-6" />
              Open Demo: Asha Devi
            </span>
            <ChevronRight className="w-5 h-5" />
          </Button>

          <Button
            size="lg"
            variant="outline"
            className="w-full h-14 text-lg justify-between border-janhit-blue text-janhit-blue hover:bg-blue-50 rounded-xl"
            onClick={() => navigate('assessment')}
          >
            <span className="flex items-center gap-3">
              <Plus className="w-6 h-6" />
              New Assessment
            </span>
            <ChevronRight className="w-5 h-5" />
          </Button>

          <Button
            size="lg"
            variant="ghost"
            className="w-full h-14 text-lg justify-between text-gray-600 hover:text-gray-900 rounded-xl"
            onClick={() => navigate('workspace')}
          >
            <span className="flex items-center gap-3">
              <LogIn className="w-6 h-6" />
              Field Worker Login
            </span>
            <ChevronRight className="w-5 h-5" />
          </Button>
        </div>

        {/* Feature Cards */}
        <div className="grid gap-4 mb-10">
          <Card className="border-gray-200 shadow-sm rounded-xl">
            <CardContent className="p-5 flex items-start gap-4">
              <div className="bg-blue-50 p-3 rounded-xl">
                <Users className="w-7 h-7 text-janhit-blue" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Create Beneficiary Case
                </h3>
                <p className="text-gray-600 mt-1">
                  Record citizen details and identify welfare needs in minutes.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-gray-200 shadow-sm rounded-xl">
            <CardContent className="p-5 flex items-start gap-4">
              <div className="bg-green-50 p-3 rounded-xl">
                <FileSearch className="w-7 h-7 text-janhit-green" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Find Eligible Schemes
                </h3>
                <p className="text-gray-600 mt-1">
                  Match citizens to central and state welfare schemes automatically.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-gray-200 shadow-sm rounded-xl">
            <CardContent className="p-5 flex items-start gap-4">
              <div className="bg-amber-50 p-3 rounded-xl">
                <ClipboardList className="w-7 h-7 text-janhit-amber" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Generate Action Plan
                </h3>
                <p className="text-gray-600 mt-1">
                  Step-by-step roadmap with documents, deadlines, and owners.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Workflow */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            How JanHit Works
          </h2>
          <div className="flex flex-col gap-3">
            {[
              { label: 'Citizen', icon: Users },
              { label: 'Assessment', icon: FileText },
              { label: 'Eligibility', icon: ShieldCheck },
              { label: 'Documents', icon: FileSearch },
              { label: 'Action Plan', icon: ClipboardList },
              { label: 'Benefit', icon: Banknote },
            ].map((step, i) => (
              <div key={step.label} className="flex items-center gap-3">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-10 h-10 rounded-full bg-janhit-blue text-white flex items-center justify-center shrink-0">
                    <step.icon className="w-5 h-5" />
                  </div>
                  <span className="text-base font-medium text-gray-900">
                    {step.label}
                  </span>
                </div>
                {i < 5 && (
                  <ArrowRight className="w-5 h-5 text-gray-400 shrink-0" />
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

/* ================================================================
   ASSESSMENT SCREEN
   ================================================================ */

function AssessmentScreen({
  navigate,
  isDemo,
  onSubmitted,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
  isDemo: boolean;
  onSubmitted: (beneficiary: Beneficiary, caseId: string, assessmentId: string, schemes: Scheme[]) => void;
}) {
  const [step, setStep] = useState(1);
  const totalSteps = 4;
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [form, setForm] = useState<Partial<Beneficiary>>(
    isDemo ? DEMO_BENEFICIARY : {}
  );

  const update = (key: keyof Beneficiary, value: any) => {
    setForm((f) => ({ ...f, [key]: value }));
  };

  const canProceed = () => {
    if (step === 1) return form.name && form.age && form.gender;
    if (step === 2) return form.district && form.occupation;
    if (step === 3) return form.annualIncome !== undefined;
    return true;
  };

  const next = async () => {
    if (step < totalSteps) {
      setStep(step + 1);
      return;
    }

    if (isDemo) {
      navigate('eligibility', true);
      return;
    }

    // Real flow: submit to backend, run the rule engine, then move on.
    setSubmitting(true);
    setSubmitError(null);
    try {
      const beneficiary = form as Beneficiary;
      const assessment = await createAssessment(beneficiary);
      const results = await runEligibility(assessment.id);
      onSubmitted(beneficiary, assessment.case_id, assessment.id, toUiSchemes(results));
      navigate('eligibility', false);
    } catch (err: any) {
      setSubmitError(err.message || 'Could not reach the server. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const prev = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-janhit-blue text-white px-4 py-5">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-1">
            <button
              onClick={() => navigate('landing')}
              className="text-blue-100 hover:text-white flex items-center gap-1 text-sm"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Back
            </button>
            <div className="w-12" />
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Beneficiary Case</h1>
              <p className="text-sm text-blue-100">Asha Devi • Nagpur • In Progress</p>
            </div>
          </div>
        </div>
      </div>

      {/* Progress */}
      <div className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">
              Step {step} of {totalSteps}
            </span>
            <span className="text-sm text-gray-500">
              {step === 1 && 'Personal Details'}
              {step === 2 && 'Location & Work'}
              {step === 3 && 'Income & Status'}
              {step === 4 && 'Review'}
            </span>
          </div>
          <Progress
            value={(step / totalSteps) * 100}
            className="h-3"
          />
        </div>
      </div>

      {/* Form */}
      <main className="flex-1 px-4 py-6 max-w-2xl mx-auto w-full">
        {step === 1 && (
          <div className="space-y-5">
            <h2 className="text-2xl font-semibold text-gray-900">
              Personal Details
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={form.name || ''}
                onChange={(e) => update('name', e.target.value)}
                placeholder="Enter citizen's full name"
                className="w-full h-14 px-4 text-lg rounded-xl border border-gray-300 focus:ring-2 focus:ring-janhit-blue focus:border-janhit-blue outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Age
                </label>
                <input
                  type="number"
                  value={form.age || ''}
                  onChange={(e) => update('age', parseInt(e.target.value) || '')}
                  placeholder="Age"
                  className="w-full h-14 px-4 text-lg rounded-xl border border-gray-300 focus:ring-2 focus:ring-janhit-blue focus:border-janhit-blue outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gender
                </label>
                <div className="flex gap-2">
                  {(['female', 'male', 'other'] as const).map((g) => (
                    <button
                      key={g}
                      onClick={() => update('gender', g)}
                      className={`flex-1 h-14 rounded-xl border-2 text-base font-medium capitalize transition-colors ${
                        form.gender === g
                          ? 'border-janhit-blue bg-blue-50 text-janhit-blue'
                          : 'border-gray-200 text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      {g}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-5">
            <h2 className="text-2xl font-semibold text-gray-900">
              Location & Work
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                District
              </label>
              <input
                type="text"
                value={form.district || ''}
                onChange={(e) => update('district', e.target.value)}
                placeholder="e.g., Nagpur"
                className="w-full h-14 px-4 text-lg rounded-xl border border-gray-300 focus:ring-2 focus:ring-janhit-blue focus:border-janhit-blue outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Occupation
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  'Farmer',
                  'Labourer',
                  'Homemaker',
                  'Shopkeeper',
                  'Retired',
                  'Other',
                ].map((occ) => (
                  <button
                    key={occ}
                    onClick={() => update('occupation', occ)}
                    className={`h-14 rounded-xl border-2 text-base font-medium transition-colors ${
                      form.occupation === occ
                        ? 'border-janhit-blue bg-blue-50 text-janhit-blue'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    {occ}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-5">
            <h2 className="text-2xl font-semibold text-gray-900">
              Income & Status
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Annual Income (₹)
              </label>
              <input
                type="number"
                value={form.annualIncome || ''}
                onChange={(e) =>
                  update('annualIncome', parseInt(e.target.value) || '')
                }
                placeholder="e.g., 60000"
                className="w-full h-14 px-4 text-lg rounded-xl border border-gray-300 focus:ring-2 focus:ring-janhit-blue focus:border-janhit-blue outline-none"
              />
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Special Categories
              </label>
              {[
                { key: 'isWidow', label: 'Widow' },
                { key: 'isFarmer', label: 'Farmer' },
                { key: 'hasDisability', label: 'Person with Disability' },
              ].map((item) => (
                <button
                  key={item.key}
                  onClick={() =>
                    update(item.key as keyof Beneficiary, !(form as any)[item.key])
                  }
                  className={`w-full h-14 rounded-xl border-2 text-left px-4 text-base font-medium flex items-center justify-between transition-colors ${
                    (form as any)[item.key]
                      ? 'border-janhit-blue bg-blue-50 text-janhit-blue'
                      : 'border-gray-200 text-gray-600 hover:border-gray-300'
                  }`}
                >
                  {item.label}
                  {(form as any)[item.key] && (
                    <CheckCircle2 className="w-5 h-5" />
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-5">
            <h2 className="text-2xl font-semibold text-gray-900">Review</h2>

            <Card className="border-gray-200 shadow-sm rounded-xl">
              <CardContent className="p-5 space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Name</span>
                  <span className="font-medium text-gray-900">{form.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Age</span>
                  <span className="font-medium text-gray-900">{form.age}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Gender</span>
                  <span className="font-medium text-gray-900 capitalize">
                    {form.gender}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">District</span>
                  <span className="font-medium text-gray-900">
                    {form.district}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Occupation</span>
                  <span className="font-medium text-gray-900">
                    {form.occupation}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Annual Income</span>
                  <span className="font-medium text-gray-900">
                    ₹{form.annualIncome?.toLocaleString()}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 pt-2">
                  {form.isWidow && (
                    <Badge className="bg-blue-100 text-janhit-blue hover:bg-blue-100">
                      Widow
                    </Badge>
                  )}
                  {form.isFarmer && (
                    <Badge className="bg-green-100 text-janhit-green hover:bg-green-100">
                      Farmer
                    </Badge>
                  )}
                  {form.hasDisability && (
                    <Badge className="bg-amber-100 text-janhit-amber hover:bg-amber-100">
                      Disability
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Bottom Actions */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-2xl mx-auto">
          {submitError && (
            <p className="text-sm text-janhit-red mb-3">{submitError}</p>
          )}
          <div className="flex gap-3">
            {step > 1 && (
              <Button
                variant="outline"
                size="lg"
                className="h-14 text-base rounded-xl"
                onClick={prev}
                disabled={submitting}
              >
                Previous
              </Button>
            )}
            <Button
              size="lg"
              className="flex-1 h-14 text-lg bg-janhit-blue hover:bg-janhit-blue-light text-white rounded-xl"
              onClick={next}
              disabled={!canProceed() || submitting}
            >
              {submitting
                ? 'Finding Schemes...'
                : step === totalSteps
                ? 'Find Schemes'
                : 'Next'}
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   ELIGIBILITY SCREEN
   ================================================================ */

function EligibilityScreen({
  navigate,
  isDemo,
  schemes: realSchemes,
  caseId,
  onPlanGenerated,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
  isDemo: boolean;
  schemes: Scheme[];
  caseId: string | null;
  onPlanGenerated: (steps: ActionStep[]) => void;
}) {
  const schemes = isDemo ? DEMO_SCHEMES : realSchemes;
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);

  const handleGeneratePlan = async () => {
    if (isDemo) {
      navigate('action-plan', true);
      return;
    }
    if (!caseId) {
      setGenError('Missing case reference. Please restart the assessment.');
      return;
    }
    setGenerating(true);
    setGenError(null);
    try {
      const steps = await generateActionPlan(caseId);
      onPlanGenerated(toUiActionSteps(steps));
      navigate('action-plan', false);
    } catch (err: any) {
      setGenError(err.message || 'Could not reach the server. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const statusBadge = (status: typeof DEMO_SCHEMES[number]['status']) => {
    if (status === 'eligible')
      return (
        <Badge className="bg-green-100 text-janhit-green hover:bg-green-100 text-sm px-3 py-1">
          Eligible
        </Badge>
      );
    if (status === 'needs-documents')
      return (
        <Badge className="bg-amber-100 text-janhit-amber hover:bg-amber-100 text-sm px-3 py-1">
          Needs Documents
        </Badge>
      );
    return (
      <Badge className="bg-gray-100 text-gray-600 hover:bg-gray-100 text-sm px-3 py-1">
        Pending
      </Badge>
    );
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-janhit-blue text-white px-4 py-5">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-1">
            <button
              onClick={() => navigate('assessment', isDemo)}
              className="text-blue-100 hover:text-white flex items-center gap-1 text-sm"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Back
            </button>
            <div className="w-12" />
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Eligible Schemes</h1>
              <p className="text-sm text-blue-100">Asha Devi • 4 schemes matched</p>
            </div>
          </div>
        </div>
      </div>

      <main className="flex-1 px-4 py-6 max-w-2xl mx-auto w-full">
        <div className="space-y-4">
          {schemes.map((scheme) => (
            <Card key={scheme.id} className="border-gray-200 shadow-sm rounded-xl overflow-hidden relative">
              <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${scheme.status === 'eligible' ? 'bg-janhit-green' : 'bg-janhit-amber'}`} />
              <CardContent className="p-0">
                <div className="p-5 pl-6">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <h3 className="text-xl font-bold text-gray-900 leading-tight">
                      {scheme.name}
                    </h3>
                    {statusBadge(scheme.status)}
                  </div>

                  <p className="text-sm text-gray-500 mb-4">{scheme.department}</p>

                  <div className="bg-blue-50 rounded-xl p-3.5 mb-4">
                    <p className="text-sm font-semibold text-janhit-blue mb-1">
                      Why eligible
                    </p>
                    <p className="text-sm text-gray-700">{scheme.whyEligible}</p>
                  </div>

                  {scheme.missingDocuments.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-semibold text-janhit-amber mb-2">
                        Missing Documents
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {scheme.missingDocuments.map((doc) => (
                          <span
                            key={doc}
                            className="inline-flex items-center px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 text-sm font-medium text-janhit-amber"
                          >
                            {doc}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <div>
                      <p className="text-xs text-gray-500">Benefit</p>
                      <p className="text-sm font-bold text-janhit-green">
                        {scheme.benefitAmount}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Next Step</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {scheme.nextStep}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>

      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-2xl mx-auto">
          {genError && <p className="text-sm text-janhit-red mb-3">{genError}</p>}
          <Button
            size="lg"
            className="w-full h-14 text-lg bg-janhit-blue hover:bg-janhit-blue-light text-white rounded-xl"
            onClick={handleGeneratePlan}
            disabled={generating}
          >
            {generating ? 'Generating Plan...' : 'Generate Action Plan'}
            <ChevronRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   ACTION PLAN SCREEN
   ================================================================ */

function ActionPlanScreen({
  navigate,
  isDemo,
  steps: realSteps,
  caseId,
  onShared,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
  isDemo: boolean;
  steps: ActionStep[];
  caseId: string | null;
  onShared: (token: string) => void;
}) {
  const steps = isDemo ? DEMO_ACTION_PLAN : realSteps;
  const [sharing, setSharing] = useState(false);

  const handleShare = async () => {
    if (isDemo) {
      navigate('citizen-record', true);
      return;
    }
    if (!caseId) {
      navigate('citizen-record', false);
      return;
    }
    setSharing(true);
    try {
      const link = await createShareLink(caseId);
      onShared(link.token);
    } catch {
      // Non-fatal: citizen record screen will show a friendly empty state.
    } finally {
      setSharing(false);
      navigate('citizen-record', false);
    }
  };

  const statusConfig = (status: ActionStep['status']) => {
    switch (status) {
      case 'completed':
        return {
          dot: 'bg-janhit-green',
          badge: (
            <Badge className="bg-green-100 text-janhit-green hover:bg-green-100">
              Completed
            </Badge>
          ),
          icon: <CheckCircle2 className="w-5 h-5 text-janhit-green" />,
        };
      case 'in-progress':
        return {
          dot: 'bg-janhit-blue',
          badge: (
            <Badge className="bg-blue-100 text-janhit-blue hover:bg-blue-100">
              In Progress
            </Badge>
          ),
          icon: <Clock className="w-5 h-5 text-janhit-blue" />,
        };
      case 'blocked':
        return {
          dot: 'bg-janhit-red',
          badge: (
            <Badge className="bg-red-100 text-janhit-red hover:bg-red-100">
              Blocked
            </Badge>
          ),
          icon: <AlertCircle className="w-5 h-5 text-janhit-red" />,
        };
      default:
        return {
          dot: 'bg-gray-300',
          badge: (
            <Badge className="bg-gray-100 text-gray-600 hover:bg-gray-100">
              Pending
            </Badge>
          ),
          icon: <Clock className="w-5 h-5 text-gray-400" />,
        };
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-janhit-blue text-white px-4 py-5">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-1">
            <button
              onClick={() => navigate('eligibility', isDemo)}
              className="text-blue-100 hover:text-white flex items-center gap-1 text-sm"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Back
            </button>
            <div className="w-12" />
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Action Plan</h1>
              <p className="text-sm text-blue-100">Asha Devi • 4 steps • 2 completed</p>
            </div>
          </div>
        </div>
      </div>

      <main className="flex-1 px-4 py-6 max-w-2xl mx-auto w-full">
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />

          <div className="space-y-6">
            {steps.map((step, i) => {
              const config = statusConfig(step.status);
              return (
                <div key={step.id} className="relative flex gap-4">
                  {/* Dot */}
                  <div className="relative z-10">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center border-4 border-white shadow-sm ${config.dot}`}
                    >
                      <span className="text-white text-sm font-bold">
                        {i + 1}
                      </span>
                    </div>
                  </div>

                  {/* Card */}
                  <Card className="flex-1 border-gray-200 shadow-sm rounded-xl">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {step.title}
                        </h3>
                        {config.badge}
                      </div>

                      <p className="text-gray-600 mb-3">{step.description}</p>

                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1.5 text-gray-600">
                          <UserCheck className="w-4 h-4" />
                          {step.owner}
                        </div>
                        <div className="flex items-center gap-1.5 text-gray-600">
                          <Calendar className="w-4 h-4" />
                          {step.dueDate}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              );
            })}
          </div>
        </div>
      </main>

      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-2xl mx-auto flex gap-3">
          <Button
            variant="outline"
            size="lg"
            className="flex-1 h-14 text-base rounded-xl"
            onClick={handleShare}
            disabled={sharing}
          >
            <Share2 className="w-5 h-5 mr-2" />
            {sharing ? 'Sharing...' : 'Share Record'}
          </Button>
          <Button
            size="lg"
            className="flex-1 h-14 text-lg bg-janhit-blue hover:bg-janhit-blue-light text-white rounded-xl"
            onClick={() => navigate('workspace')}
          >
            <ClipboardList className="w-5 h-5 mr-2" />
            Save to Workspace
          </Button>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   CITIZEN RECORD SCREEN
   ================================================================ */

function CitizenRecordScreen({
  navigate,
  isDemo,
  shareToken,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
  isDemo: boolean;
  shareToken: string | null;
}) {
  const [loading, setLoading] = useState(!isDemo);
  const [record, setRecord] = useState<{
    beneficiary: Beneficiary;
    schemes: Scheme[];
    nextStep: ActionStep | null;
  } | null>(
    isDemo
      ? {
          beneficiary: DEMO_BENEFICIARY,
          schemes: DEMO_SCHEMES,
          nextStep: DEMO_ACTION_PLAN.find((s) => s.status !== 'completed') || null,
        }
      : null
  );

  useEffect(() => {
    if (isDemo || !shareToken) {
      setLoading(false);
      return;
    }
    getCitizenRecord(shareToken)
      .then((data) => {
        setRecord({
          beneficiary: {
            name: data.beneficiary.name,
            age: data.beneficiary.age,
            district: data.beneficiary.district,
            occupation: data.beneficiary.occupation,
            annualIncome: data.beneficiary.annual_income,
            isWidow: data.beneficiary.is_widow,
            isFarmer: data.beneficiary.is_farmer,
            hasDisability: data.beneficiary.has_disability,
            caste: data.beneficiary.caste,
            gender: data.beneficiary.gender,
          },
          schemes: toUiSchemes(data.schemes),
          nextStep: data.next_step
            ? {
                id: data.next_step.id,
                title: data.next_step.title,
                description: data.next_step.description,
                status: data.next_step.status,
                owner: data.next_step.owner,
                dueDate: data.next_step.due_date || '',
              }
            : null,
        });
      })
      .catch(() => setRecord(null))
      .finally(() => setLoading(false));
  }, [isDemo, shareToken]);

  const beneficiary = record?.beneficiary || null;
  const schemes = record?.schemes || [];
  const nextPending = record?.nextStep || null;

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Top Bar */}
      <div className="bg-janhit-blue text-white px-4 py-5">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-1">
            <button
              onClick={() => navigate('action-plan', isDemo)}
              className="text-blue-100 hover:text-white flex items-center gap-1 text-sm"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Back
            </button>
            <div className="w-12" />
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Citizen Record</h1>
              <p className="text-sm text-blue-100">Asha Devi • Shareable</p>
            </div>
          </div>
        </div>
      </div>

      <main className="flex-1 px-4 py-6 max-w-md mx-auto w-full">
        {loading && <p className="text-center text-gray-500 py-12">Loading record...</p>}
        {!loading && !beneficiary && (
          <p className="text-center text-gray-500 py-12">Record not found or link expired.</p>
        )}
        {beneficiary && (
          <div className="space-y-6">
            {/* Citizen Header */}
            <div className="text-center">
              <div className="w-20 h-20 bg-janhit-blue rounded-full flex items-center justify-center mx-auto mb-3">
                <Users className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                {beneficiary.name}
              </h2>
              <p className="text-gray-600">
                {beneficiary.age} years • {beneficiary.district}
              </p>
            </div>

            {/* Status Card */}
            <Card className="border-gray-200 shadow-sm rounded-xl bg-green-50 border-green-200">
              <CardContent className="p-5 text-center">
                <CheckCircle2 className="w-8 h-8 text-janhit-green mx-auto mb-2" />
                <p className="text-sm text-gray-600">Current Status</p>
                <p className="text-xl font-bold text-janhit-green">
                  {schemes.filter((s) => s.status === 'eligible').length} schemes
                  eligible
                </p>
              </CardContent>
            </Card>

            {/* Next Step */}
            {nextPending && (
              <Card className="border-gray-200 shadow-sm rounded-xl">
                <CardContent className="p-5">
                  <p className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-1">
                    Next Step
                  </p>
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">
                    {nextPending.title}
                  </h3>
                  <p className="text-gray-600">{nextPending.description}</p>
                  <div className="flex items-center gap-2 mt-3 text-sm text-gray-600">
                    <MapPin className="w-4 h-4" />
                    Visit {nextPending.owner} office
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Schemes Summary */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Eligible Schemes
              </h3>
              <div className="space-y-2">
                {schemes.map((scheme) => (
                  <div
                    key={scheme.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
                  >
                    <span className="text-sm font-medium text-gray-900">
                      {scheme.name}
                    </span>
                    <Badge
                      className={`text-xs ${
                        scheme.status === 'eligible'
                          ? 'bg-green-100 text-janhit-green'
                          : 'bg-amber-100 text-janhit-amber'
                      }`}
                    >
                      {scheme.status === 'eligible' ? 'Eligible' : 'Needs Docs'}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

/* ================================================================
   WORKSPACE SCREEN
   ================================================================ */

function WorkspaceScreen({
  navigate,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
}) {
  const [filter, setFilter] = useState<'all' | 'today' | 'pending' | 'completed' | 'follow-up'>('all');
  const [cases, setCases] = useState<Case[]>(DEMO_CASES);

  useEffect(() => {
    listCases()
      .then((apiCases) => {
        // Real cases don't carry beneficiary name/district/schemeCount inline
        // (that needs a join the backend doesn't expose yet) — fall back to
        // demo cases if the backend has nothing seeded, otherwise show ids.
        if (apiCases.length === 0) return;
        setCases(
          apiCases.map((c) => ({
            id: c.id,
            beneficiaryName: c.beneficiary_id.slice(0, 8),
            district: '—',
            status: c.status,
            lastUpdated: c.updated_at.slice(0, 10),
            schemeCount: 0,
          }))
        );
      })
      .catch(() => {
        // Backend unreachable — keep showing demo cases so the screen never breaks.
      });
  }, []);

  const filtered = cases.filter((c) => {
    if (filter === 'today') return c.lastUpdated === '2024-12-20';
    if (filter === 'pending') return c.status === 'pending';
    if (filter === 'completed') return c.status === 'completed';
    if (filter === 'follow-up') return c.status === 'needs-follow-up';
    return true;
  });

  const statusBadge = (status: typeof DEMO_CASES[number]['status']) => {
    switch (status) {
      case 'completed':
        return (
          <Badge className="bg-green-100 text-janhit-green hover:bg-green-100">
            Completed
          </Badge>
        );
      case 'in-progress':
        return (
          <Badge className="bg-blue-100 text-janhit-blue hover:bg-blue-100">
            In Progress
          </Badge>
        );
      case 'needs-follow-up':
        return (
          <Badge className="bg-amber-100 text-janhit-amber hover:bg-amber-100">
            Follow-up
          </Badge>
        );
      default:
        return (
          <Badge className="bg-gray-100 text-gray-600 hover:bg-gray-100">
            Pending
          </Badge>
        );
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-janhit-blue text-white px-4 py-5">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-1">
            <button
              onClick={() => navigate('landing')}
              className="text-blue-100 hover:text-white flex items-center gap-1 text-sm"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Back
            </button>
            <button
              onClick={() => navigate('settings')}
              className="text-blue-100 hover:text-white"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Field Worker Workspace</h1>
              <p className="text-sm text-blue-100">5 active cases</p>
            </div>
          </div>
        </div>
      </div>

      <main className="flex-1 px-4 py-6 max-w-4xl mx-auto w-full">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[
            { label: "Today's Cases", value: 3, color: 'bg-blue-50 text-janhit-blue' },
            { label: 'Pending', value: 2, color: 'bg-amber-50 text-janhit-amber' },
            { label: 'Completed', value: 1, color: 'bg-green-50 text-janhit-green' },
            { label: 'Follow-up', value: 1, color: 'bg-red-50 text-janhit-red' },
          ].map((stat) => (
            <Card key={stat.label} className="border-gray-200 shadow-sm rounded-xl">
              <CardContent className="p-4">
                <p className={`text-2xl font-bold ${stat.color.split(' ')[1]}`}>
                  {stat.value}
                </p>
                <p className="text-sm text-gray-600">{stat.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Filters */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-4">
          {([
            { key: 'all', label: 'All Cases' },
            { key: 'today', label: "Today's" },
            { key: 'pending', label: 'Pending' },
            { key: 'completed', label: 'Completed' },
            { key: 'follow-up', label: 'Follow-up' },
          ] as const).map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${
                filter === f.key
                  ? 'bg-janhit-blue text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Cases List */}
        <div className="space-y-3">
          {filtered.map((c) => (
            <Card key={c.id} className="border-gray-200 shadow-sm rounded-xl hover:border-janhit-blue transition-colors cursor-pointer">
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-base font-semibold text-gray-900">
                        {c.beneficiaryName}
                      </h3>
                      {statusBadge(c.status)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5" />
                        {c.district}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {c.lastUpdated}
                      </span>
                      <span className="flex items-center gap-1">
                        <FileSearch className="w-3.5 h-3.5" />
                        {c.schemeCount} schemes
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 shrink-0 mt-1" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}

/* ================================================================
   DISTRICT INTELLIGENCE SCREEN
   ================================================================ */

function DistrictScreen({
  navigate,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
}) {
  const [stats, setStats] = useState(DISTRICT_STATS);

  useEffect(() => {
    getDistrictStats()
      .then((data) => {
        if (data.total_cases === 0) return; // nothing seeded yet, keep demo numbers
        setStats({
          totalCases: data.total_cases,
          pendingCases: data.pending_cases,
          completedThisMonth: data.completed_this_month,
          schemesDisbursed: data.schemes_disbursed,
          topSchemes: data.top_schemes.length ? data.top_schemes : DISTRICT_STATS.topSchemes,
          monthlyTrend: data.monthly_trend.length ? data.monthly_trend : DISTRICT_STATS.monthlyTrend,
        });
      })
      .catch(() => {
        // Backend unreachable — keep showing demo stats so the screen never breaks.
      });
  }, []);

  const maxBar = Math.max(...stats.topSchemes.map((s) => s.count));

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-janhit-blue text-white px-4 py-5">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-1">
            <button
              onClick={() => navigate('workspace')}
              className="text-blue-100 hover:text-white flex items-center gap-1 text-sm"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Back
            </button>
            <div className="w-12" />
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">District Intelligence</h1>
              <p className="text-sm text-blue-100">Nagpur District Overview</p>
            </div>
          </div>
        </div>
      </div>

      <main className="flex-1 px-4 py-6 max-w-4xl mx-auto w-full">
        {/* KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          {[
            { label: 'Total Cases', value: stats.totalCases, icon: Users },
            { label: 'Pending', value: stats.pendingCases, icon: Clock },
            { label: 'This Month', value: stats.completedThisMonth, icon: CheckCircle2 },
            { label: 'Disbursed', value: stats.schemesDisbursed, icon: Banknote },
          ].map((kpi) => (
            <Card key={kpi.label} className="border-gray-200 shadow-sm rounded-xl">
              <CardContent className="p-4">
                <kpi.icon className="w-5 h-5 text-janhit-blue mb-2" />
                <p className="text-2xl font-bold text-gray-900">{kpi.value.toLocaleString()}</p>
                <p className="text-sm text-gray-600">{kpi.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Top Schemes Bar Chart */}
        <Card className="border-gray-200 shadow-sm rounded-xl mb-8">
          <CardContent className="p-5">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Top Schemes by Applications
            </h2>
            <div className="space-y-3">
              {stats.topSchemes.map((scheme) => (
                <div key={scheme.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {scheme.name}
                    </span>
                    <span className="text-sm font-semibold text-gray-900">
                      {scheme.count}
                    </span>
                  </div>
                  <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-janhit-blue rounded-full transition-all"
                      style={{
                        width: `${(scheme.count / maxBar) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Monthly Trend */}
        <Card className="border-gray-200 shadow-sm rounded-xl mb-8">
          <CardContent className="p-5">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Monthly Case Trend
            </h2>
            <div className="flex items-end gap-3 h-40">
              {stats.monthlyTrend.map((m) => {
                const max = Math.max(...stats.monthlyTrend.map((t) => t.cases));
                return (
                  <div key={m.month} className="flex-1 flex flex-col items-center gap-2">
                    <div className="w-full flex justify-center">
                      <div
                        className="w-full max-w-[48px] bg-janhit-green rounded-t"
                        style={{ height: `${(m.cases / max) * 128}px` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">{m.month}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card className="border-gray-200 shadow-sm rounded-xl">
          <CardContent className="p-5">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Recent Cases
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-3 font-medium text-gray-600">
                      Name
                    </th>
                    <th className="text-left py-2 px-3 font-medium text-gray-600">
                      District
                    </th>
                    <th className="text-left py-2 px-3 font-medium text-gray-600">
                      Status
                    </th>
                    <th className="text-right py-2 px-3 font-medium text-gray-600">
                      Schemes
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {DEMO_CASES.slice(0, 5).map((c) => (
                    <tr key={c.id} className="border-b border-gray-100">
                      <td className="py-2 px-3 font-medium text-gray-900">
                        {c.beneficiaryName}
                      </td>
                      <td className="py-2 px-3 text-gray-600">{c.district}</td>
                      <td className="py-2 px-3">
                        {c.status === 'completed' && (
                          <span className="text-janhit-green font-medium">
                            Completed
                          </span>
                        )}
                        {c.status === 'in-progress' && (
                          <span className="text-janhit-blue font-medium">
                            In Progress
                          </span>
                        )}
                        {c.status === 'pending' && (
                          <span className="text-gray-600 font-medium">
                            Pending
                          </span>
                        )}
                        {c.status === 'needs-follow-up' && (
                          <span className="text-janhit-amber font-medium">
                            Follow-up
                          </span>
                        )}
                      </td>
                      <td className="py-2 px-3 text-right font-medium text-gray-900">
                        {c.schemeCount}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

/* ================================================================
   SETTINGS SCREEN
   ================================================================ */

function SettingsScreen({
  navigate,
}: {
  navigate: (s: Screen, demo?: boolean) => void;
}) {
  const [fontSize, setFontSize] = useState<'normal' | 'large'>('normal');

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-janhit-blue text-white px-4 py-5">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-1">
            <button
              onClick={() => navigate('workspace')}
              className="text-blue-100 hover:text-white flex items-center gap-1 text-sm"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Back
            </button>
            <div className="w-12" />
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Settings</h1>
              <p className="text-sm text-blue-100">Preferences</p>
            </div>
          </div>
        </div>
      </div>

      <main className="flex-1 px-4 py-6 max-w-2xl mx-auto w-full">
        <div className="space-y-6">
          {/* Font Size */}
          <Card className="border-gray-200 shadow-sm rounded-xl">
            <CardContent className="p-5">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Display
              </h2>
              <div className="space-y-3">
                <p className="text-sm text-gray-600">Font Size</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setFontSize('normal')}
                    className={`flex-1 h-14 rounded-xl border-2 text-base font-medium transition-colors ${
                      fontSize === 'normal'
                        ? 'border-janhit-blue bg-blue-50 text-janhit-blue'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    Normal
                  </button>
                  <button
                    onClick={() => setFontSize('large')}
                    className={`flex-1 h-14 rounded-xl border-2 text-base font-medium transition-colors ${
                      fontSize === 'large'
                        ? 'border-janhit-blue bg-blue-50 text-janhit-blue'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    Large
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* About */}
          <Card className="border-gray-200 shadow-sm rounded-xl">
            <CardContent className="p-5">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                About JanHit
              </h2>
              <div className="space-y-2 text-sm text-gray-600">
                <p>Version 1.0.0</p>
                <p>Built for frontline welfare workers in rural India.</p>
                <p>Supports: Gram Sevaks, CSC Operators, NGO Field Workers, ASHA Workers</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
