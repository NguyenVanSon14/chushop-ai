import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createExpense, deleteExpense, ExpenseInput, listExpenses, updateExpense } from "./api";

const expenseKey = (businessId: string) => ["expenses", businessId] as const;

export function useExpenses(businessId?: string) {
  return useQuery({
    queryKey: expenseKey(businessId ?? ""),
    queryFn: () => listExpenses(businessId!),
    enabled: Boolean(businessId),
  });
}

export function useCreateExpense(businessId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: ExpenseInput) => createExpense(businessId, input),
    onSuccess: () => client.invalidateQueries({ queryKey: expenseKey(businessId) }),
  });
}

export function useUpdateExpense(businessId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: ExpenseInput }) =>
      updateExpense(businessId, id, input),
    onSuccess: () => client.invalidateQueries({ queryKey: expenseKey(businessId) }),
  });
}

export function useDeleteExpense(businessId: string) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteExpense(businessId, id),
    onSuccess: () => client.invalidateQueries({ queryKey: expenseKey(businessId) }),
  });
}
