const POSTHOG_UPSTREAM = "https://us.i.posthog.com";
const POSTHOG_PREFIX = "/posthog";

// Upstream gateway for API requests. When deploying, override this value
// via a Wrangler environment variable or a Cloudflare secret binding if needed.
// Default uses the CloudFront domain configured in the frontend build.
const GATEWAY_UPSTREAM = "https://d1wkhs3cq8vcom.cloudfront.net";
const API_PREFIX = "/api";

const corsHeaders = (request) => {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
};

const posthogUrl = (requestUrl) => {
  const url = new URL(requestUrl);
  const upstream = new URL(POSTHOG_UPSTREAM);
  upstream.pathname = url.pathname.replace(POSTHOG_PREFIX, "") || "/";
  upstream.search = url.search;
  return upstream.toString();
};

const proxyPostHog = async (request) => {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request) });
  }

  const headers = new Headers(request.headers);
  headers.delete("Host");
  headers.delete("Origin");
  headers.delete("Referer");

  const upstreamResponse = await fetch(posthogUrl(request.url), {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
    redirect: "follow",
  });

  const responseHeaders = new Headers(upstreamResponse.headers);
  Object.entries(corsHeaders(request)).forEach(([key, value]) => {
    responseHeaders.set(key, value);
  });

  return new Response(upstreamResponse.body, {
    status: upstreamResponse.status,
    statusText: upstreamResponse.statusText,
    headers: responseHeaders,
  });
};

const apiUrl = (requestUrl) => {
  const url = new URL(requestUrl);
  const upstream = new URL(GATEWAY_UPSTREAM);
  upstream.pathname = url.pathname;
  upstream.search = url.search;
  return upstream.toString();
};

const proxyApi = async (request) => {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request) });
  }

  const headers = new Headers(request.headers);
  // Remove host-related headers so upstream doesn't misinterpret them
  headers.delete("Host");
  headers.delete("Origin");
  headers.delete("Referer");

  const upstreamResponse = await fetch(apiUrl(request.url), {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
    redirect: "follow",
  });

  const responseHeaders = new Headers(upstreamResponse.headers);
  Object.entries(corsHeaders(request)).forEach(([key, value]) => {
    responseHeaders.set(key, value);
  });

  return new Response(upstreamResponse.body, {
    status: upstreamResponse.status,
    statusText: upstreamResponse.statusText,
    headers: responseHeaders,
  });
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === POSTHOG_PREFIX || url.pathname.startsWith(`${POSTHOG_PREFIX}/`)) {
      return proxyPostHog(request);
    }
    if (url.pathname === API_PREFIX || url.pathname.startsWith(`${API_PREFIX}/`)) {
      return proxyApi(request);
    }
    return new Response("Not found", { status: 404 });
  },
};
