import { auth } from "@/auth";
import { errorResponse, withErrorHandling } from "@/server/api-helpers";
import { getJob } from "@/server/jobs";
import { storage } from "@/server/storage";

export const runtime = "nodejs";

const CONTENT_TYPE_BY_EXTENSION: Record<string, string> = {
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  webp: "image/webp",
  pdf: "application/pdf",
};

/**
 * GET /api/jobs/[id]/source — owner-authenticated image/PDF preview.
 * Videos continue to use direct object-storage playback.
 */
export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> },
): Promise<Response> {
  return withErrorHandling(async () => {
    const session = await auth();
    if (!session?.user?.id) {
      return errorResponse("UNAUTHORIZED", "Sign in required");
    }

    const { id } = await context.params;
    const result = await getJob(id, session.user.id);
    if (result.kind === "NOT_FOUND") {
      return errorResponse("NOT_FOUND", "Job not found");
    }
    if (result.kind === "FORBIDDEN") {
      return errorResponse("FORBIDDEN", "You don't have access to this job");
    }

    const detail = result.job;
    const requestedIndex = Number(new URL(request.url).searchParams.get("asset") ?? "0");
    const assets = detail.source?.assets ?? [];
    const hasValidIndex =
      Number.isInteger(requestedIndex) &&
      requestedIndex >= 0 &&
      requestedIndex < assets.length;
    if (requestedIndex !== 0 && !hasValidIndex) {
      return errorResponse("NOT_FOUND", "Source preview not found");
    }
    const asset = hasValidIndex ? assets[requestedIndex] : assets[0];
    const sourceExt = asset
      ? asset.ext
      : detail.source?.ext;
    const contentType =
      sourceExt
        ? CONTENT_TYPE_BY_EXTENSION[sourceExt.toLowerCase()]
        : undefined;
    const key = asset?.key ?? detail.source?.key;
    if (!key || !contentType) {
      return errorResponse("NOT_FOUND", "Source preview not found");
    }
    const body = await storage.stream(key);
    if (!body) {
      return errorResponse("NOT_FOUND", "Source preview not found");
    }
    return new Response(body, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "private, max-age=300",
        "X-Content-Type-Options": "nosniff",
      },
    });
  });
}
