'use client'

import { useState, useRef, useEffect } from 'react'
import { signIn } from 'next-auth/react'
import { motion, useInView } from 'framer-motion'
import apiClient from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CardWatermark } from '@/components/ui/card-watermark'
import { Icons } from '@/components/ui/icons'
import { Logomark } from '@/components/brand'
import { Skeleton, SkeletonCard } from '@/components/ui/skeleton'
import { ActivityChart } from '@/components/ActivityChart'
import { useSessionRefresh } from '@/hooks'
import { cn } from '@/lib/utils'

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  },
}

// Animated number component
function AnimatedNumber({
  value,
  suffix = '',
  duration = 1000,
}: {
  value: number
  suffix?: string
  duration?: number
}) {
  const [displayValue, setDisplayValue] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true, amount: 0.5 })
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (!isInView || hasAnimated.current) return
    hasAnimated.current = true

    const startTime = performance.now()

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(2, -10 * progress)

      setDisplayValue(Math.round(eased * value))

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        setDisplayValue(value)
      }
    }

    requestAnimationFrame(animate)
  }, [value, duration, isInView])

  const formatValue = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  return (
    <span ref={ref}>
      {formatValue(displayValue)}
      {suffix}
    </span>
  )
}

// Stats Card Component with Bento styling
interface StatCardProps {
  title: string
  value: number
  suffix?: string
  icon: React.ElementType
  trend?: { value: string; positive: boolean }
  colorClass: string
  delay?: number
}

function StatCard({
  title,
  value,
  suffix = '',
  icon: Icon,
  trend,
  colorClass,
  delay = 0,
}: StatCardProps) {
  return (
    <motion.div
      variants={itemVariants}
      initial='hidden'
      animate='visible'
      transition={{ delay }}
      whileHover={{ y: -4 }}
    >
      <Card className='group relative h-full cursor-default overflow-hidden'>
        {/* Branded watermark texture */}
        <CardWatermark opacity={3} scale={0.9} />
        <CardContent className='relative z-10 p-5'>
          <div className='flex items-start justify-between'>
            <div className='space-y-2'>
              {/* Micro label */}
              <p className='text-micro uppercase text-brand-muted transition-colors duration-200 group-hover:text-brand-cornflower'>
                {title}
              </p>
              {/* Display number */}
              <p className='font-display text-[2.25rem] font-bold leading-none tracking-tight text-brand-navy'>
                <AnimatedNumber value={value} suffix={suffix} />
              </p>
              {/* Trend */}
              {trend && (
                <motion.p
                  className={cn(
                    'flex items-center gap-1 text-xs font-medium',
                    trend.positive ? 'text-emerald-600' : 'text-red-500'
                  )}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: delay + 0.3 }}
                >
                  {trend.positive ? (
                    <Icons.trendingUp className='h-3 w-3' strokeWidth={2} />
                  ) : (
                    <Icons.trendingUp
                      className='h-3 w-3 rotate-180'
                      strokeWidth={2}
                    />
                  )}
                  {trend.value}
                </motion.p>
              )}
            </div>
            {/* Icon */}
            <motion.div
              className={cn(
                'rounded-xl p-2.5 text-white',
                'shadow-lg',
                colorClass
              )}
              whileHover={{ scale: 1.15, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400, damping: 17 }}
            >
              <Icon className='h-5 w-5' strokeWidth={1.5} />
            </motion.div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

// Hero Section
function HeroSection({ userName }: { userName?: string }) {
  const firstName = userName?.split(' ')[0] || 'there'

  return (
    <motion.div
      className='col-span-12 py-2'
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      <h1 className='text-display-3 font-bold tracking-tight text-brand-navy lg:text-display-2'>
        Where Intelligence <br className='hidden sm:block' />
        <span className='text-gradient'>Meets Human.</span>
      </h1>
      <p className='mt-4 text-lg font-light text-muted-foreground'>
        Welcome back, {firstName}. Your AI Command Center is ready.
      </p>
    </motion.div>
  )
}

