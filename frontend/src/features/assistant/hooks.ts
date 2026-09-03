import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  askAssistant,
  type AskInput,
  createConversation,
  getConversation,
  listConversations,
} from "./api";

const listKey = (businessId: string) => ["assistant-conversations", businessId] as const;
const detailKey = (businessId: string, conversationId: string) =>
  ["assistant-conversation", businessId, conversationId] as const;

export function useConversations(businessId?: string) {
  return useQuery({
    queryKey: listKey(businessId ?? ""),
    queryFn: () => listConversations(businessId!),
    enabled: Boolean(businessId),
  });
}

export function useConversation(businessId?: string, conversationId?: string) {
  return useQuery({
    queryKey: detailKey(businessId ?? "", conversationId ?? ""),
    queryFn: () => getConversation(businessId!, conversationId!),
    enabled: Boolean(businessId && conversationId),
  });
}

export function useCreateConversation(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => createConversation(businessId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: listKey(businessId) }),
  });
}

export function useAskAssistant(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ conversationId, input }: { conversationId: string; input: AskInput }) =>
      askAssistant(businessId, conversationId, input),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: listKey(businessId) });
      queryClient.invalidateQueries({
        queryKey: detailKey(businessId, variables.conversationId),
      });
    },
  });
}
