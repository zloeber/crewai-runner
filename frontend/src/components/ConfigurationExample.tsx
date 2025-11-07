import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ConnectionMonitor } from "@/components/ConnectionMonitor";
import { ConfigurationMenu } from "@/components/ConfigurationMenu";
import { AuthTokenManager } from "@/components/AuthTokenManager";

/**
 * Example component showing different ways to integrate the configuration components
 */
export function ConfigurationExample() {
  const [authStatus, setAuthStatus] = useState(false);

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Option 1: Use the all-in-one ConfigurationMenu */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Complete Configuration Menu</h2>
        <ConfigurationMenu onAuthChange={setAuthStatus} />
      </section>

      {/* Option 2: Use individual components in tabs */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Tabbed Configuration</h2>
        <Tabs defaultValue="connection" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="connection">Connection</TabsTrigger>
            <TabsTrigger value="auth">Authentication</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>
          
          <TabsContent value="connection" className="space-y-4">
            <ConnectionMonitor />
          </TabsContent>
          
          <TabsContent value="auth" className="space-y-4">
            <AuthTokenManager onAuthChange={setAuthStatus} />
          </TabsContent>
          
          <TabsContent value="settings" className="space-y-4">
            {/* Additional settings components */}
            <div className="text-center p-8 text-muted-foreground">
              Additional settings can go here
            </div>
          </TabsContent>
        </Tabs>
      </section>

      {/* Option 3: Side-by-side layout */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Side-by-Side Layout</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ConnectionMonitor />
          <AuthTokenManager onAuthChange={setAuthStatus} />
        </div>
      </section>

      {/* Current authentication status display */}
      <section className="p-4 bg-muted rounded-lg">
        <p className="text-sm">
          Current Authentication Status: 
          <span className={`ml-2 font-medium ${authStatus ? 'text-green-600' : 'text-red-600'}`}>
            {authStatus ? 'Authenticated' : 'Not Authenticated'}
          </span>
        </p>
      </section>
    </div>
  );
}