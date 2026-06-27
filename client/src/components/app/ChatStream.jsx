import { Bot } from 'lucide-react';

export default function ChatStream({ content }) {
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-bg-tertiary text-text-secondary">
        <Bot size={16} />
      </div>
      <div className="max-w-[80%] px-4 py-3 rounded-2xl rounded-tl-md bg-bg-secondary border border-border text-text-primary text-sm whitespace-pre-wrap">
        {content}<span className="inline-block w-1.5 h-4 bg-primary animate-pulse ml-0.5 align-middle" />
      </div>
    </div>
  );
}