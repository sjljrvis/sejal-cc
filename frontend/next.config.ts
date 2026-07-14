import type { NextConfig } from 'next'

// Handle basePath - Next.js requires either empty string or path starting with /
// but NOT just "/" alone
const getBasePath = () => {
  const path = process.env.NEXT_PUBLIC_BASE_PATH || ''
  // "/" is not a valid basePath, treat it as empty
  if (path === '/') return ''
  return path
}

// Where Next should proxy backend /api/* calls (server-side rewrite target).
// The FastAPI backend runs alongside Next: idp/local dev on localhost:8001,
// docker-compose as the `backend` service (set INTERNAL_API_URL there).
const getBackendOrigin = () =>
  process.env.INTERNAL_API_URL || 'http://localhost:8001'

const nextConfig: NextConfig = {
  // --- BASE_PATH ADDITION START ---
  basePath: getBasePath(),
  // --- BASE_PATH ADDITION END ---

  env: {
    // Empty => the browser calls the API on the SAME origin it was served from
    // (e.g. the preview host) and the rewrites() below proxy it to the backend.
    // This avoids hard-coding localhost / a per-deploy host into client bundles.
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
    INTERNAL_API_URL: process.env.INTERNAL_API_URL || 'http://backend:8000',
  },
  serverExternalPackages: [],

  // Proxy backend /api/* to FastAPI so the browser only ever talks to this same
  // origin (keeps auth cookies first-party and works behind any preview host).
  // Ordering matters because the backend and NextAuth share the /api/auth/*
  // namespace, and NextAuth's [...nextauth] handler is an App Router *dynamic*
  // route:
  //   - beforeFiles runs BEFORE everything, so it claims the two backend
  //     endpoints that NextAuth's [...nextauth] catch-all would otherwise
  //     swallow (/api/auth/register, /api/auth/pending-status).
  //   - fallback runs AFTER dynamic routes, so NextAuth keeps all of its routes
  //     (/api/auth/signin|callback|session|csrf|providers|signout, /logout) and
  //     only the /api/* paths Next has no route for (admin, audit, items, ai,
  //     examples, health) fall through to the backend. (afterFiles would run
  //     *before* the dynamic [...nextauth] route and hijack /api/auth/signin.)
  async rewrites() {
    const backend = getBackendOrigin()
    return {
      beforeFiles: [
        { source: '/api/auth/register', destination: `${backend}/api/auth/register` },
        { source: '/api/auth/pending-status', destination: `${backend}/api/auth/pending-status` },
      ],
      fallback: [
        { source: '/api/:path*', destination: `${backend}/api/:path*` },
      ],
    }
  },

  // Enable source maps for production debugging
  productionBrowserSourceMaps: true,

  // Ensure TypeScript errors fail the build
  typescript: {
    ignoreBuildErrors: false,
  },

  // Development optimizations
  ...(process.env.NODE_ENV === 'development' && {
    experimental: {
      optimizePackageImports: ['@radix-ui/react-icons', 'lucide-react'],
    },

    // Optimize bundling for development
    webpack: (config: any, { dev }: { dev: boolean }) => {
      if (dev) {
        config.watchOptions = {
          poll: 1000,
          aggregateTimeout: 300,
          ignored: /node_modules/,
        }
        config.infrastructureLogging = { level: 'error' }
      }
      return config
    },
  }),
}

export default nextConfig
