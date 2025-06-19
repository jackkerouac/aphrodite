'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { useConnectionTesting } from './hooks';

export function ConnectionCheck() {
  const { services, isTestingAll, testConnection, testAllConnections } = useConnectionTesting();

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Connection Check</CardTitle>
        <CardDescription>
          Test connectivity to all configured external services and APIs.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {services.map((service) => (
            <Card key={service.name} className="bg-muted/50">
              <CardContent className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-medium">{service.name}</h3>
                  <div className="flex items-center gap-2">
                    {service.status === 'checking' && (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                    {service.status && service.status !== 'checking' && (
                      <Badge variant={service.status === 'connected' ? "default" : "destructive"}>
                        {service.status === 'connected' && <CheckCircle className="h-3 w-3 mr-1" />}
                        {service.status === 'failed' && <XCircle className="h-3 w-3 mr-1" />}
                        {service.status === 'connected' ? 'Connected' : 'Failed'}
                      </Badge>
                    )}
                    {!service.status && (
                      <Badge variant="outline">Not tested</Badge>
                    )}
                  </div>
                </div>
                
                <p className="text-sm text-muted-foreground mb-3">
                  {service.description}
                </p>
                
                {service.error && (
                  <p className="text-sm text-destructive mb-3">
                    {service.error}
                  </p>
                )}
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => testConnection(service.name)}
                  disabled={service.status === 'checking' || isTestingAll}
                  className="w-full"
                >
                  {service.status === 'checking' ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Testing...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Test Connection
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Test All Button */}
        <div className="flex justify-center pt-4 border-t">
          <Button 
            onClick={testAllConnections}
            disabled={isTestingAll}
            size="lg"
            className="min-w-48"
          >
            {isTestingAll ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin mr-2" />
                Testing All Connections...
              </>
            ) : (
              <>
                <RefreshCw className="h-5 w-5 mr-2" />
                Test All Connections
              </>
            )}
          </Button>
        </div>

        {/* Results Summary */}
        {services.some(s => s.status && s.status !== 'checking') && (
          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="font-medium mb-2">Connection Test Results</h4>
            <div className="flex flex-wrap gap-2">
              {services
                .filter(s => s.status && s.status !== 'checking')
                .map(service => (
                  <Badge 
                    key={service.name} 
                    variant={service.status === 'connected' ? "default" : "destructive"}
                    className="flex items-center gap-1"
                  >
                    {service.status === 'connected' ? (
                      <CheckCircle className="h-3 w-3" />
                    ) : (
                      <XCircle className="h-3 w-3" />
                    )}
                    {service.name}
                  </Badge>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
