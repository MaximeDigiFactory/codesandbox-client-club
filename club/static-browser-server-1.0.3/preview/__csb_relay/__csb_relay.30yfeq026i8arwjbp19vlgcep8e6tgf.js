// node_modules/outvariant/lib/index.mjs
var POSITIONALS_EXP = /(%?)(%([sdijo]))/g;
function serializePositional(positional, flag) {
  switch (flag) {
    case "s":
      return positional;
    case "d":
    case "i":
      return Number(positional);
    case "j":
      return JSON.stringify(positional);
    case "o": {
      if (typeof positional === "string") {
        return positional;
      }
      const json = JSON.stringify(positional);
      if (json === "{}" || json === "[]" || /^\[object .+?\]$/.test(json)) {
        return positional;
      }
      return json;
    }
  }
}
function format(message, ...positionals) {
  if (positionals.length === 0) {
    return message;
  }
  let positionalIndex = 0;
  let formattedMessage = message.replace(
    POSITIONALS_EXP,
    (match, isEscaped, _, flag) => {
      const positional = positionals[positionalIndex];
      const value = serializePositional(positional, flag);
      if (!isEscaped) {
        positionalIndex++;
        return value;
      }
      return match;
    }
  );
  if (positionalIndex < positionals.length) {
    formattedMessage += ` ${positionals.slice(positionalIndex).join(" ")}`;
  }
  formattedMessage = formattedMessage.replace(/%{2,2}/g, "%");
  return formattedMessage;
}
var STACK_FRAMES_TO_IGNORE = 2;
function cleanErrorStack(error) {
  if (!error.stack) {
    return;
  }
  const nextStack = error.stack.split("\n");
  nextStack.splice(1, STACK_FRAMES_TO_IGNORE);
  error.stack = nextStack.join("\n");
}
var InvariantError = class extends Error {
  constructor(message, ...positionals) {
    super(message);
    this.message = message;
    this.name = "Invariant Violation";
    this.message = format(message, ...positionals);
    cleanErrorStack(this);
  }
};
var invariant = (predicate, message, ...positionals) => {
  if (!predicate) {
    throw new InvariantError(message, ...positionals);
  }
};
invariant.as = (ErrorConstructor, predicate, message, ...positionals) => {
  if (!predicate) {
    const formatMessage = positionals.length === 0 ? message : format(message, ...positionals);
    let error;
    try {
      error = Reflect.construct(ErrorConstructor, [
        formatMessage
      ]);
    } catch (err) {
      error = ErrorConstructor(formatMessage);
    }
    throw error;
  }
};

// node_modules/@open-draft/deferred-promise/build/index.mjs
function createDeferredExecutor() {
  const executor = (resolve, reject) => {
    executor.state = "pending";
    executor.resolve = (data) => {
      if (executor.state !== "pending") {
        return;
      }
      executor.result = data;
      const onFulfilled = (value) => {
        executor.state = "fulfilled";
        return value;
      };
      return resolve(
        data instanceof Promise ? data : Promise.resolve(data).then(onFulfilled)
      );
    };
    executor.reject = (reason) => {
      if (executor.state !== "pending") {
        return;
      }
      queueMicrotask(() => {
        executor.state = "rejected";
      });
      return reject(executor.rejectionReason = reason);
    };
  };
  return executor;
}
var DeferredPromise = class extends Promise {
  #executor;
  resolve;
  reject;
  constructor(executor = null) {
    const deferredExecutor = createDeferredExecutor();
    super((originalResolve, originalReject) => {
      deferredExecutor(originalResolve, originalReject);
      executor?.(deferredExecutor.resolve, deferredExecutor.reject);
    });
    this.#executor = deferredExecutor;
    this.resolve = this.#executor.resolve;
    this.reject = this.#executor.reject;
  }
  get state() {
    return this.#executor.state;
  }
  get rejectionReason() {
    return this.#executor.rejectionReason;
  }
  then(onFulfilled, onRejected) {
    return this.#decorate(super.then(onFulfilled, onRejected));
  }
  catch(onRejected) {
    return this.#decorate(super.catch(onRejected));
  }
  finally(onfinally) {
    return this.#decorate(super.finally(onfinally));
  }
  #decorate(promise) {
    return Object.defineProperties(promise, {
      resolve: { configurable: true, value: this.resolve },
      reject: { configurable: true, value: this.reject }
    });
  }
};

