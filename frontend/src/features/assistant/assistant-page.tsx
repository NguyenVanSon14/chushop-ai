"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useHasAccessToken } from "@/features/auth/use-auth-token";
import { useActiveBusiness, useBusinesses } from "@/features/businesses/hooks";
import type { AssistantMessage } from "@/lib/api/types";
import {
  useAskAssistant,
  useConversation,
  useConversations,
  useCreateConversation,
} from "./hooks";
import { assistantQuestionSchema } from "./schema";

const suggestions = [
  "Tháng này tôi lời bao nhiêu?",
  "Sản phẩm nào lời nhiều nhất?",
  "Sản phẩm nào đang bán lỗ?",
  "Chi phí nào lớn nhất?",
  "Tại sao lợi nhuận tuần này giảm?",
  "Shopee hay TikTok mang lại lợi nhuận cao hơn?",
];

function localDate(value: Date) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function currentMonth() {
  const today = new Date();
  return {
    from: localDate(new Date(today.getFullYear(), today.getMonth(), 1)),
    to: localDate(today),
  };
}

export function AssistantPage() {
  const router = useRouter();
  const authenticated = useHasAccessToken();
  const businesses = useBusinesses(authenticated);
  const business = useActiveBusiness(businesses.data);
  const conversations = useConversations(business?.id);
  const [selectedId, setSelectedId] = useState<string>();
  const activeId = conversations.data
    ? conversations.data.find((conversation) => conversation.id === selectedId)?.id
      ?? conversations.data[0]?.id
    : undefined;
  const selectedConversation = useConversation(business?.id, activeId);
  const createConversation = useCreateConversation(business?.id ?? "");
  const askAssistant = useAskAssistant(business?.id ?? "");
  const [question, setQuestion] = useState("");
  const [period, setPeriod] = useState(currentMonth);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    if (!authenticated) router.replace("/login");
  }, [authenticated, router]);

  async function startConversation() {
    setFormError("");
    try {
      const created = await createConversation.mutateAsync();
      setSelectedId(created.id);
      setQuestion("");
    } catch {
      setFormError("Không thể tạo cuộc trò chuyện.");
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setFormError("");
    const parsed = assistantQuestionSchema.safeParse({
      question,
      date_from: period.from,
      date_to: period.to,
    });
    if (!parsed.success) {
      setFormError(parsed.error.issues[0]?.message ?? "Câu hỏi không hợp lệ.");
      return;
    }
    try {
      let conversationId = activeId;
      if (!conversationId) {
        const created = await createConversation.mutateAsync();
        conversationId = created.id;
        setSelectedId(created.id);
      }
      await askAssistant.mutateAsync({ conversationId, input: parsed.data });
      setQuestion("");
    } catch {
      setFormError("Trợ lý chưa thể trả lời. Vui lòng thử lại.");
    }
  }

  if (!authenticated || businesses.isLoading) return <Status text="Đang tải trợ lý..." />;
  if (!business) return <Status text="Bạn cần tạo doanh nghiệp trước." />;

  const messages = selectedConversation.data?.messages ?? [];
  const pending = createConversation.isPending || askAssistant.isPending;

  return (
    <AppShell businessId={business.id} businessName={business.name} businesses={businesses.data ?? []} wide>
      <div className="grid gap-5 xl:grid-cols-[280px_1fr]">
        <aside className="rounded-2xl border border-[var(--border)] bg-white p-4 xl:min-h-[680px]">
          <Button className="w-full" disabled={createConversation.isPending} onClick={startConversation}>+ Cuộc trò chuyện mới</Button>
          <h2 className="mt-6 text-xs font-bold uppercase tracking-[0.14em] text-[var(--muted)]">Lịch sử</h2>
          {conversations.isLoading && <p className="mt-3 text-sm text-[var(--muted)]">Đang tải...</p>}
          {conversations.isError && <p className="mt-3 text-sm text-red-700">Không thể tải lịch sử.</p>}
          {conversations.data?.length === 0 && <p className="mt-3 text-sm text-[var(--muted)]">Chưa có cuộc trò chuyện.</p>}
          <div className="mt-2 flex gap-2 overflow-x-auto xl:flex-col">
            {conversations.data?.map((conversation) => (
              <button key={conversation.id} className={`min-w-52 rounded-xl px-3 py-3 text-left text-sm xl:min-w-0 ${activeId === conversation.id ? "bg-green-50 font-semibold text-green-900" : "hover:bg-gray-50"}`} onClick={() => setSelectedId(conversation.id)}>{conversation.title}</button>
            ))}
          </div>
        </aside>

        <Card className="flex min-h-[680px] flex-col overflow-hidden">
          <div className="border-b border-[var(--border)] p-5 sm:flex sm:items-center sm:justify-between">
            <div><p className="text-sm font-bold text-green-700">TRỢ LÝ MONEY BRAIN</p><h1 className="mt-1 text-2xl font-bold">Hỏi về tài chính shop</h1></div>
            <div className="mt-3 flex gap-2 sm:mt-0">
              <DateInput label="Từ" value={period.from} onChange={(from) => setPeriod((old) => ({ ...old, from }))} />
              <DateInput label="Đến" value={period.to} onChange={(to) => setPeriod((old) => ({ ...old, to }))} />
            </div>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto bg-[#fbfcf8] p-5 sm:p-7" aria-live="polite">
            {selectedConversation.isLoading && <p className="text-center text-[var(--muted)]">Đang tải hội thoại...</p>}
            {selectedConversation.isError && <p className="text-center text-red-700">Không thể tải hội thoại.</p>}
            {messages.length === 0 && !selectedConversation.isLoading && <Welcome onSelect={setQuestion} />}
            {messages.map((message) => <MessageBubble key={message.id} message={message} />)}
            {askAssistant.isPending && <div className="max-w-[85%] rounded-2xl bg-white p-4 text-sm text-[var(--muted)] shadow-sm">Đang đọc báo cáo Money Brain...</div>}
          </div>

          <form className="border-t border-[var(--border)] bg-white p-4 sm:p-5" onSubmit={submit}>
            <div className="mb-3 flex flex-wrap gap-2">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => setQuestion(suggestion)}
                  className="rounded-full border border-emerald-200 bg-emerald-50/60 px-3 py-1 text-xs font-semibold text-emerald-800 transition hover:bg-emerald-100"
                >
                  💡 {suggestion}
                </button>
              ))}
            </div>
            <textarea className="min-h-24 w-full resize-none rounded-xl border border-[var(--border)] p-3 outline-none focus:border-green-700" maxLength={1000} placeholder="Ví dụ: Tháng này tôi lời bao nhiêu?" value={question} onChange={(event) => setQuestion(event.target.value)} />
            <div className="mt-3 flex items-center justify-between gap-3">
              <p className="text-sm text-red-700">{formError}</p>
              <Button disabled={pending} type="submit">{pending ? "Đang xử lý..." : "Gửi câu hỏi"}</Button>
            </div>
          </form>
        </Card>
      </div>
    </AppShell>
  );
}

