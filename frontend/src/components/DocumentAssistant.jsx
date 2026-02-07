import { useState } from 'react';
import { Button } from './ui/button';
import { Send, FileText, Loader2, Copy, Check } from 'lucide-react';
import api from '../api';

export default function DocumentAssistant() {
    const [formData, setFormData] = useState({
        college: '',
        reason: 'medical',
        tone: 'Professional',
        roll_no: '',
        context: '',
        student_name: '',
    });

    const [generatedEmail, setGeneratedEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState('');

    const REASONS = [
        { value: 'medical', label: 'Medical Leave' },
        { value: 'internship', label: 'Internship NOC' },
        { value: 'attendance', label: 'Attendance Condonation' },
        { value: 'general', label: 'General Request' },
    ];

    const TONES = ['Professional', 'Urgent', 'Apologetic', 'Persuasive'];

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setGeneratedEmail('');

        try {
            const user = await api.getCurrentUser();
            const payload = {
                ...formData,
                student_name: formData.student_name || user.full_name || 'Student',
                roll_no: formData.roll_no || 'Not Provided',
            };

            const result = await api.generateDocument(payload);
            setGeneratedEmail(result.email);
        } catch (err) {
            console.error('Error generating document:', err);
            setError('Failed to generate email. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(generatedEmail);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="flex flex-col h-full bg-white rounded-2xl overflow-hidden shadow-2xl border border-gray-100 ring-1 ring-black/5">
            {/* Header */}
            <div className="p-6 border-b border-gray-100 bg-white">
                <h3 className="text-xl font-bold text-black flex items-center gap-2">
                    <FileText className="w-6 h-6 text-black" />
                    Document Assistant
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                    Generate professional academic emails instantly using AI.
                </p>
            </div>

            <div className="flex flex-col lg:flex-row h-full overflow-hidden">
                {/* Form Section */}
                <div className="w-full lg:w-1/2 p-6 overflow-y-auto border-r border-gray-100 bg-gray-50/30 custom-scrollbar">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                                    Reason
                                </label>
                                <select
                                    name="reason"
                                    value={formData.reason}
                                    onChange={handleInputChange}
                                    className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent transition-all"
                                >
                                    {REASONS.map((r) => (
                                        <option key={r.value} value={r.value}>
                                            {r.label}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                                    Tone
                                </label>
                                <select
                                    name="tone"
                                    value={formData.tone}
                                    onChange={handleInputChange}
                                    className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent transition-all"
                                >
                                    {TONES.map((t) => (
                                        <option key={t} value={t}>
                                            {t}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                                Target College / Institution
                            </label>
                            <input
                                type="text"
                                name="college"
                                value={formData.college}
                                onChange={handleInputChange}
                                placeholder="e.g. Stanford University"
                                className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent transition-all"
                                required
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                                    Student Name
                                </label>
                                <input
                                    type="text"
                                    name="student_name"
                                    value={formData.student_name}
                                    onChange={handleInputChange}
                                    placeholder="Your Full Name"
                                    className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent transition-all"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                                    Roll / ID Number
                                </label>
                                <input
                                    type="text"
                                    name="roll_no"
                                    value={formData.roll_no}
                                    onChange={handleInputChange}
                                    placeholder="e.g. 2024CS101"
                                    className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent transition-all"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                                Detailed Context
                            </label>
                            <textarea
                                name="context"
                                value={formData.context}
                                onChange={handleInputChange}
                                placeholder="Provide specific details (e.g., dates of absence, name of illness, company name for internship)..."
                                rows="4"
                                className="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-black focus:border-transparent transition-all resize-none"
                                required
                            />
                        </div>

                        <Button
                            type="submit"
                            disabled={loading}
                            className="w-full py-6 bg-black text-white hover:bg-gray-800 rounded-xl shadow-lg font-bold transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-70"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Generating Draft...
                                </>
                            ) : (
                                <>
                                    Generate Email <Send className="w-4 h-4 ml-2" />
                                </>
                            )}
                        </Button>

                        {error && <p className="text-xs text-red-500 text-center font-medium">{error}</p>}
                    </form>
                </div>

                {/* Output Section */}
                <div className="w-full lg:w-1/2 p-6 flex flex-col bg-white">
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wide">
                            Generated Draft
                        </h4>
                        {generatedEmail && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={copyToClipboard}
                                className="h-8 border-gray-200 hover:bg-gray-50 text-xs"
                            >
                                {copied ? (
                                    <>
                                        <Check className="w-3 h-3 mr-1 text-green-500" /> Copied
                                    </>
                                ) : (
                                    <>
                                        <Copy className="w-3 h-3 mr-1" /> Copy Text
                                    </>
                                )}
                            </Button>
                        )}
                    </div>

                    <div className="flex-1 rounded-xl border border-gray-200 bg-gray-50/50 p-4 overflow-y-auto custom-scrollbar relative">
                        {generatedEmail ? (
                            <pre className="whitespace-pre-wrap font-sans text-sm text-gray-800 leading-relaxed">
                                {generatedEmail}
                            </pre>
                        ) : (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
                                <FileText className="w-12 h-12 mb-3 opacity-20" />
                                <p className="text-sm font-medium">No draft generated yet</p>
                                <p className="text-xs max-w-[200px] text-center mt-1 opacity-60">
                                    Fill out the form and click generate to create your email.
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="mt-4 p-3 bg-blue-50 border border-blue-100 rounded-lg">
                        <p className="text-xs text-blue-700 flex items-start gap-2">
                            <span className="font-bold">Note:</span>
                            This is an AI-generated draft. Please review policies and edit details before sending.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
