import "./instrument.mjs";
import * as Sentry from "@sentry/node";
import express from "express";
import { randomUUID } from "node:crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";

import { checkoutTool } from "./tools/checkout.js";
import { getProductsTool } from "./tools/get-products.js";
import { productsResource } from "./resources/products.js";

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
          logging: {},
        },
      })
    );

    // Tools
    server.registerTool("checkout", checkoutTool, checkoutTool.handler);
    server.registerTool("get-products", getProductsTool, getProductsTool.handler);

    // Resources
    server.registerResource(
      "products",
      productsResource.template,
      productsResource.metadata,
      productsResource.handler
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

console.log("🚀 MCP Server starting...");

const server = app.listen(Number(port), () => {
  console.log(`📡 Server running on port ${port}`);
  console.log(`🔗 MCP Streamable HTTP endpoint: http://localhost:${port}/mcp`);
  console.log(`🏠 Home: http://localhost:${port}/`);
});

process.on("SIGINT", () => {
  console.log("\n🛑 Received SIGINT, shutting down gracefully...");
  server.close(() => {
    process.exit(0);
  });
});

process.on("SIGTERM", () => {
  console.log("\n🛑 Received SIGTERM, shutting down gracefully...");
  server.close(() => {
    process.exit(0);
  });
});