// Diagnostics Card
function DiagnosticsCard() {
  const [apiResponse, setApiResponse] = useState<string>('')
  const [adminResponse, setAdminResponse] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const callApi = async (
    endpoint: string,
    setter: React.Dispatch<React.SetStateAction<string>>
  ) => {
    setIsLoading(true)
    setter('Loading...')
    try {
      const data = await apiClient(endpoint)
      setter(JSON.stringify(data, null, 2))
    } catch (error) {
      setter(
        `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className='relative col-span-12 h-full overflow-hidden'>
      <CardWatermark opacity={3} scale={1.1} />
      <CardHeader className='relative z-10'>
        <CardTitle className='flex items-center gap-2'>
          <Icons.activity
            className='h-5 w-5 text-brand-cornflower'
            strokeWidth={1.5}
          />
          System Diagnostics
        </CardTitle>
      </CardHeader>
      <CardContent className='relative z-10 space-y-6'>
        <div className='space-y-3'>
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-sm font-medium text-foreground'>
                Standard Authorization
              </p>
              <p className='mt-0.5 font-mono text-xs text-muted-foreground'>
                /api/test
              </p>
            </div>
          </div>
          <Button
            onClick={() => callApi('/api/test', setApiResponse)}
            disabled={isLoading}
            variant='outline'
            className='w-full'
          >
            {isLoading ? 'Running...' : 'Run Diagnostics'}
          </Button>
          {apiResponse && (
            <div className='rounded-xl border border-border/50 bg-muted/30 p-4'>
              <pre className='overflow-x-auto font-mono text-xs text-muted-foreground'>
                <code>{apiResponse}</code>
              </pre>
            </div>
          )}
        </div>

        <div className='h-px bg-border/50' />

        <div className='space-y-3'>
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-sm font-medium text-foreground'>
                Admin Verification
              </p>
              <p className='mt-0.5 font-mono text-xs text-muted-foreground'>
                /api/admin/dashboard
              </p>
            </div>
          </div>
          <Button
            onClick={() => callApi('/api/admin/dashboard', setAdminResponse)}
            disabled={isLoading}
            variant='gradient'
            className='w-full'
          >
            {isLoading ? 'Verifying...' : 'Verify Admin Access'}
            <Icons.arrowRight className='ml-2 h-4 w-4' />
          </Button>
          {adminResponse && (
            <div className='rounded-xl border border-border/50 bg-muted/30 p-4'>
              <pre className='overflow-x-auto font-mono text-xs text-muted-foreground'>
                <code>{adminResponse}</code>
              </pre>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Loading skeleton for dashboard
function DashboardSkeleton() {
  return (
    <div
      className='space-y-6'
      role='status'
      aria-live='polite'
      aria-label='Loading dashboard'
    >
      {/* Screen reader announcement */}
      <span className='sr-only'>Loading dashboard content...</span>

      {/* Hero skeleton */}
      <div className='space-y-4 py-2'>
        <Skeleton className='h-12 w-3/4 max-w-md' />
        <Skeleton className='h-6 w-1/2 max-w-sm' />
      </div>

      {/* Stats skeleton */}
      <div className='grid grid-cols-2 gap-4 lg:grid-cols-4'>
        {[...Array(4)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>

      {/* Cards skeleton */}
      <div className='grid gap-6 lg:grid-cols-12'>
        <div className='lg:col-span-7'>
          <SkeletonCard className='h-[300px]' />
        </div>
        <div className='lg:col-span-5'>
          <SkeletonCard className='h-[300px]' />
        </div>
      </div>
    </div>
  )
}

// Sign-in Card
function SignInCard() {
  return (
    <div className='flex min-h-[500px] items-center justify-center'>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
      >
        <Card className='relative w-full max-w-md overflow-hidden bg-white shadow-float-lg transition-shadow duration-500 hover:shadow-accent'>
          <CardWatermark opacity={4} scale={1} />
          <CardHeader className='relative z-10 space-y-4 pb-8 text-center'>
            <motion.div
              className='mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-brand-navy shadow-xl'
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{
                delay: 0.2,
                type: 'spring',
                stiffness: 200,
                damping: 15,
              }}
            >
              <Logomark variant='light' size={48} />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              <CardTitle className='text-display-5 font-bold text-brand-navy'>
                Supervity
              </CardTitle>
              <p className='mt-2 text-muted-foreground'>
                Command Center Access
              </p>
            </motion.div>
          </CardHeader>
          <CardContent className='relative z-10 space-y-4 px-8 pb-8'>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.4 }}
            >
              <Button
                onClick={() => signIn('keycloak', { callbackUrl: '/' })}
                variant='gradient'
                size='lg'
                className='group w-full py-6 text-base'
              >
                Sign In with SSO
                <Icons.arrowRight className='ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-1' />
              </Button>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

// Pending Approval Card - shown to users awaiting admin approval
function PendingApprovalCard({ userName }: { userName?: string }) {
  const firstName = userName?.split(' ')[0] || 'there'

  return (
    <div className='flex min-h-[500px] items-center justify-center'>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
        className='w-full max-w-lg'
      >
        <Card className='relative overflow-hidden bg-white shadow-float-lg'>
          <CardWatermark opacity={4} scale={1} />
          <CardHeader className='relative z-10 space-y-4 pb-6 text-center'>
            <motion.div
              className='mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-amber-500 shadow-xl'
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                delay: 0.2,
                type: 'spring',
                stiffness: 200,
                damping: 15,
              }}
            >
              <Icons.clock className='h-10 w-10 text-white' />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              <CardTitle className='text-display-5 font-bold text-brand-navy'>
                Account Pending Approval
              </CardTitle>
              <p className='mt-2 text-muted-foreground'>
                Welcome, {firstName}!
              </p>
            </motion.div>
          </CardHeader>
          <CardContent className='relative z-10 space-y-6 px-8 pb-8'>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.4 }}
              className='space-y-4'
            >
              <div className='rounded-xl border border-amber-200 bg-amber-50 p-4 text-center'>
                <p className='text-sm text-amber-800'>
                  Your account has been created successfully, but it requires admin approval before you can access the full Command Center.
                </p>
              </div>

              <div className='space-y-3 rounded-xl border border-gray-100 bg-gray-50 p-4'>
                <h3 className='font-medium text-gray-900'>What happens next?</h3>
                <ul className='space-y-2 text-sm text-gray-600'>
                  <li className='flex items-start gap-2'>
                    <Icons.checkCircle className='mt-0.5 h-4 w-4 text-emerald-500 shrink-0' />
                    <span>An administrator will review your registration</span>
                  </li>
                  <li className='flex items-start gap-2'>
                    <Icons.checkCircle className='mt-0.5 h-4 w-4 text-emerald-500 shrink-0' />
                    <span>You&apos;ll receive an email once approved</span>
                  </li>
                  <li className='flex items-start gap-2'>
                    <Icons.checkCircle className='mt-0.5 h-4 w-4 text-emerald-500 shrink-0' />
                    <span>Then you can access all Command Center features</span>
                  </li>
                </ul>
              </div>

              <p className='text-center text-xs text-muted-foreground'>
                Need urgent access? Contact your administrator.
              </p>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

// Main Dashboard
export default function HomePage() {
  const { session, status } = useSessionRefresh()

  if (status === 'loading') {
    return <DashboardSkeleton />
  }

  if (status !== 'authenticated') {
    return <SignInCard />
  }

  // Check if user has pending role (and not user or admin roles)
  const roles = session?.roles || []
  const isPending = roles.includes('pending') && !roles.includes('user') && !roles.includes('admin')

  if (isPending) {
    return <PendingApprovalCard userName={session?.user?.name || undefined} />
  }

  return (
    <motion.div
      className='space-y-6'
      variants={containerVariants}
      initial='hidden'
      animate='visible'
    >
      {/* Hero Section */}
      <HeroSection userName={session?.user?.name || undefined} />

      {/* Stats Grid - Bento style */}
      <div className='grid grid-cols-2 gap-4 lg:grid-cols-4'>
        <StatCard
          title='Total Users'
          value={10400}
          icon={Icons.users}
          trend={{ value: '+12%', positive: true }}
          colorClass='bg-brand-navy'
          delay={0.1}
        />
        <StatCard
          title='Active Sessions'
          value={524}
          icon={Icons.activity}
          trend={{ value: '+8%', positive: true }}
          colorClass='bg-brand-cornflower'
          delay={0.2}
        />
        <StatCard
          title='Success Rate'
          value={98}
          suffix='%'
          icon={Icons.checkCircle}
          trend={{ value: '+2%', positive: true }}
          colorClass='bg-brand-purple'
          delay={0.3}
        />
        <StatCard
          title='AI Confidence'
          value={96}
          suffix='%'
          icon={Icons.sparkles}
          trend={{ value: 'Stable', positive: true }}
          colorClass='bg-gradient-to-br from-brand-navy to-brand-purple'
          delay={0.4}
        />
      </div>

      {/* Activity Chart - Full Width */}
      <motion.div variants={itemVariants}>
        <ActivityChart className='col-span-12' />
      </motion.div>

      {/* System Diagnostics */}
      <motion.div
        className='grid gap-6 lg:grid-cols-12'
        variants={itemVariants}
      >
        <DiagnosticsCard />
      </motion.div>
    </motion.div>
  )
}
