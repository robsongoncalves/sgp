export interface AutomationFunction {
  id: number;
  name: string;
  slug: string;
  description: string;
  language: 'python';
  source_code: string;
  timeout_seconds: number;
  active: boolean;
}

export type AutomationFunctionPayload = Omit<AutomationFunction, 'id'>;
