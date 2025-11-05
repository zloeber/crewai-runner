"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { MadeWithDyad } from "@/components/made-with-dyad";
import { MessageCircle, Settings, Play, Square, Upload } from "lucide-react";
import { ChatInterface } from "@/components/ChatInterface";
import { ProviderConfig } from "@/components/ProviderConfig";
import { crewAIApi } from "@/services/crewai-api";
import { useToast } from "@/hooks/use-toast";
import { StartWorkflowResponse, ValidateYamlResponse } from "@/types/crewai-api";

export default function Index() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("chat");
  const [isRunning, setIsRunning] = useState(false);
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [yamlContent, setYamlContent] = useState(`name: ResearchCrew
agents:
  - name: researcher
    role: Senior Research Analyst
    goal: Uncover cutting-edge developments in AI and data science
    backstory: You work at a leading tech think tank...
    
  - name: writer
    role: Tech Content Strategist
    goal: Craft compelling content on tech advancements
    backstory: You are a renowned Content Strategist...

tasks:
  - name: research_task
    description: Investigate the latest AI trends...
    expected_output: A comprehensive 3 paragraphs report...
    agent: researcher

  - name: writing_task
    description: Write a compelling article...
    expected_output: A 3 paragraph article...
    agent: writer`);

  const handleStartWorkflow = async () => {
    if (isRunning) {
      // Stop workflow
      if (workflowId) {
        try {
          await crewAIApi.stopWorkflow({ workflowId });
          setIsRunning(false);
          setWorkflowId(null);
          toast({
            title: "Success",
            description: "Workflow stopped successfully",
          });
        } catch (error) {
          toast({
            title: "Error",
            description: "Failed to stop workflow",
            variant: "destructive",
          });
        }
      }
      return;
    }

    // Start workflow
    try {
      // First validate YAML
      const validationResponse: ValidateYamlResponse = await crewAIApi.validateYaml({ 
        yamlContent 
      });
      
      if (!validationResponse.valid) {
        toast({
          title: "Validation Error",
          description: validationResponse.errors?.join(", ") || "Invalid YAML content",
          variant: "destructive",
        });
        return;
      }

      // Start workflow
      const response: StartWorkflowResponse = await crewAIApi.startWorkflow({
        workflow: validationResponse.workflow!,
      });
      
      setWorkflowId(response.workflowId);
      setIsRunning(true);
      
      toast({
        title: "Success",
        description: "Workflow started successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start workflow",
        variant: "destructive",
      });
    }
  };

  const handleValidateYaml = async () => {
    try {
      const response = await crewAIApi.validateYaml({ yamlContent });
      
      if (response.valid) {
        toast({
          title: "Validation Success",
          description: "YAML is valid",
        });
      } else {
        toast({
          title: "Validation Error",
          description: response.errors?.join(", ") || "Invalid YAML",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to validate YAML",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">CrewAI Workflow Interface</h1>
          <p className="text-lg text-gray-600">
            Configure and interact with your CrewAI agent workflows
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Configuration
                </CardTitle>
                <CardDescription>
                  Set up your default provider and custom endpoints
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ProviderConfig />
              </CardContent>
            </Card>

            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Workflow Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Button 
                    className="flex-1" 
                    onClick={handleStartWorkflow}
                    variant={isRunning ? "destructive" : "default"}
                  >
                    {isRunning ? (
                      <>
                        <Square className="mr-2 h-4 w-4" />
                        Stop Workflow
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Start Workflow
                      </>
                    )}
                  </Button>
                </div>
                
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={handleValidateYaml}
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Validate YAML
                  </Button>
                </div>
                
                <Separator />
                
                <div>
                  <h3 className="font-medium mb-2">Current Workflow</h3>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">ResearchAgent</Badge>
                    <Badge variant="secondary">WriterAgent</Badge>
                    <Badge variant="secondary">EditorAgent</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="chat" className="flex items-center gap-2">
                  <MessageCircle className="h-4 w-4" />
                  Chat Interface
                </TabsTrigger>
                <TabsTrigger value="yaml" className="flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  YAML Definition
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="chat" className="mt-0">
                <Card>
                  <CardHeader>
                    <CardTitle>Agent Chat</CardTitle>
                    <CardDescription>
                      Interact with your CrewAI agents in real-time
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ChatInterface isRunning={isRunning} workflowId={workflowId || undefined} />
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="yaml" className="mt-0">
                <Card>
                  <CardHeader>
                    <CardTitle>YAML Workflow Definition</CardTitle>
                    <CardDescription>
                      Define your agent workflows using YAML
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="yaml-input">YAML Configuration</Label>
                        <Textarea
                          id="yaml-input"
                          placeholder="Enter your YAML workflow definition here..."
                          className="min-h-[400px] font-mono text-sm"
                          value={yamlContent}
                          onChange={(e) => setYamlContent(e.target.value)}
                        />
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" onClick={handleValidateYaml}>
                          Validate
                        </Button>
                        <Button onClick={handleStartWorkflow}>
                          Apply & Start
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
      <MadeWithDyad />
    </div>
  );
}