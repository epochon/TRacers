import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    ArrowRight,
    Shield,
    Activity,
    Brain,
    Sparkles
} from 'lucide-react';
import { Button } from "../components/ui/button";

const LandingPage = () => {
    const [scrolled, setScrolled] = useState(false);
    const [authCode, setAuthCode] = useState(null);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        if (code) {
            setAuthCode(code);
            return;
        }

        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    if (authCode) {
        return (
            <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 text-center">
                <div className="glass-card p-8 max-w-md w-full space-y-6">
                    <div className="w-16 h-16 rounded-full bg-green-50 text-green-600 flex items-center justify-center mx-auto mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </div>
                    <h2 className="text-3xl font-bold text-foreground">Authorization Successful!</h2>
                    <p className="text-muted-foreground text-base">Copy the code below and paste it back in the Student Portal window to complete the sync.</p>

                    <div className="bg-secondary p-4 rounded-xl border border-border break-all font-mono text-sm text-foreground">
                        {authCode}
                    </div>

                    <Button
                        className="w-full btn-apple-primary"
                        onClick={() => {
                            navigator.clipboard.writeText(authCode);
                            alert("Code copied to clipboard!");
                        }}
                    >
                        Copy Code to Clipboard
                    </Button>
                    <p className="text-xs text-muted-foreground pt-4">You can close this window after copying.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white text-foreground overflow-x-hidden">

            {/* Minimal Navigation */}
            <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-white/95 backdrop-blur-xl border-b border-border' : 'bg-transparent'}`}>
                <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <span className={`text-2xl font-bold tracking-tight ${scrolled ? 'text-foreground' : 'text-white'}`}>TRACERS</span>
                    </div>
                    <div className={`hidden md:flex items-center gap-8 text-sm font-medium ${scrolled ? 'text-muted-foreground' : 'text-white/80'}`}>
                        <a href="#features" className={`hover:text-foreground transition-colors ${!scrolled && 'hover:text-white'}`}>Features</a>
                        <a href="#how-it-works" className={`hover:text-foreground transition-colors ${!scrolled && 'hover:text-white'}`}>How It Works</a>
                        <a href="#ethics" className={`hover:text-foreground transition-colors ${!scrolled && 'hover:text-white'}`}>Ethics</a>
                    </div>
                    <div className="flex items-center gap-4">
                        <Link to="/login">
                            <button className={`${scrolled ? 'btn-apple-primary' : 'bg-white text-black px-6 py-2.5 rounded-xl font-semibold hover:bg-gray-100 transition-all'}`}>
                                Get Started
                            </button>
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section - Solid Black */}
            <section className="relative pt-40 pb-32 min-h-screen flex items-center bg-black overflow-hidden">


                <div className="max-w-6xl mx-auto px-6 w-full relative z-10">
                    <div className="max-w-5xl mx-auto text-center space-y-10">
                        <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-bold tracking-wide">
                            <Sparkles className="w-4 h-4" />
                            Next Generation Student Retention
                        </div>

                        {/* High Contrast Headline - White Text on Black */}
                        <h1
                            className="font-extrabold leading-none tracking-tight text-white font-inter"
                            style={{
                                fontSize: 'clamp(3.5rem, 8vw, 7rem)',
                                letterSpacing: '-0.02em',
                                lineHeight: '1.05'
                            }}
                        >
                            Predict. Protect.<br />
                            Empower.
                        </h1>

                        {/* Secondary Text */}
                        <p
                            className="text-xl md:text-2xl leading-relaxed max-w-3xl mx-auto font-normal text-gray-400"
                        >
                            A trajectory-aware collective multi-agent system designed to identify silent dropout risks caused by bureaucratic friction.
                        </p>

                        {/* Buttons with proper spacing */}
                        <div className="flex flex-col sm:flex-row gap-5 pt-10 justify-center">
                            <Link to="/login">
                                <button
                                    className="text-lg px-10 py-4 bg-white text-black font-semibold rounded-2xl transition-all duration-200 hover:scale-105 hover:shadow-xl"
                                    style={{ letterSpacing: '0.01em' }}
                                >
                                    Launch Dashboard
                                </button>
                            </Link>
                            <button
                                className="text-lg px-10 py-4 bg-transparent border-2 border-white/20 text-white font-semibold rounded-2xl hover:bg-white/5 transition-all duration-200"
                                style={{ letterSpacing: '0.01em' }}
                            >
                                View Documentation
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-32 bg-gray-50">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center max-w-3xl mx-auto mb-20">
                        <h2 className="text-5xl md:text-6xl font-bold mb-6 text-foreground">Core Principles</h2>
                        <p className="text-xl text-muted-foreground leading-relaxed">Built on a foundation of ethical AI and human dignity, TRACERS goes beyond simple metrics.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: <Shield className="w-10 h-10 text-primary" />,
                                title: "Ethical Restraint",
                                desc: "Our agents know when NOT to act. Privacy and consent are baked into the core architecture, not added as an afterthought."
                            },
                            {
                                icon: <Activity className="w-10 h-10 text-primary" />,
                                title: "Friction Detection",
                                desc: "We analyze subtle signals of bureaucratic friction—missed deadlines, form errors, and silence—that often precede dropout."
                            },
                            {
                                icon: <Brain className="w-10 h-10 text-primary" />,
                                title: "Multi-Agent Support",
                                desc: "Specialized agents debate strategies to find the most balanced support path for each student."
                            }
                        ].map((feature, idx) => (
                            <div key={idx} className="glass-card p-10 apple-hover group cursor-default bg-white">
                                <div className="w-16 h-16 rounded-2xl bg-blue-50 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                    {feature.icon}
                                </div>
                                <h3 className="text-2xl font-bold mb-4 text-foreground">{feature.title}</h3>
                                <p className="text-base text-muted-foreground leading-relaxed">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-16 border-t border-border bg-white">
                <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="text-sm text-muted-foreground">
                        © 2026 TRACERS System. All rights reserved.
                    </div>
                    <div className="flex gap-8 text-sm font-medium text-muted-foreground">
                        <a href="#" className="hover:text-foreground transition-colors">Privacy Policy</a>
                        <a href="#" className="hover:text-foreground transition-colors">Terms of Service</a>
                        <a href="#" className="hover:text-foreground transition-colors">Contact Support</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
