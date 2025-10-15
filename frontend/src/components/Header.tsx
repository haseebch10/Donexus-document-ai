import donexusLogo from '@/assets/donexus.png';

export function Header() {
  return (
    <header className="border-b bg-background">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <img 
              src={donexusLogo} 
              alt="DoNexus" 
              className="h-10 w-auto"
            />
            <div>
              <p className="text-sm text-muted-foreground">Document AI</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">German Lease Extraction</p>
            <p className="text-xs text-muted-foreground">Powered by AI</p>
          </div>
        </div>
      </div>
    </header>
  );
}
