import { useState } from 'react';
import { useAuth } from '../auth';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, User, Lock, Mail, Type, Shield, GraduationCap } from 'lucide-react';
import { Button } from "../components/ui/button";

export default function Login() {
  const { login, register } = useAuth();
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    full_name: '',
    role: 'student'
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegistering) {
        await register(formData);
        navigate('/dashboard');
      } else {
        await login(formData.username, formData.password);
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 relative overflow-hidden p-4">
      {/* Back Button */}
      <div className="absolute top-6 left-6 z-20">
        <Link to="/">
          <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-foreground">
            <ArrowLeft className="w-4 h-4" /> Back to Home
          </Button>
        </Link>
      </div>

      <div className="glass-card w-full max-w-md p-10 relative z-10 bg-white">
        {/* Header */}
        <div className="text-center mb-10">
          <Link to="/" className="inline-block mb-6">
            <span className="text-5xl font-bold text-foreground">TRACERS</span>
          </Link>
          <p className="text-muted-foreground text-base">
            Trajectory-Aware Collective System<br />for Student Retention
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl mb-6 text-center font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-foreground ml-1">Username</label>
            <div className="relative">
              <User className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />
              <input
                type="text"
                name="username"
                className="w-full bg-white border-2 border-border rounded-xl pl-12 pr-4 py-3 text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all outline-none font-medium"
                placeholder="Enter your username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-foreground ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />
              <input
                type="password"
                name="password"
                className="w-full bg-white border-2 border-border rounded-xl pl-12 pr-4 py-3 text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all outline-none font-medium"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {isRegistering && (
            <>
              <div className="space-y-2">
                <label className="text-sm font-semibold text-foreground ml-1">Email</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />
                  <input
                    type="email"
                    name="email"
                    className="w-full bg-white border-2 border-border rounded-xl pl-12 pr-4 py-3 text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all outline-none font-medium"
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-foreground ml-1">Full Name</label>
                <div className="relative">
                  <Type className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />
                  <input
                    type="text"
                    name="full_name"
                    className="w-full bg-white border-2 border-border rounded-xl pl-12 pr-4 py-3 text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all outline-none font-medium"
                    placeholder="Enter full name"
                    value={formData.full_name}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-foreground ml-1">Role</label>
                <div className="relative">
                  {formData.role === 'student' && <GraduationCap className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />}
                  {formData.role === 'counselor' && <Shield className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />}
                  {formData.role === 'admin' && <Lock className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />}

                  <select
                    name="role"
                    className="w-full bg-white border-2 border-border rounded-xl pl-12 pr-4 py-3 text-foreground focus:ring-2 focus:ring-primary focus:border-primary transition-all outline-none appearance-none font-medium"
                    value={formData.role}
                    onChange={handleChange}
                    required
                  >
                    <option value="student">Student</option>
                    <option value="counselor">Counselor</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>
            </>
          )}

          <button
            type="submit"
            className="w-full btn-apple-primary text-base mt-8 py-4"
            disabled={loading}
          >
            {loading ? 'Processing...' : (isRegistering ? 'Create Account' : 'Login')}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegistering(!isRegistering);
              setError('');
            }}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors font-medium"
          >
            {isRegistering ? 'Already have an account? Login' : "Don't have an account? Register"}
          </button>
        </div>

        {/* Demo Credentials */}
        {!isRegistering && (
          <div className="mt-10 p-6 rounded-2xl bg-gray-50 border-2 border-border text-sm shadow-sm">
            <p className="font-bold text-black mb-4 flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary" /> Demo Access:
            </p>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-foreground font-semibold">
                <span>Student</span>
                <span className="bg-white px-2 py-1 rounded-md border border-border">student1 / demo123</span>
              </div>
              <div className="flex justify-between items-center text-foreground font-semibold">
                <span>Counselor</span>
                <span className="bg-white px-2 py-1 rounded-md border border-border">counselor1 / demo123</span>
              </div>
              <div className="flex justify-between items-center text-foreground font-semibold">
                <span>Admin</span>
                <span className="bg-white px-2 py-1 rounded-md border border-border">admin1 / demo123</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}