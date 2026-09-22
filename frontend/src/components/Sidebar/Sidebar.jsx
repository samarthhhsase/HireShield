import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  Shield, 
  LayoutDashboard, 
  Briefcase, 
  SearchCode, 
  FileText, 
  Activity, 
  Settings, 
  User, 
  LogOut, 
  ChevronRight 
} from 'lucide-react';
import { getStoredUser, logoutUser } from '../../api/auth';

export default function Sidebar({ mobileOpen = false, setMobileOpen = () => {} }) {
  const navigate = useNavigate();
  const rawUser = getStoredUser();
  const user = rawUser || { full_name: 'Lead Security Analyst', role: 'SecOps Analyst' };
  const displayName = user.full_name || user.name || user.email || 'Analyst';

  const handleLogout = () => {
    logoutUser();
    navigate('/login', { replace: true });
  };

  const navItems = [
    { to: '/dashboard', label: 'Overview', icon: LayoutDashboard },
    { to: '/jobs', label: 'Jobs', icon: Briefcase },
    { to: '/risk-analysis', label: 'Risk Analysis', icon: SearchCode, highlight: true },
    { to: '/reports', label: 'Reports', icon: FileText },
    { to: '/activity', label: 'Activity', icon: Activity },
  ];

  const bottomItems = [
    { to: '/settings', label: 'Settings', icon: Settings },
    { to: '/profile', label: 'Profile', icon: User },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-surface-200 border-r border-surface-border flex flex-col justify-between transition-transform duration-300 ${
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}>
        {/* Top: Logo & Platform Identity */}
        <div>
          <div className="p-5 border-b border-surface-border flex items-center justify-between">
            <NavLink to="/" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-surface-100 border border-brand-primary/40 flex items-center justify-center text-brand-primary shadow-cyber">
                <Shield className="w-4 h-4 fill-brand-primary/20 stroke-brand-primary" />
              </div>
              <div>
                <span className="font-sans font-bold text-sm text-white tracking-tight">HireShield</span>
                <span className="block font-mono text-[9px] text-brand-light tracking-wider uppercase">Risk Platform</span>
              </div>
            </NavLink>
          </div>

          {/* Primary Navigation Links */}
          <nav className="p-3 space-y-1 font-mono text-xs">
            <div className="px-3 py-2 text-[10px] tracking-wider text-text-muted uppercase">
              Intelligence Hub
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) => `flex items-center justify-between px-3 py-2.5 rounded-lg transition-all ${
                    isActive
                      ? 'bg-brand-primary/15 text-brand-light border border-brand-primary/30 font-semibold shadow-cyber'
                      : 'text-text-secondary hover:text-white hover:bg-surface-100 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.highlight && (
                    <span className="w-1.5 h-1.5 rounded-full bg-brand-light animate-ping" />
                  )}
                </NavLink>
              );
            })}

            <div className="pt-4 px-3 py-2 text-[10px] tracking-wider text-text-muted uppercase border-t border-surface-border/60">
              System & Workspace
            </div>
            {bottomItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) => `flex items-center gap-2.5 px-3 py-2 rounded-lg transition-all ${
                    isActive
                      ? 'bg-brand-primary/15 text-brand-light border border-brand-primary/30 font-semibold'
                      : 'text-text-secondary hover:text-white hover:bg-surface-100 border border-transparent'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Bottom: User profile */}
        <div className="p-4 border-t border-surface-border font-mono">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-7 h-7 rounded-full bg-surface-100 border border-surface-border flex items-center justify-center text-brand-light text-[11px] font-bold">
                {displayName.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0 truncate">
                <div className="text-xs font-semibold text-text-primary truncate">{displayName}</div>
                <div className="text-[10px] text-text-muted truncate">{user.organization || user.role || 'SecOps'}</div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="p-1.5 text-text-muted hover:text-risk-critical transition-colors rounded hover:bg-surface-100"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
