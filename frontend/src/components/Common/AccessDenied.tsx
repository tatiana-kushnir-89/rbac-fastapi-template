import { ShieldX } from "lucide-react"
import { Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

export function AccessDenied() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <ShieldX className="h-16 w-16 text-destructive" />
      <h1 className="text-2xl font-bold">Access Denied</h1>
      <p className="text-muted-foreground text-center max-w-md">
        You don't have permission to access this page. Please contact your
        administrator if you believe this is an error.
      </p>
      <Button asChild>
        <Link to="/">Return to Dashboard</Link>
      </Button>
    </div>
  )
}

export default AccessDenied