import { useState, useEffect } from "react";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { crewAIApi } from "@/services/crewai-api";

interface FrameworkSelectorProps {
  value: string;
  onChange: (framework: string) => void;
}

export function FrameworkSelector({ value, onChange }: FrameworkSelectorProps) {
  const [frameworks, setFrameworks] = useState<string[]>(["crewai"]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFrameworks = async () => {
      try {
        const response = await crewAIApi.getSupportedFrameworks();
        setFrameworks(response.frameworks);
      } catch (error) {
        console.error("Failed to load frameworks:", error);
      } finally {
        setLoading(false);
      }
    };

    loadFrameworks();
  }, []);

  return (
    <div className="space-y-2">
      <Label htmlFor="framework-select">Framework</Label>
      <Select value={value} onValueChange={onChange} disabled={loading}>
        <SelectTrigger id="framework-select" className="w-full">
          <SelectValue placeholder={loading ? "Loading..." : "Select framework"} />
        </SelectTrigger>
        <SelectContent>
          {frameworks.map((framework) => (
            <SelectItem key={framework} value={framework}>
              {framework.toUpperCase()}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <p className="text-sm text-muted-foreground">
        Choose the AI agent framework to use for workflow execution
      </p>
    </div>
  );
}
