import type { SVGProps } from 'react'

const base = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  viewBox: '0 0 24 24',
  'aria-hidden': true,
} as const

type Props = SVGProps<SVGSVGElement>

export const Logo = (p: Props) => (
  <svg viewBox="0 0 64 64" aria-hidden="true" {...p}>
    <rect width="64" height="64" rx="14" fill="#14161c" />
    <rect x="10" y="23" width="7" height="18" rx="2.5" fill="#ff5a1f" />
    <rect x="47" y="23" width="7" height="18" rx="2.5" fill="#ff5a1f" />
    <rect x="17" y="27" width="5" height="10" rx="2" fill="#ff5a1f" />
    <rect x="42" y="27" width="5" height="10" rx="2" fill="#ff5a1f" />
    <rect x="22" y="30" width="20" height="4" rx="2" fill="#f6f5f2" />
  </svg>
)
export const FlameIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M12 3c1 3.5 5 5.5 5 10a5 5 0 0 1-10 0c0-2.2 1-3.6 2-4.6.2 1.6 1 2.6 2 2.6 0-3 0-5.5 1-8z" />
  </svg>
)
export const DumbbellIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M6.5 6.5v11M3.5 9v6M17.5 6.5v11M20.5 9v6M6.5 12h11" />
  </svg>
)
export const BarbellIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M2 12h20M5 7v10M8 5v14M16 5v14M19 7v10" />
  </svg>
)
export const HeartIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" />
    <path d="M7.5 12h2.5l1.2-2 1.6 4 1.2-2h2.5" />
  </svg>
)
export const PrintIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M7 9V3h10v6M7 17H4v-7h16v7h-3M7 14h10v7H7z" />
  </svg>
)
export const EditIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M4 20h4l10.5-10.5a2.1 2.1 0 0 0-3-3L5 17v3z" />
  </svg>
)
export const SwapIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M7 4 3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7" />
  </svg>
)
export const AlertIcon = (p: Props) => (
  <svg {...base} {...p}>
    <path d="M12 4 2.5 20h19z" />
    <path d="M12 10v4.5M12 17.5v.01" />
  </svg>
)
