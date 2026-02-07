import { useState } from 'react';
import { Building2, Send, Shield, Info, CheckCircle2, MessageSquare } from 'lucide-react';
import { Button } from './ui/button';

export default function GovConnectLanding() {
    const [submitted, setSubmitted] = useState(false);
    const [category, setCategory] = useState('');
    const [grievance, setGrievance] = useState('');

    const categories = [
        'Scholarship & Financial Aid',
        'Hostel Allotment & Infrastructure',
        'Examination & Fee Issues',
        'Administrative Process Delay',
        'Course/Academic Grievance'
    ];

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!category || !grievance) return;
        setSubmitted(true);
    };

    if (submitted) {
        return (
            <div className="flex flex-col items-center justify-center h-full p-12 text-center bg-emerald-50/30">
                <div className="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center mb-6 border-4 border-white shadow-sm">
                    <CheckCircle2 className="w-10 h-10 text-emerald-600" />
                </div>
                <h3 className="text-3xl font-bold text-emerald-900 mb-4">Grievance Registered</h3>
                <p className="text-emerald-800/80 mb-8 max-w-md text-lg leading-relaxed">
                    Your direct connection to the institutional authorities has been established.
                    A case officer will review your friction markers and respond within 24-48 hours.
                </p>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 max-w-sm w-full text-left">
                    <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest mb-3">Next Steps</p>
                    <ul className="space-y-3 text-sm text-emerald-800/70">
                        <li className="flex gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5" /> Case tracking ID generated</li>
                        <li className="flex gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5" /> Department assignment (In Progress)</li>
                        <li className="flex gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5" /> Direct resolution protocol activated</li>
                    </ul>
                </div>
                <Button onClick={() => setSubmitted(false)} variant="outline" className="mt-10 border-emerald-200 text-emerald-700 hover:bg-emerald-50 px-8 py-6 rounded-2xl">
                    Log Another Grievance
                </Button>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-white">
            <div className="border-b border-border p-8">
                <div className="flex items-center gap-5">
                    <div className="w-16 h-16 rounded-3xl bg-black flex items-center justify-center shadow-lg">
                        <Building2 className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold flex items-center gap-2">
                            GovConnect <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 uppercase tracking-wider">Direct Authority Channel</span>
                        </h2>
                        <p className="text-muted-foreground">Direct-line to institutional leadership for resolving high-friction administrative barriers.</p>
                    </div>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-10 bg-gray-50/50">
                <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10">
                    <div className="space-y-8">
                        <div className="space-y-4">
                            <h3 className="text-xl font-bold">Institutional Transparency Commitment</h3>
                            <p className="text-muted-foreground leading-relaxed">
                                GovConnect bypasses traditional clerical layers to put students in direct contact with department heads.
                                This channel is strictly for resolving **administrative friction** identified by your TRACERS trajectory.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="p-5 rounded-2xl bg-white border border-border flex flex-col items-center text-center">
                                <Shield className="w-8 h-8 text-blue-500 mb-3" />
                                <h4 className="font-bold text-sm">Protected Claims</h4>
                                <p className="text-xs text-muted-foreground mt-1">Legally backed grievance protection.</p>
                            </div>
                            <div className="p-5 rounded-2xl bg-white border border-border flex flex-col items-center text-center">
                                <Info className="w-8 h-8 text-amber-500 mb-3" />
                                <h4 className="font-bold text-sm">Direct Review</h4>
                                <p className="text-xs text-muted-foreground mt-1">No intermediary clerical filtering.</p>
                            </div>
                        </div>

                        <div className="p-5 rounded-2xl bg-black text-white">
                            <div className="flex gap-3 items-start">
                                <MessageSquare className="w-5 h-5 mt-1 shrink-0" />
                                <div>
                                    <h4 className="font-bold mb-1">Active Monitoring</h4>
                                    <p className="text-xs opacity-70 leading-relaxed">
                                        This session is monitored for institutional accountability.
                                        Authorities are required to respond within the mandated service-level agreement (SLA).
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="glass-card p-8 shadow-xl bg-white">
                        <h3 className="text-xl font-bold mb-6">Lodge Administrative Grievance</h3>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Department Category</label>
                                <select
                                    value={category}
                                    onChange={(e) => setCategory(e.target.value)}
                                    className="w-full p-4 rounded-xl bg-gray-50 border border-border focus:ring-2 focus:ring-black outline-none transition-all"
                                    required
                                >
                                    <option value="">Select Department</option>
                                    {categories.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Detailed Description of Friction</label>
                                <textarea
                                    value={grievance}
                                    onChange={(e) => setGrievance(e.target.value)}
                                    placeholder="Describe the administrative barrier you are facing... (e.g. Scholarship pending since July, no response from finance office)"
                                    className="w-full min-h-[150px] p-4 rounded-xl bg-gray-50 border border-border focus:ring-2 focus:ring-black outline-none transition-all resize-none"
                                    required
                                />
                            </div>

                            <div className="p-4 rounded-xl bg-blue-50 border border-blue-100 flex gap-3">
                                <Info className="w-5 h-5 text-blue-600 shrink-0" />
                                <p className="text-xs text-blue-800 leading-normal">
                                    Attaching your friction markers automatically helps the authority understand the systemic nature of your issue.
                                </p>
                            </div>

                            <Button type="submit" className="w-full py-7 rounded-2xl text-lg font-bold shadow-lg">
                                Send Direct Grievance <Send className="w-5 h-5 ml-2" />
                            </Button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
