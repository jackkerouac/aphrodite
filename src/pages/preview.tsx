/**
 * This page now redirects to the new, unified badge preview page
 * as part of the Phase 3 badge system refactoring.
 */
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function LegacyPreviewRedirect() {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to the new unified badge preview page
    navigate("/preview/unified", { replace: true });
  }, [navigate]);

  return (
    <div className="container mx-auto py-12 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Redirecting...</h1>
        <p className="text-muted-foreground">
          This page has been replaced by the new unified badge preview system.
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