// src/preview/relay/constants.ts
var CHANNEL_NAME = "$CSB_RELAY";

// src/preview/relay/utils.ts
function getWorkerInstance(registration) {
  return registration.installing || registration.waiting || registration.active;
}

// src/preview/relay/main.ts
var workerChannel = new MessageChannel();
var workerReadyPromise = new DeferredPromise();
workerReadyPromise.then((worker) => {
  const workerInitMessage = {
    $channel: CHANNEL_NAME,
    $type: "worker/init"
  };
  worker.postMessage(workerInitMessage, [workerChannel.port2]);
  return worker;
});
var parentPortPromise = new DeferredPromise();
window.addEventListener(
  "message",
  (event) => {
    if (event.data.$type === "preview/init") {
      const parentPort = event.ports[0];
      parentPort.onmessage = async (evt) => {
        if (typeof evt.data === "object" && evt.data.$channel === CHANNEL_NAME && evt.data.$type === "preview/response") {
          const msg = evt.data;
          workerChannel.port1.postMessage(msg);
        }
      };
      parentPortPromise.resolve(parentPort);
    }
  }
);
workerChannel.port1.onmessage = async (event) => {
  const data = event.data;
  if (data.$channel === CHANNEL_NAME) {
    const port = await parentPortPromise;
    const message = data;
    port.postMessage(message);
  }
};
var workerUrl = new URL("/__csb_sw.rpfsli6sirrzs1630o3lgzuxwlr2uqc.js", location.origin).href;
function preventStaleTermination(worker) {
  const keepaliveInterval = setInterval(() => {
    const pingMessage = {
      $channel: CHANNEL_NAME,
      $type: "worker/ping"
    };
    worker.postMessage(pingMessage);
  }, 5e3);
  worker.addEventListener("statechange", () => {
    if (worker.state === "redundant") {
      clearInterval(keepaliveInterval);
    }
  });
}
async function getServiceWorker() {
  invariant(
    "serviceWorker" in navigator,
    "Failed to start the relay Service Worker: Service Worker API is not supported in this browser"
  );
  const registerWorker = async () => {
    const registration2 = await navigator.serviceWorker.register(
      "/__csb_sw.rpfsli6sirrzs1630o3lgzuxwlr2uqc.js",
      {
        scope: "/"
      }
    );
    return getWorkerInstance(registration2);
  };
  const registrations = await navigator.serviceWorker.getRegistrations();
  await Promise.all(
    registrations.map((registration2) => {
      const worker = getWorkerInstance(registration2);
      if (worker && worker.scriptURL !== workerUrl) {
        return registration2.unregister();
      }
    })
  );
  const { controller } = navigator.serviceWorker;
  if (!controller) {
    return registerWorker();
  }
  if (controller.scriptURL === workerUrl) {
    return controller;
  }
  const [controllerRegistration, registration] = await Promise.all([
    navigator.serviceWorker.getRegistration(controller.scriptURL),
    navigator.serviceWorker.getRegistration(workerUrl)
  ]);
  if (!registration) {
    await controllerRegistration?.unregister();
    return registerWorker();
  }
  if (registration.waiting) {
    await registration.update();
    const worker = getWorkerInstance(registration);
    invariant(
      worker,
      "Failed to retrieve the worker instance after promotion: worked does not exist"
    );
    invariant(
      registration.active,
      'Failed to promove a waiting Service Worker: expected the worker state to be "active" but got "%s"',
      worker.state
    );
    return worker;
  }
  return null;
}
async function start() {
  const worker = await getServiceWorker().catch((error) => {
    console.error(
      "Failed to ensure the relay has a Service Worker registered. See details below."
    );
    console.error(error);
    return null;
  });
  if (worker) {
    await navigator.serviceWorker.ready;
    preventStaleTermination(worker);
    workerReadyPromise.resolve(worker);
  }
  const parentPort = await parentPortPromise;
  const readyMessage = {
    $channel: CHANNEL_NAME,
    $type: "preview/ready"
  };
  parentPort.postMessage(readyMessage);
}
start().catch(console.error);
