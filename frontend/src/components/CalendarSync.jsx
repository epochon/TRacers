import { useState } from 'react';
import { Calendar, Upload, Check, AlertCircle, Loader2, ArrowRight } from 'lucide-react';
import { Button } from "./ui/button";
import { api } from '../api';

export default function CalendarSync() {
    const [step, setStep] = useState(1); // 1: Auth, 2: Upload, 3: Syncing, 4: Success
    const [authUrl, setAuthUrl] = useState(null);
    const [authCode, setAuthCode] = useState("");
    const [file, setFile] = useState(null);
    const [syncResult, setSyncResult] = useState(null);
    const [error, setError] = useState(null);

    const handleGetAuth = async () => {
        try {
            const redirectUri = window.location.origin + "/auth-callback"; // Using current page or specific callback
            // For simplicity in this demo, we might use a popup or just assume we grab the code from a redirect manually if we don't set up full routing.
            // However, the backend expects a code.
            // A proper flow: Open Google Auth in new window, user approves, gets code.
            // Since implementing a full OAuth callback route in React might be overkill for this single task without changing router config too much,
            // I will implement a "Paste Code" flow or a simplified flow.

            // Actually, standard flow: redirect user to Google. Google redirects back to a page we control.
            // Let's assume we can use the current page or a popup.
            // Let's try the "Open in new tab, paste code" approach if we can't easily add a route, 
            // OR better: use the `auth-url` to redirect the user, and handle the callback.
            // But preserving state is hard with full redirect.

            // Let's fetch the URL first.
            const response = await api.getGoogleAuthUrl(window.location.origin); // We might need a dummy redirect URI if we are just pasting code
            // If we use "urn:ietf:wg:oauth:2.0:oob" (Out of band), Google gives a code involved. 
            // But oob is deprecated.

            // Let's use a popup window approach.
            const width = 600;
            const height = 600;
            const left = window.innerWidth / 2 - width / 2;
            const top = window.innerHeight / 2 - height / 2;

            // Ideally we need the backend to support the redirect URI we send.
            // If the backend `credentials.json` has a specific redirect URI configured, we must match it.
            // Typically `http://localhost:5173` is allowed for dev.

            window.open(response.auth_url, 'Google Auth', `width=${width},height=${height},top=${top},left=${left}`);

            // Prompt user to paste code (if we can't capture it easily from popup without more code)
            // For this hackathon/MVP level, "Paste Code" is robust.
            setStep(1.5);
        } catch (err) {
            setError(err.message || "Failed to get auth URL");
        }
    };

    const handleSync = async () => {
        if (!file) return;

        // In a real app we'd capture the code automatically. 
        // Here let's assume we have a code input or we just need the file if the backend handles auth differently.
        // Wait, the backend endpoint `sync_calendar` NEEDS a code.
        // So we definitely need the auth code.

        // Let's add an input for the code.
        if (!authCode) {
            setError("Please enter the authorization code");
            return;
        }

        setStep(3);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('code', authCode);
            formData.append('redirect_uri', window.location.origin);

            console.log("Sending sync request...");
            const result = await api.syncCalendar(formData);
            console.log("Sync result:", result);
            setSyncResult(result);
            setStep(4);
        } catch (err) {
            console.error("Sync error:", err);
            setError(err.message || "Sync failed");
            setStep(2);
        }
    };

    return (
        <div className="glass-card p-8 animate-fade-in-up">
            {/* ... header ... */}
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
                    <Calendar className="w-6 h-6" />
                </div>
                <div>
                    <h2 className="text-xl font-bold">Academic Calendar Sync</h2>
                    <p className="text-sm text-muted-foreground">Upload your course calendar to sync events to Google Calendar.</p>
                </div>
            </div>

            <div className="max-w-xl mx-auto space-y-8">
                {/* Step Indicators (Unchanged) */}
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className={`flex items-center gap-2 ${step >= 1 ? 'text-primary font-medium' : ''}`}>
                        <span className="w-6 h-6 rounded-full border flex items-center justify-center text-xs">1</span>
                        Connect
                    </div>
                    <div className="h-[1px] bg-white/10 flex-1 mx-4" />
                    <div className={`flex items-center gap-2 ${step >= 2 ? 'text-primary font-medium' : ''}`}>
                        <span className="w-6 h-6 rounded-full border flex items-center justify-center text-xs">2</span>
                        Upload
                    </div>
                    <div className="h-[1px] bg-white/10 flex-1 mx-4" />
                    <div className={`flex items-center gap-2 ${step >= 4 ? 'text-primary font-medium' : ''}`}>
                        <span className="w-6 h-6 rounded-full border flex items-center justify-center text-xs">3</span>
                        Done
                    </div>
                </div>

                {/* Content */}
                <div className="bg-white/5 rounded-xl p-8 border border-white/10">

                    {step === 1 && (
                        <div className="text-center space-y-4">
                            <p className="text-foreground/80">
                                First, we need permission to access your Google Calendar.
                                <br />
                                <span className="text-xs text-muted-foreground">We only add events; we don't delete your existing items.</span>
                            </p>
                            <Button onClick={handleGetAuth} className="w-full sm:w-auto">
                                Authorize with Google
                            </Button>
                        </div>
                    )}

                    {step === 1.5 && (
                        <div className="space-y-4">
                            <p className="text-sm text-muted-foreground">
                                Please authorize the app in the popup window, then copy the code provided (or the code from the URL) and paste it below.
                            </p>
                            <div className="space-y-2">
                                <label className="text-xs font-medium">Authorization Code</label>
                                <input
                                    id="auth-code"
                                    type="text"
                                    value={authCode}
                                    onChange={(e) => setAuthCode(e.target.value)}
                                    className="w-full bg-background/50 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                                    placeholder="Paste code here..."
                                />
                            </div>
                            <Button onClick={() => setStep(2)} className="w-full" disabled={!authCode}>
                                Verify Code & Continue
                            </Button>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-6">
                            <div className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:bg-white/5 transition-colors cursor-pointer relative">
                                <input
                                    type="file"
                                    accept=".pdf,.txt,.ics"
                                    onChange={(e) => setFile(e.target.files[0])}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-4" />
                                {file ? (
                                    <div className="text-primary font-medium flex items-center justify-center gap-2">
                                        {/* Removed File Icon import dependency check by just using generic div or re-verifying imports. 
                                            Wait, 'File' is actually NOT imported in the viewed file snippet! 
                                            The viewed snippet had `import { Calendar, Upload, Check, AlertCircle, Loader2, ArrowRight } from 'lucide-react';`
                                            It used `<File ... />` on line 165 but File was NOT in the imports!
                                            THIS IS THE BUG!
                                            <File /> is undefined. Rendering <undefined /> crashes React.
                                        */}
                                        <div className="w-4 h-4 border rounded bg-white/20" />
                                        {file.name}
                                    </div>
                                ) : (
                                    <>
                                        <p className="font-medium">Drop your calendar file here</p>
                                        <p className="text-xs text-muted-foreground mt-1">PDF, TXT, or ICS</p>
                                    </>
                                )}
                            </div>
                            <Button onClick={handleSync} disabled={!file} className="w-full">
                                Start Sync
                            </Button>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="text-center space-y-4 py-8">
                            <Loader2 className="w-10 h-10 animate-spin text-primary mx-auto" />
                            <p className="animate-pulse">Analyzing document and syncing events...</p>
                        </div>
                    )}

                    {step === 4 && syncResult && (
                        <div className="text-center space-y-6">
                            <div className="w-16 h-16 rounded-full bg-green-500/20 text-green-500 flex items-center justify-center mx-auto">
                                <Check className="w-8 h-8" />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-green-500">Sync Complete!</h3>
                                <p className="text-muted-foreground">
                                    Successfully added {syncResult?.details?.success_count || 0} events to your calendar.
                                </p>
                            </div>

                            {(syncResult?.details?.error_count || 0) > 0 && (
                                <div className="text-xs text-destructive bg-destructive/10 p-2 rounded">
                                    {syncResult?.details?.error_count} events failed to sync.
                                </div>
                            )}

                            {/* Event List */}
                            {syncResult?.details?.created_events_details && syncResult.details.created_events_details.length > 0 && (
                                <div className="bg-white/5 rounded-lg border border-white/10 overflow-hidden text-left mt-4">
                                    <div className="p-3 border-b border-white/10 bg-white/5 font-medium text-xs uppercase tracking-wider text-muted-foreground">
                                        Synced Events
                                    </div>
                                    <div className="max-h-60 overflow-y-auto custom-scrollbar">
                                        {syncResult.details.created_events_details.map((event, i) => (
                                            <div key={i} className="p-3 border-b border-white/5 last:border-0 hover:bg-white/5 transition-colors flex justify-between items-start gap-4">
                                                <div>
                                                    <p className="font-medium text-sm text-foreground">{event.summary}</p>
                                                    <p className="text-xs text-muted-foreground mt-0.5">{event.start}</p>
                                                </div>
                                                {event.link && (
                                                    <a
                                                        href={event.link}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-xs text-primary hover:underline whitespace-nowrap"
                                                    >
                                                        View
                                                    </a>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <Button variant="outline" onClick={() => { setStep(1); setFile(null); setSyncResult(null); }} className="w-full">
                                Sync Another File
                            </Button>
                        </div>
                    )}

                    {error && (
                        <div className="flex items-center gap-2 text-destructive bg-destructive/10 p-3 rounded-lg text-sm">
                            <AlertCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}
