import { apiRequest } from "@/lib/api/client";
import type {
  AssistantConversation,
  AssistantConversationDetail,
  AssistantReply,
} from "@/lib/api/types";

const path = (businessId: string) => `/businesses/${businessId}/assistant/conversations`;

export function listConversations(businessId: string) {
  return apiRequest<AssistantConversation[]>(path(businessId));
}

export function createConversation(businessId: string) {
  return apiRequest<AssistantConversation>(path(businessId), {
    method: "POST",
    body: JSON.stringify({ title: "Cuộc trò chuyện mới" }),
  });
}

export function getConversation(businessId: string, conversationId: string) {
  return apiRequest<AssistantConversationDetail>(`${path(businessId)}/${conversationId}`);
}

export type AskInput = {
  question: string;
  date_from: string;
  date_to: string;
};

export function askAssistant(
  businessId: string,
  conversationId: string,
  input: AskInput,
) {
  return apiRequest<AssistantReply>(`${path(businessId)}/${conversationId}/messages`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}
