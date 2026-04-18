import { ExternalLink, Sheet } from 'lucide-react';

interface OutputButtonsProps {
  visible: boolean;
  driveUrl?: string;
  sheetUrl?: string;
}

export default function OutputButtons({ visible, driveUrl, sheetUrl }: OutputButtonsProps) {
  return (
    <div
      className={`flex flex-col sm:flex-row items-stretch sm:items-center gap-3 transition-all duration-500 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}
      style={{ transitionDelay: '300ms' }}
    >
      <button onClick={() => window.open(driveUrl ?? 'https://drive.google.com', '_blank')} className="flex items-center justify-center gap-2.5 px-5 py-3 bg-white border-2 border-blue-700 text-blue-700 rounded-xl font-semibold text-sm hover:bg-blue-50 transition-colors shadow-sm">
        <ExternalLink size={16} />
        View Portfolio on Drive
      </button>
      <button onClick={() => window.open(sheetUrl ?? 'https://docs.google.com/spreadsheets/d/16MvwG0MAbRhDNJVB34Dhcc9l45hO7qRnkBJLXYJufYQ', '_blank')} className="flex items-center justify-center gap-2.5 px-5 py-3 bg-blue-700 text-white rounded-xl font-semibold text-sm hover:bg-blue-800 transition-colors shadow-sm shadow-blue-200">
        <Sheet size={16} />
        Open Google Sheet
      </button>
    </div>
  );
}
