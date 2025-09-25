
import 'dotenv/config';
import { Mastra } from '@mastra/core/mastra';
import { PinoLogger } from '@mastra/loggers';
import { LibSQLStore } from '@mastra/libsql';
import { weatherWorkflow } from './workflows/weather-workflow';
import { weatherAgent } from './agents/weather-agent';
import { plantAdvisorAgent } from './agents/plant-advisor-agent';
import { mastraLogger } from './logger';


export const mastra = new Mastra({
  workflows: { weatherWorkflow },
  agents: { weatherAgent, plantAdvisorAgent },
  storage: new LibSQLStore({
    // stores telemetry, evals, ... into memory storage, if it needs to persist, change to file:../mastra.db
    url: ":memory:",
  }),
  logger: mastraLogger,
});
