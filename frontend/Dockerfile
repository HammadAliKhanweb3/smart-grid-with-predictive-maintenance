 # --- STAGE 1: Base & Dependencies ---

FROM node:20-alpine AS base

# Set up pnpm environment

ENV PNPM_HOME="/pnpm"

ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable && corepack prepare pnpm@latest --activate


WORKDIR /app


# Copy dependency files first for better caching

COPY package.json pnpm-lock.yaml* ./

RUN pnpm install --frozen-lockfile



# --- STAGE 2: Development ---

# This stage is what your docker-compose will use locally

FROM base AS dev

WORKDIR /app

# Copy node_modules from base

COPY --from=base /app/node_modules ./node_modules

# Copy all source files

COPY . .

ENV NODE_ENV=development

ENV NEXT_TELEMETRY_DISABLED=1


EXPOSE 3000

# Hot-reloading dev server

CMD ["pnpm", "dev"]



# --- STAGE 3: Builder (Production Build) ---

# This stage compiles the code but isn't the final image

FROM base AS builder

WORKDIR /app

COPY --from=base /app/node_modules ./node_modules

COPY . .

# Important: next.config.js must have output: 'standalone'

RUN pnpm run build



# --- STAGE 4: Production Runner ---

# This is the tiny, secure final image for the cloud

FROM node:20-alpine AS runner

WORKDIR /app


ENV NODE_ENV=production

ENV NEXT_TELEMETRY_DISABLED=1


# Security: Don't run as root

RUN addgroup --system --gid 1001 nodejs

RUN adduser --system --uid 1001 nextjs


# Copy only the compiled standalone app (very small)

COPY --from=builder /app/public ./public

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static


USER nextjs


EXPOSE 3000

ENV PORT=3000

ENV HOSTNAME="0.0.0.0"


# Production server (much faster than pnpm dev)

CMD ["node", "server.js"] 