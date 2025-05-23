import { useState } from "react";
import type { ReactNode } from "react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Menu, Home, User, Receipt, Package, HelpCircle, Github, ExternalLink } from "lucide-react";

interface DashboardLayoutProps {
  children: ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

interface NavItem {
  id: string;
  label: string;
  icon: ReactNode;
}

export function DashboardLayout({ children, activeTab, onTabChange }: DashboardLayoutProps) {
  const [sheetOpen, setSheetOpen] = useState(false);

  const navItems: NavItem[] = [
    { id: "dashboard", label: "Dashboard", icon: <Home className="h-4 w-4" /> },
    { id: "usage", label: "Data Usage", icon: <Package className="h-4 w-4" /> },
    { id: "profile", label: "Profile", icon: <User className="h-4 w-4" /> },
    { id: "bill", label: "Bills", icon: <Receipt className="h-4 w-4" /> },
    { id: "vas", label: "VAS Bundles", icon: <Package className="h-4 w-4" /> },
  ];

  const handleNavigation = (id: string) => {
    onTabChange(id);
    setSheetOpen(false);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-30">
        <div className="container flex items-center justify-between h-16 px-4">
          <div className="flex items-center gap-2">
            <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
              <SheetTrigger asChild className="lg:hidden">
                <Button variant="outline" size="icon">
                  <Menu className="h-5 w-5" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-[240px] sm:w-[300px]">
                <div className="py-6">
                  <h2 className="text-lg font-bold mb-6">MySLT Dashboard</h2>
                  <nav className="space-y-1">
                    {navItems.map((item) => (
                      <Button
                        key={item.id}
                        variant={activeTab === item.id ? "secondary" : "ghost"}
                        className="w-full justify-start gap-3"
                        onClick={() => handleNavigation(item.id)}
                      >
                        {item.icon}
                        {item.label}
                      </Button>
                    ))}
                  </nav>
                </div>
              </SheetContent>
            </Sheet>
            <h1 className="text-xl font-bold">MySLT Dashboard</h1>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1">
        {/* Sidebar (desktop only) */}
        <aside className="hidden lg:flex w-[240px] flex-col border-r bg-card py-6 px-4">
          <nav className="space-y-1">
            {navItems.map((item) => (
              <Button
                key={item.id}
                variant={activeTab === item.id ? "secondary" : "ghost"}
                className="w-full justify-start gap-3"
                onClick={() => handleNavigation(item.id)}
              >
                {item.icon}
                {item.label}
              </Button>
            ))}
          </nav>
          <div className="flex-1"></div>
          <div className="border-t pt-4 mt-4">
            <Button variant="ghost" className="w-full justify-start gap-3" asChild>
              <a href="https://github.com/HimashaHerath/MySLT_Bot" target="_blank" rel="noopener noreferrer">
                <Github className="h-4 w-4" />
                GitHub
              </a>
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-3" asChild>
              <a href="https://myslt.slt.lk/" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4" />
                SLT Website
              </a>
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-3" asChild>
              <a href="https://github.com/HimashaHerath/MySLT_Bot/issues" target="_blank" rel="noopener noreferrer">
                <HelpCircle className="h-4 w-4" />
                Help & Support
              </a>
            </Button>
          </div>
        </aside>

        {/* Main content area */}
        <main className="flex-1 py-6 px-4 md:px-6 max-w-6xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  );
} 