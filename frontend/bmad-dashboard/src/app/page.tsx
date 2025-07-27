import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-foreground mb-8">
          BMAD Dashboard
        </h1>
        
        <div className="space-y-6">
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Shadcn/ui Test</h2>
            <div className="flex gap-4 flex-wrap">
              <Button>Default Button</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="link">Link</Button>
            </div>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Button Sizes</h2>
            <div className="flex gap-4 items-center flex-wrap">
              <Button size="sm">Small</Button>
              <Button size="default">Default</Button>
              <Button size="lg">Large</Button>
            </div>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Agent Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 border rounded-lg">
                <h3 className="font-semibold">FrontendDeveloper</h3>
                <p className="text-sm text-muted-foreground">Status: Online</p>
                <Button size="sm" className="mt-2">View Details</Button>
              </div>
              <div className="p-4 border rounded-lg">
                <h3 className="font-semibold">BackendDeveloper</h3>
                <p className="text-sm text-muted-foreground">Status: Online</p>
                <Button size="sm" className="mt-2">View Details</Button>
              </div>
              <div className="p-4 border rounded-lg">
                <h3 className="font-semibold">TestEngineer</h3>
                <p className="text-sm text-muted-foreground">Status: Online</p>
                <Button size="sm" className="mt-2">View Details</Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
