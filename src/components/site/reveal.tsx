'use client';

import { useEffect, useRef, type ReactNode } from 'react';

interface RevealProps {
  children: ReactNode;
  delay?: number; // ms, staggered
  className?: string;
  as?: 'div' | 'section' | 'article' | 'li' | 'span';
}

/**
 * Reveal — fade + slight rise on scroll into view, with safety net.
 *
 * - Uses IntersectionObserver (per the brief).
 * - 2.5s safety net: if observer doesn't fire (or JS hiccups), the element
 *   becomes visible anyway. Prevents content from being permanently hidden.
 * - Honors prefers-reduced-motion via the .reveal CSS rule (content visible).
 */
export function Reveal({ children, delay = 0, className = '', as = 'div' }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    // Safety net — force visible after 2.5s no matter what
    const safetyNet = setTimeout(() => {
      el.classList.add('is-visible');
    }, 2500);

    // If IntersectionObserver is unavailable, just show it
    if (!('IntersectionObserver' in window)) {
      el.classList.add('is-visible');
      clearTimeout(safetyNet);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Apply staggered delay if provided
            if (delay > 0) {
              setTimeout(() => el.classList.add('is-visible'), delay);
            } else {
              el.classList.add('is-visible');
            }
            observer.unobserve(el);
            clearTimeout(safetyNet);
          }
        });
      },
      {
        threshold: 0.12,
        rootMargin: '0px 0px -8% 0px',
      }
    );

    observer.observe(el);

    return () => {
      observer.disconnect();
      clearTimeout(safetyNet);
    };
  }, [delay]);

  const Tag = as as 'div';
  return (
    <Tag ref={ref} className={`reveal ${className}`} style={delay > 0 ? { transitionDelay: `${delay}ms` } : undefined}>
      {children}
    </Tag>
  );
}
