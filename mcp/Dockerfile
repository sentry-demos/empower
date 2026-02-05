# Use Node.js LTS Alpine for minimal size
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@10.11.0

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN pnpm build

# Expose port (Cloud Run sets PORT env var, app reads from process.env.PORT)
EXPOSE 8080

# Start the server
CMD ["pnpm", "start"]
