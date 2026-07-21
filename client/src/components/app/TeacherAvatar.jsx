import { useEffect, useState } from 'react';

export default function TeacherAvatar({ speaking = false, emotion = 'idle' }) {
  const [blink, setBlink] = useState(false);

  useEffect(() => {
    if (!speaking) {
      const interval = setInterval(() => {
        setBlink(true);
        setTimeout(() => setBlink(false), 150);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [speaking]);

  const mouthD = speaking
    ? 'M14 28 Q18 32 22 28'  // open
    : 'M15 28 Q18 29 21 28'; // closed

  const eyeStyle = blink ? 'scale-y-[0.1]' : 'scale-y-100';

  return (
    <div className="flex flex-col items-center justify-end h-full pb-8">
      <svg viewBox="0 0 36 60" className="w-full max-w-[180px] h-auto">
        {/* Head */}
        <ellipse cx="18" cy="12" rx="7" ry="8" className="fill-[#f4c29a]" />
        
        {/* Hair */}
        <path d="M11 10 Q11 3 18 3 Q25 3 25 10" className="fill-gray-900" />
        <path d="M10 11 Q18 2 26 11 Q24 5 18 5 Q12 5 10 11" className="fill-gray-800" />

        {/* Eyes */}
        <g className={`transition-transform duration-100 ${eyeStyle}`}>
          <ellipse cx="15" cy="11" rx="1.2" ry="1.5" className="fill-gray-900" />
          <ellipse cx="21" cy="11" rx="1.2" ry="1.5" className="fill-gray-900" />
          <circle cx="15.3" cy="10.5" r="0.4" className="fill-white" />
          <circle cx="21.3" cy="10.5" r="0.4" className="fill-white" />
        </g>

        {/* Eyebrows */}
        <path d="M13 9 Q15 8 17 9" className="stroke-gray-900" strokeWidth="0.5" fill="none" />
        <path d="M19 9 Q21 8 23 9" className="stroke-gray-900" strokeWidth="0.5" fill="none" />

        {/* Nose */}
        <path d="M17.5 13 Q18 15 18.5 13" className="stroke-gray-600" strokeWidth="0.3" fill="none" />

        {/* Mouth */}
        <path d={mouthD} className="stroke-gray-700" strokeWidth="0.7" fill="none" strokeLinecap="round" />

        {/* Glasses */}
        <rect x="13" y="9.5" width="4.5" height="3" rx="1" className="stroke-gray-700 fill-none" strokeWidth="0.5" />
        <rect x="18.5" y="9.5" width="4.5" height="3" rx="1" className="stroke-gray-700 fill-none" strokeWidth="0.5" />
        <line x1="17.5" y1="11" x2="18.5" y2="11" className="stroke-gray-700" strokeWidth="0.5" />

        {/* Suit Body */}
        <path d="M12 20 L12 45 Q18 50 24 45 L24 20 Z" className="fill-gray-900" />
        
        {/* White Shirt */}
        <path d="M14 20 L14 36 L22 36 L22 20 Z" className="fill-white" />
        
        {/* Tie */}
        <path d="M16 20 L18 32 L20 20 Z" className="fill-blue-600" />
        <path d="M15 20 L18 24 L21 20 Z" className="fill-blue-700" />

        {/* Jacket Lapels */}
        <path d="M14 20 L18 28 L18 20" className="fill-gray-800" />
        <path d="M22 20 L18 28 L18 20" className="fill-gray-800" />

        {/* Arms */}
        <path d="M12 22 Q6 28 8 38 Q9 42 12 40" className="stroke-gray-900 fill-none" strokeWidth="3" strokeLinecap="round" />
        <path d="M24 22 Q30 28 28 38 Q27 42 24 40" className="stroke-gray-900 fill-none" strokeWidth="3" strokeLinecap="round" />

        {/* Hands */}
        <circle cx="9" cy="40" r="1.5" className="fill-[#f4c29a]" />
        <circle cx="27" cy="40" r="1.5" className="fill-[#f4c29a]" />

        {/* Pocket square */}
        <path d="M17 22 L19 22 L19 24 L17 24 Z" className="fill-blue-400" />

        {/* Speaking indicator */}
        {speaking && (
          <>
            <circle cx="18" cy="12" r="10" className="stroke-primary/20" strokeWidth="0.5" fill="none">
              <animate attributeName="r" from="10" to="14" dur="1s" repeatCount="indefinite" />
              <animate attributeName="opacity" from="0.5" to="0" dur="1s" repeatCount="indefinite" />
            </circle>
          </>
        )}
      </svg>
      <p className="text-xs text-text-muted mt-2 font-medium">Mr. HDM</p>
      <p className="text-[10px] text-text-muted">AI Tutor</p>
    </div>
  );
}