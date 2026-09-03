import { apiRequest } from "@/lib/api/client";
import type { Expense } from "@/lib/api/types";

export type ExpenseInput = {
  description: string;
  category: string;
  amount: number;
  incurred_on: string;
};

const path = (businessId: string) => `/businesses/${businessId}/expenses`;

export const listExpenses = (businessId: string) => apiRequest<Expense[]>(path(businessId));
export const createExpense = (businessId: string, input: ExpenseInput) =>
  apiRequest<Expense>(path(businessId), { method: "POST", body: JSON.stringify(input) });
export const updateExpense = (businessId: string, expenseId: string, input: ExpenseInput) =>
  apiRequest<Expense>(`${path(businessId)}/${expenseId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
export const deleteExpense = (businessId: string, expenseId: string) =>
  apiRequest<void>(`${path(businessId)}/${expenseId}`, { method: "DELETE" });
