/* eslint-disable no-restricted-globals */
/// <reference no-default-lib="true"/>
/// <reference lib="webworker" />

import { generateRandomId } from "../../lib/utils";
import { invariant } from "outvariant";
import { DeferredPromise } from "@open-draft/deferred-promise";
import { CHANNEL_NAME } from "./constants";
import {
  IPreviewRequestMessage,
  IPreviewResponseMessage,
  IWorkerPongMessage,
  MessageSentToWorker,
} from "./types";

declare const self: ServiceWorkerGlobalScope;

// Export empty type because of the "tsc --isolatedModules" flag.
export type {};

self.addEventListener("install", function () {
  self.skipWaiting();
});

self.addEventListener("activate", async (event) => {
  event.waitUntil(self.clients.claim());
});

interface IResponseData {
  status: number;
  headers: Record<string, string>;
  body: string | Uint8Array;
}

const pendingRequests = new Map<string, DeferredPromise<IResponseData>>();
function initRelayPort(relayPort: MessagePort): void {
  /**
   * @note that "addEventListener" and "onmessage" are not always
   * synonymous in MessageChannel so be careful refactoring this.
   */
  relayPort.onmessage = (event: MessageEvent<MessageSentToWorker>) => {
    const { data } = event;

    switch (data.$type) {
      case "preview/response": {
        const message: IPreviewResponseMessage = data;
        const foundRequest = pendingRequests.get(message.id);

        // No pending request associated with the request ID from the message is a no-op.
        invariant(
          foundRequest,
          'Failed to handle "PREVIEW_RESPONSE_TYPE" message from the relay: unknown request ID "%s"',
          message.id
        );

        pendingRequests.delete(message.id);
        foundRequest.resolve({
          status: message.status,
          headers: message.headers,
          body: message.body,
        });
        break;
      }
    }
  };
}

function createRelayPortPromise(): DeferredPromise<MessagePort> {
  const promise = new DeferredPromise<MessagePort>();
  promise.then((port) => {
    initRelayPort(port);
    return port;
  });
  return promise;
}

// Declare a promise that resolves once the relay sends
// a message with the MessagePort to bind their communication.
let relayPortPromise = createRelayPortPromise();

async function sendToRelay(message: any): Promise<void> {
  const relayPort = await relayPortPromise;
  invariant(
    relayPort,
    "Failed to send message to the relay: relay message port is not defined",
    message
  );
  relayPort.postMessage(message);
}

self.addEventListener("message", async (event) => {
  if (typeof event.data !== "object" || event.data.$channel !== CHANNEL_NAME) {
    return;
  }

  const message = event.data as MessageSentToWorker;
  switch (message.$type) {
    case "worker/init": {
      const nextRelayPort = event.ports[0];

      invariant(
        relayPortPromise.state === "pending",
        "Failed to initialize relay: relay port promise already fulfilled from previous evaluation."
      );

      /**
       * @fixme Looks like upon shell restart, the worker is still running,
       * so this promise is already resolved. Resolving it again with
       * the correct message port does nothing, and it keeps pointing
       * to the previous (incorrect) message port.
       */
      relayPortPromise.resolve(nextRelayPort);
      break;
    }

    case "worker/ping": {
      // We are only interested in clients sending this.
      if (!(event.source instanceof Client)) {
        return;
      }

      const client = await self.clients.get(event.source.id);
      if (client) {
        const pong: IWorkerPongMessage = {
          $channel: CHANNEL_NAME,
          $type: "worker/pong",
        };

        // Send back the pong message to keep the client/worker
        // communication from becoming idle (i.e. terminated).
        client.postMessage(pong);
      }
      break;
    }
  }
});

export function getResponse(request: Request): DeferredPromise<IResponseData> {
  const requestId = generateRandomId();
  const requestPromise = new DeferredPromise<IResponseData>();

  // Add some response timeout so the worker doesn't hang indefinitely,
  // making it hard to know what went wrong.
  const timeout = setTimeout(() => {
    pendingRequests.delete(requestId);
    requestPromise.reject(
      new Error(
        `Failed to handle ${request.method} ${request.url} request: no response received from the BroadcastChannel within timeout. There's likely an issue with the relay/worker communication.`
      )
    );
  }, 20_000);

  const requestMessage: IPreviewRequestMessage = {
    $channel: CHANNEL_NAME,
    $type: "preview/request",
    id: requestId,
    url: request.url,
    method: request.method,
  };

  pendingRequests.set(requestId, requestPromise);

  // The worker delegates request resolution to the relay, which,
  // in turn, forwards these request messages to the main frame.
  sendToRelay(requestMessage);

  return requestPromise.finally(() => clearTimeout(timeout));
}

function rewriteNativePreview(body: string): string {
  const resources = {"https://cdn.tailwindcss.com/3.4.17": "/__csb_vendor/tailwind.3.4.17.js", "https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js": "/__csb_vendor/jszip.3.10.1.js", "https://cdn.jsdelivr.net/npm/docx-preview@0.3.7/dist/docx-preview.min.js": "/__csb_vendor/docx-preview.0.3.7.js"};
  for (const [remote, local] of Object.entries(resources)) body = body.replaceAll(remote, local);
  // The native Office meta CSP must also allow these same-origin, pinned scripts.
  return body.replaceAll("script-src https://cdn.jsdelivr.net 'unsafe-inline'", "script-src 'self' 'unsafe-inline'");
}

self.addEventListener("fetch", (event) => {
  const req = event.request.clone();
  const parsedUrl = new URL(req.url);

  if (parsedUrl.pathname.startsWith("/__csb")) {
    return;
  }

  const handleRequest = async () => {
    const response = await getResponse(req);
    const body = typeof response.body === "string" ? rewriteNativePreview(response.body) : response.body;
    const swResponse = new Response(body, {
      headers: { ...response.headers, "Content-Security-Policy": "default-src 'self' blob: data:; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://cdn.jsdelivr.net https://unpkg.com https://esm.sh; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self' https://cdn.jsdelivr.net https://data.jsdelivr.com https://unpkg.com https://registry.npmjs.org https://esm.sh; worker-src 'self' blob:; frame-src 'self' blob:; frame-ancestors https://librechat.digiconseil.fr https://librechat-preprod.digiconseil.fr; object-src 'none'; base-uri 'self'", "Referrer-Policy": "no-referrer", "X-Content-Type-Options": "nosniff" },
      status: response.status,
    });
    return swResponse;
  };

  return event.respondWith(handleRequest());
});