function Welcome({ onSelect }: { onSelect: (question: string) => void }) {
  return <div className="mx-auto max-w-2xl py-8 text-center"><div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-green-100 text-2xl">₫</div><h2 className="mt-4 text-xl font-bold">Mình có thể giúp bạn đọc số liệu</h2><p className="mt-2 text-sm text-[var(--muted)]">Mọi con số đều lấy từ Money Brain; trợ lý không tự đoán hay tự sửa dữ liệu.</p><div className="mt-6 grid gap-2 sm:grid-cols-2">{suggestions.map((suggestion) => <button key={suggestion} className="rounded-xl border border-[var(--border)] bg-white p-3 text-left text-sm hover:border-green-600 hover:bg-green-50" onClick={() => onSelect(suggestion)} type="button">{suggestion}</button>)}</div></div>;
}

function MessageBubble({ message }: { message: AssistantMessage }) {
  const assistant = message.role === "ASSISTANT";
  return <div className={`flex ${assistant ? "justify-start" : "justify-end"}`}><div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${assistant ? "bg-white" : "bg-green-800 text-white"}`}><p>{message.content}</p>{assistant && message.tool_name && <p className="mt-2 text-xs text-[var(--muted)]">Nguồn: Money Brain · {message.tool_name}</p>}</div></div>;
}

function DateInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="text-xs font-semibold text-[var(--muted)]">{label}<input className="mt-1 block w-full rounded-lg border border-[var(--border)] px-2 py-1.5 text-sm text-[var(--foreground)]" type="date" value={value} onChange={(event) => onChange(event.target.value)} /></label>;
}

function Status({ text }: { text: string }) {
  return <main className="flex min-h-screen items-center justify-center p-6 text-[var(--muted)]">{text}</main>;
}
