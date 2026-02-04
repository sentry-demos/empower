import "./instrument.mjs";
import * as Sentry from "@sentry/node";
import express from "express";
import { randomUUID } from "node:crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

import { getProductsTool } from "./tools/get-products.js";
import { getPlantCareGuideTool } from "./tools/get-plant-care-guide.js";
import { checkoutTool } from "./tools/checkout.js";
import { alwaysErrorTool } from "./tools/always-error.js";
import { seasonalCalendarResource } from "./resources/seasonal-calendar.js";
import { plantDiagnosticsResource } from "./resources/plant-diagnostics.js";
import { seasonalCareGuidePrompt } from "./prompts/seasonal-care-guide.js";
import { plantShoppingAssistantPrompt } from "./prompts/plant-shopping-assistant.js";
import { newPlantParentPrompt } from "./prompts/new-plant-parent.js";
import { plantSymptomsResource } from "./resources/plant-symptoms.js";

import { CallerScript } from "./caller-script.js";

const app = express();
app.use(express.json());

const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

app.get("/", (req, res) => {
  res.send(`
  <h1>Empower Plant MCP Server</h1>
  <p>This is a MCP server for the Empower Plant API.</p>
  <p>You can use the following endpoints to interact with the server:</p>
  <ul>
    <li><a href="/mcp">/mcp - MCP Streamable HTTP </a></li>
  </ul>
  <p>You can use MCP inspector to interact with the server.</p>
  <p>Run:</p>
  <pre>npx @modelcontextprotocol/inspector</pre>
  `);
});

app.post("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  let transport: StreamableHTTPServerTransport;

  if (sessionId && transports[sessionId]) {
    transport = transports[sessionId];
  } else if (!sessionId && isInitializeRequest(req.body)) {
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (sessionId) => {
        transports[sessionId] = transport;
      },
    });

    transport.onclose = () => {
      if (transport.sessionId) {
        delete transports[transport.sessionId];
      }
    };

    const server = Sentry.wrapMcpServerWithSentry(
      new McpServer({
        name: "demo-server",
        version: "1.0.0",
        capabilities: {
          tools: { listChanged: true },
          resources: { listChanged: true },
          prompts: { listChanged: true },
          logging: {},
        },
      })
    );

    server.registerTool(
      "get-products",
      getProductsTool,
      getProductsTool.handler
    );
    server.registerTool(
      "get-plant-care-guide",
      getPlantCareGuideTool,
      getPlantCareGuideTool.handler
    );
    server.registerTool("checkout", checkoutTool, checkoutTool.handler);
    server.registerTool(
      "always-error",
      alwaysErrorTool,
      alwaysErrorTool.handler
    );

    server.registerResource(
      "seasonal-calendar",
      seasonalCalendarResource.template,
      seasonalCalendarResource.metadata,
      seasonalCalendarResource.handler
    );

    server.registerResource(
      "plant-diagnostics",
      plantDiagnosticsResource.template,
      plantDiagnosticsResource.metadata,
      plantDiagnosticsResource.handler
    );

    server.registerResource(
      "plant-symptoms",
      plantSymptomsResource.template,
      plantSymptomsResource.metadata,
      plantSymptomsResource.handler
    );

    server.registerPrompt(
      "seasonal-care-guide",
      seasonalCareGuidePrompt.metadata,
      seasonalCareGuidePrompt.handler
    );
    server.registerPrompt(
      "plant-shopping-assistant",
      plantShoppingAssistantPrompt.metadata,
      plantShoppingAssistantPrompt.handler
    );
    server.registerPrompt(
      "new-plant-parent",
      newPlantParentPrompt.metadata,
      newPlantParentPrompt.handler
    );

    await server.connect(transport);
  } else {
    res.status(400).json({
      jsonrpc: "2.0",
      error: {
        code: -32000,
        message: "Bad Request: No valid session ID provided",
      },
      id: null,
    });
    return;
  }

  await transport.handleRequest(req, res, req.body);

  // 20% chance to emit a fake stdio span to make transport widget show something
  // else than StreamableHTTP
  if (Math.random() < 0.2) {
    Sentry.startSpan({ op: "mcp.server", name: "handleRequest" }, (span) => {
      span.setAttribute("mcp.transport", "stdio");
    });
  }
});

const handleSessionRequest = async (
  req: express.Request,
  res: express.Response
) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  if (!sessionId || !transports[sessionId]) {
    res.status(400).send("Invalid or missing session ID");
    return;
  }

  const transport = transports[sessionId];
  await transport.handleRequest(req, res);
};

app.get("/mcp", handleSessionRequest);

// Handle DELETE requests for session termination
app.delete("/mcp", handleSessionRequest);

const port = process.env.PORT || 3000;
const enableCallerScript = process.argv.includes("--caller-script");

console.log("🚀 MCP Server starting...");

let callerScript: CallerScript | null = null;

const server = app.listen(Number(port), () => {
  console.log(`📡 Server running on port ${port}`);
  console.log(`🔗 MCP Streamable HTTP endpoint: http://localhost:${port}/mcp`);
  console.log(`🏠 Home: http://localhost:${port}/`);

  if (enableCallerScript) {
    console.log("🎨 Starting caller script...");
    callerScript = new CallerScript();

    setTimeout(async () => {
      try {
        if (callerScript) {
          await callerScript.start();
        }
      } catch (error) {
        console.error("❌ Failed to start caller script:", error);
      }
    }, 2000);
  }
});

process.on("SIGINT", async () => {
  console.log("\n🛑 Received SIGINT, shutting down gracefully...");
  if (callerScript) {
    await callerScript.stop();
  }
  server.close(() => {
    process.exit(0);
  });
});

process.on("SIGTERM", async () => {
  console.log("\n🛑 Received SIGTERM, shutting down gracefully...");
  if (callerScript) {
    await callerScript.stop();
  }
  server.close(() => {
    process.exit(0);
  });
});
