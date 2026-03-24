import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, Send, X, Bot, User, Sparkles, Minimize2 } from 'lucide-react';
import { chatWithData } from '../services/api';

const SUGGESTED_QUESTIONS = [
    "What's my biggest financial risk?",
    "How much cash runway do I have?",
    "Which government scheme should I apply for?",
    "Will I survive another COVID lockdown?",
    "What does my 6-month forecast look like?",
    "How can I improve my health score?",
];

export default function ChatPanel({ result, activePage = 'dashboard' }) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "Hi! I'm FinTwin AI 🤖 — your MSME financial advisor. Ask me anything about your analysis, and I'll give you data-driven answers.",
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (question) => {
        const q = question || input.trim();
        if (!q || loading) return;

        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: q }]);
        setLoading(true);

        try {
            const context = result ? {
                metrics: result.metrics,
                health: result.health,
                simulations: result.simulations,
                forecast: result.forecast,
                backtest: result.backtest,
                schemes: result.schemes,
            } : {};

            const res = await chatWithData(q, context, activePage);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: res.answer,
                provider: res.llm_provider,
            }]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Sorry, I couldn't process that question. Please try again.",
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <>
            {/* Floating chat button */}
            <AnimatePresence>
                {!isOpen && (
                    <motion.button
                        className="chat-fab"
                        onClick={() => setIsOpen(true)}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        title="Chat with FinTwin AI"
                    >
                        <MessageCircle size={22} />
                        <Sparkles size={10} style={{ position: 'absolute', top: 6, right: 6 }} />
                    </motion.button>
                )}
            </AnimatePresence>

            {/* Chat panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        className="chat-panel"
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ type: 'spring', damping: 25 }}
                    >
                        {/* Header */}
                        <div className="chat-header">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Bot size={18} />
                                <div>
                                    <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>FinTwin AI</div>
                                    <div style={{ fontSize: '0.65rem', opacity: 0.7 }}>
                                        {result?.llm_provider === 'mock' ? 'Smart Fallback' : result?.llm_provider === 'openai' ? 'GPT-4o' : result?.llm_provider === 'gemini' ? 'Gemini 2.0' : 'Ready'}
                                    </div>
                                </div>
                            </div>
                            <button className="chat-close" onClick={() => setIsOpen(false)}>
                                <Minimize2 size={16} />
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="chat-messages">
                            {messages.map((msg, i) => (
                                <div key={i} className={`chat-msg ${msg.role}`}>
                                    <div className="chat-msg-icon">
                                        {msg.role === 'assistant' ? <Bot size={14} /> : <User size={14} />}
                                    </div>
                                    <div className="chat-msg-content">
                                        {msg.content}
                                        {msg.provider && msg.provider !== 'mock' && (
                                            <span className="chat-provider" title={`Powered by ${msg.provider}`}>
                                                <Sparkles size={9} /> {msg.provider}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="chat-msg assistant">
                                    <div className="chat-msg-icon"><Bot size={14} /></div>
                                    <div className="chat-msg-content chat-typing">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Suggestions */}
                        {messages.length <= 1 && (
                            <div className="chat-suggestions">
                                {SUGGESTED_QUESTIONS.map((q, i) => (
                                    <button key={i} className="chat-suggestion" onClick={() => handleSend(q)}>
                                        {q}
                                    </button>
                                ))}
                            </div>
                        )}

                        {/* Input */}
                        <div className="chat-input-area">
                            <input
                                className="chat-input"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask about your finances..."
                                disabled={loading}
                            />
                            <button
                                className="chat-send"
                                onClick={() => handleSend()}
                                disabled={!input.trim() || loading}
                            >
                                <Send size={16} />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
