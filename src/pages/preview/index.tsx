import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

/**
 * Index redirect for preview directory
 * Routes users to the new unified badge preview page
 */
export default function PreviewIndexRedirect() {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to the unified badge preview page
    navigate("/preview/unified", { replace: true });
  }, [navigate]);

  return (
    <div className="container mx-auto py-12 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Redirecting...</h1>
        <p className="text-muted-foreground">
          Taking you to the badge preview system.
        </p>
        <p className="mt-4">
          If you are not redirected automatically, please{" "}
          <a href="/preview/unified" className="text-primary hover:underline">
            click here
          </a>
          .
        </p>
      </div>
    </div>
  );
}
