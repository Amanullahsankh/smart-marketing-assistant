import { Zap, Bell, ChevronDown, LayoutDashboard, BarChart2, Settings, Users } from 'lucide-react';

interface NavbarProps {
  onLogoClick?: () => void;
}

export default function Navbar({ onLogoClick }: NavbarProps) {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-screen-xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <button
              onClick={onLogoClick}
              className="flex items-center gap-2.5 group"
            >
              <div className="w-8 h-8 bg-blue-700 rounded-lg flex items-center justify-center shadow-sm group-hover:bg-blue-800 transition-colors">
                <Zap className="w-4.5 h-4.5 text-white" size={18} />
              </div>
              <span className="text-gray-900 font-semibold text-[15px] tracking-tight">
                Smart Marketing
              </span>
              <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                AI-Powered
              </span>
            </button>

            <nav className="hidden md:flex items-center gap-1">
              <NavLink icon={<LayoutDashboard size={15} />} label="Dashboard" active />
              <NavLink icon={<Users size={15} />} label="Campaigns" />
              <NavLink icon={<BarChart2 size={15} />} label="Analytics" />
              <NavLink icon={<Settings size={15} />} label="Settings" />
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <button className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <Bell size={18} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full"></span>
            </button>

            <div className="h-5 w-px bg-gray-200"></div>

            <button className="flex items-center gap-2 pl-1 pr-2 py-1 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-xs font-semibold">
                SM
              </div>
              <span className="hidden sm:block text-sm font-medium text-gray-700">Sarah M.</span>
              <ChevronDown size={14} className="text-gray-400" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

interface NavLinkProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
}

function NavLink({ icon, label, active }: NavLinkProps) {
  return (
    <button
      className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        active
          ? 'bg-blue-50 text-blue-700'
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
