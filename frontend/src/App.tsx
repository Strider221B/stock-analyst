import { Button } from "@/components/ui/button"

function App() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 p-4">
      <div className="space-y-6 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-50">
          Frontend Foundation Active
        </h1>
        <p className="text-zinc-400">
          Tailwind v4, path aliases, and UI components are fully compiled.
        </p>

        {/* The shadcn/ui component in action */}
        <Button variant="default" size="lg">
          Analyze Portfolio
        </Button>
      </div>
    </div>
  )
}

export default App
