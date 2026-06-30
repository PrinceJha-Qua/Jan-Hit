export interface Beneficiary {
  name: string;
  age: number;
  district: string;
  occupation: string;
  annualIncome: number;
  isWidow: boolean;
  isFarmer: boolean;
  hasDisability: boolean;
  caste?: string;
  gender: 'female' | 'male' | 'other';
}

export interface Scheme {
  id: string;
  name: string;
  department: string;
  whyEligible: string;
  missingDocuments: string[];
  nextStep: string;
  benefitAmount: string;
  status: 'eligible' | 'pending' | 'needs-documents';
}

export interface ActionStep {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'in-progress' | 'pending' | 'blocked';
  owner: string;
  dueDate: string;
}

export interface Case {
  id: string;
  beneficiaryName: string;
  district: string;
  status: 'pending' | 'in-progress' | 'completed' | 'needs-follow-up';
  lastUpdated: string;
  schemeCount: number;
}

export const DEMO_BENEFICIARY: Beneficiary = {
  name: 'Asha Devi',
  age: 63,
  district: 'Nagpur',
  occupation: 'Homemaker',
  annualIncome: 60000,
  isWidow: true,
  isFarmer: false,
  hasDisability: false,
  gender: 'female',
  caste: 'General',
};

export const DEMO_SCHEMES: Scheme[] = [
  {
    id: '1',
    name: 'Indira Gandhi National Old Age Pension (IGNOAPS)',
    department: 'Ministry of Rural Development',
    whyEligible: 'Age 60+, widow, income below ₹1 lakh/year',
    missingDocuments: ['Income Certificate', 'Death Certificate of Spouse'],
    nextStep: 'Obtain Income Certificate from Tehsil office',
    benefitAmount: '₹500/month (Centre) + ₹600/month (State)',
    status: 'eligible',
  },
  {
    id: '2',
    name: 'National Family Benefit Scheme (NFBS)',
    department: 'Ministry of Women & Child Development',
    whyEligible: 'BPL family, primary breadwinner deceased',
    missingDocuments: ['BPL Card', 'Death Certificate'],
    nextStep: 'Verify BPL status with Gram Panchayat',
    benefitAmount: '₹20,000 one-time',
    status: 'needs-documents',
  },
  {
    id: '3',
    name: 'Pradhan Mantri Jan Arogya Yojana (PM-JAY)',
    department: 'Ministry of Health & Family Welfare',
    whyEligible: 'Rural household, SECC listed, no insurance',
    missingDocuments: ['Ration Card', 'Aadhaar Card'],
    nextStep: 'Verify SECC listing at CSC centre',
    benefitAmount: '₹5 lakh health cover per family/year',
    status: 'eligible',
  },
  {
    id: '4',
    name: 'Widow Pension Scheme (State)',
    department: 'Social Welfare Department, Maharashtra',
    whyEligible: 'Resident of Maharashtra, widow, age 18+',
    missingDocuments: ['Domicile Certificate', 'Bank Passbook'],
    nextStep: 'Apply online via MahaDBT portal',
    benefitAmount: '₹600/month',
    status: 'eligible',
  },
];

export const DEMO_ACTION_PLAN: ActionStep[] = [
  {
    id: '1',
    title: 'Income Certificate',
    description: 'Obtain from Tehsil office or via CSC',
    status: 'completed',
    owner: 'CSC Operator',
    dueDate: '2024-12-15',
  },
  {
    id: '2',
    title: 'Bank Account Linking',
    description: 'Link Aadhaar to bank for DBT transfer',
    status: 'completed',
    owner: 'Bank Mitra',
    dueDate: '2024-12-18',
  },
  {
    id: '3',
    title: 'Apply for IGNOAPS',
    description: 'Submit application via ILMS portal',
    status: 'in-progress',
    owner: 'Gram Sevak',
    dueDate: '2024-12-25',
  },
  {
    id: '4',
    title: 'Follow-up with BDO',
    description: 'Check sanction status after 30 days',
    status: 'pending',
    owner: 'Gram Sevak',
    dueDate: '2025-01-20',
  },
];

export const DEMO_CASES: Case[] = [
  {
    id: '1',
    beneficiaryName: 'Asha Devi',
    district: 'Nagpur',
    status: 'in-progress',
    lastUpdated: '2024-12-20',
    schemeCount: 4,
  },
  {
    id: '2',
    beneficiaryName: 'Ramesh Yadav',
    district: 'Wardha',
    status: 'pending',
    lastUpdated: '2024-12-19',
    schemeCount: 2,
  },
  {
    id: '3',
    beneficiaryName: 'Sunita Bai',
    district: 'Nagpur',
    status: 'needs-follow-up',
    lastUpdated: '2024-12-18',
    schemeCount: 3,
  },
  {
    id: '4',
    beneficiaryName: 'Kishan Lal',
    district: 'Chandrapur',
    status: 'completed',
    lastUpdated: '2024-12-15',
    schemeCount: 1,
  },
  {
    id: '5',
    beneficiaryName: 'Meera Devi',
    district: 'Nagpur',
    status: 'pending',
    lastUpdated: '2024-12-20',
    schemeCount: 2,
  },
];

export const DISTRICT_STATS = {
  totalCases: 1247,
  pendingCases: 342,
  completedThisMonth: 189,
  schemesDisbursed: 856,
  topSchemes: [
    { name: 'IGNOAPS', count: 412 },
    { name: 'PM-JAY', count: 298 },
    { name: 'Widow Pension', count: 187 },
    { name: 'NFBS', count: 134 },
    { name: 'PM Kisan', count: 98 },
  ],
  monthlyTrend: [
    { month: 'Aug', cases: 142 },
    { month: 'Sep', cases: 156 },
    { month: 'Oct', cases: 178 },
    { month: 'Nov', cases: 165 },
    { month: 'Dec', cases: 189 },
  ],
};
