import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2 } from 'lucide-react';
import { Button } from './ui/Button';
import { chatWithBot } from '../api';
import { cn } from '../utils';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: string[];
}

export const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: "Hello! I'm your AI financial analyst. Ask me anything about the uploaded documents." }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await chatWithBot(userMsg.content);
            const botMsg: Message = {
                role: 'assistant',
                content: response.answer,
                sources: response.sources
            };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error answering that." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[600px] w-full bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex items-center">
                <Bot className="w-5 h-5 text-accent mr-2" />
                <h3 className="font-semibold text-gray-800">Financial Analyst Assistant</h3>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div key={idx} className={cn("flex", msg.role === 'user' ? "justify-end" : "justify-start")}>
                        <div className={cn(
                            "max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed",
                            msg.role === 'user'
                                ? "bg-primary text-white"
                                : "bg-gray-100 text-gray-800"
                        )}>
                            <p>{msg.content}</p>
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-gray-200/50 text-xs opacity-70">
                                    <p className="font-semibold mb-1">Sources:</p>
                                    <ul className="list-disc pl-4">
                                        {msg.sources.map((s, i) => (
                                            <li key={i}>{s}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-2xl p-4 flex items-center space-x-2">
                            <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
                            <span className="text-sm text-gray-500">Thinking...</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-100 bg-white">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about revenue, risks, or specific figures..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent"
                    />
                    <Button onClick={handleSend} disabled={loading || !input.trim()}>
                        <Send className="w-4 h-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
};
