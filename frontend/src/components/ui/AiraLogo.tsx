import React from 'react';
import { cn } from '../../lib/utils';

export interface AiraLogoProps {
  variant?: 'full' | 'mark' | 'horizontal' | 'wordmark';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  subtitle?: string | boolean;
  showFullSubtitle?: boolean;
  className?: string;
  markClassName?: string;
  textClassName?: string;
  badge?: boolean;
}

/**
 * logo.png is exactly 2:1 landscape (1774x887).
 * We size the image by HEIGHT and let width be auto (2x height).
 * This preserves the aspect ratio perfectly at every size.
 */
const sizeMap = {
  xs: { h: 20,  text: 'text-sm',   sub: 'text-[8px]',   gap: 'gap-2'   },
  sm: { h: 28,  text: 'text-base', sub: 'text-[9.5px]', gap: 'gap-2'   },
  md: { h: 36,  text: 'text-xl',   sub: 'text-[11px]',  gap: 'gap-2.5' },
  lg: { h: 46,  text: 'text-2xl',  sub: 'text-xs',      gap: 'gap-3'   },
  xl: { h: 56,  text: 'text-3xl',  sub: 'text-sm',      gap: 'gap-3.5' },
};

export const FULL_BRAND_NAME = 'Autonomous Investment Research & Analysis';

/**
 * AiraBrandMark — renders /logo.png at the correct aspect ratio (2:1).
 * height = h, width = auto (never squash or stretch).
 */
export const AiraBrandMark: React.FC<{
  /** Height in px — width is always calculated automatically (2:1 ratio) */
  size?: number;
  className?: string;
  badge?: boolean;
}> = ({ size = 32, className }) => (
  <img
    src="/logo.png"
    alt="AIRA"
    draggable={false}
    className={cn('shrink-0 select-none object-contain', className)}
    style={{ height: size, width: 'auto' }}
  />
);

/**
 * Unified AIRA Brand Logo Component
 *
 * variant="mark"       — standalone logo image only
 * variant="horizontal" — [logo] AIRA (no subtitle)
 * variant="wordmark"   — AIRA text + optional subtitle (no image)
 * variant="full"       — [logo] AIRA + subtitle (default)
 */
export const AiraLogo: React.FC<AiraLogoProps> = ({
  variant = 'full',
  size = 'md',
  subtitle,
  showFullSubtitle = false,
  className,
  markClassName,
  textClassName,
  badge: _badge,
}) => {
  const config = sizeMap[size];

  let subText: string | null = null;
  if (showFullSubtitle) {
    subText = FULL_BRAND_NAME;
  } else if (typeof subtitle === 'string') {
    subText = subtitle;
  } else if (subtitle === true) {
    subText = 'INVESTMENT AI';
  } else if (subtitle === undefined && variant === 'full') {
    subText = 'INVESTMENT AI';
  }

  if (variant === 'mark') {
    return (
      <div className={cn('flex items-center justify-center', className)}>
        <AiraBrandMark size={config.h} className={markClassName} />
      </div>
    );
  }

  if (variant === 'wordmark') {
    return (
      <div className={cn('flex flex-col select-none', className)}>
        <span className={cn('font-black tracking-tight text-slate-900 dark:text-white font-display leading-none', config.text, textClassName)}>
          AIRA
        </span>
        {subText && (
          <span className={cn('text-indigo-600 dark:text-indigo-400 font-semibold tracking-widest uppercase mt-0.5', config.sub)}>
            {subText}
          </span>
        )}
      </div>
    );
  }

  if (variant === 'horizontal') {
    return (
      <div className={cn('flex items-center select-none', config.gap, className)}>
        <AiraBrandMark size={config.h} className={markClassName} />
        <span className={cn('font-black tracking-tight text-slate-900 dark:text-white font-display leading-none', config.text, textClassName)}>
          AIRA
        </span>
      </div>
    );
  }

  // Default: 'full' — [logo image] AIRA + subtitle stacked
  return (
    <div className={cn('flex items-center select-none', config.gap, className)}>
      <AiraBrandMark size={config.h} className={markClassName} />
      <div className="flex flex-col min-w-0">
        <span className={cn('font-black tracking-tight text-slate-900 dark:text-white leading-none font-display', config.text, textClassName)}>
          AIRA
        </span>
        {subText && (
          <span
            className={cn('text-indigo-600 dark:text-indigo-400 font-semibold tracking-widest uppercase leading-tight truncate mt-0.5', config.sub)}
            title={FULL_BRAND_NAME}
          >
            {subText}
          </span>
        )}
      </div>
    </div>
  );
};

export default AiraLogo;
