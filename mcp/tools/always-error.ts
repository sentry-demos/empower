import { z } from "zod";
import { maybeThrow } from "../utils.js";

export const alwaysErrorTool = {
  title: "Always Error",
  annotations: {
    description:
      "A tool that always throws an error for testing error handling",
  },
  inputSchema: {
    message: z.string().optional().describe("Optional custom error message"),
  },
  handler: async ({ message }: { message?: string }): Promise<any> => {
    maybeThrow(1, new Error(message || "This tool always throws an error"));
    return "Should never see this";
  },
};
