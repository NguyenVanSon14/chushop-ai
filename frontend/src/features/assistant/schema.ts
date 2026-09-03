import { z } from "zod";

export const assistantQuestionSchema = z.object({
  question: z.string().trim().min(2, "Hãy nhập câu hỏi").max(1000, "Câu hỏi quá dài"),
  date_from: z.string().date("Ngày bắt đầu không hợp lệ"),
  date_to: z.string().date("Ngày kết thúc không hợp lệ"),
}).refine((value) => value.date_from <= value.date_to, {
  message: "Ngày bắt đầu phải trước ngày kết thúc",
  path: ["date_to"],
});

export type AssistantQuestionInput = z.infer<typeof assistantQuestionSchema>;
