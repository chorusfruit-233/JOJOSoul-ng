/*!
 * coi-serviceworker v0.0.5 (精简版)
 * 基于 https://github.com/gzuidhof/coi-serviceworker (MIT)
 * 作用：为 GitHub Pages 等不支持自定义 HTTP 头的平台注入
 *       Cross-Origin-Opener-Policy / Cross-Origin-Embedder-Policy 头，
 *       从而启用 SharedArrayBuffer（Web Worker + Atomics 同步阻塞所需）。
 */

let coepCredentialless = false;

if (typeof window === "undefined") {
    self.addEventListener("install", () => self.skipWaiting());
    self.addEventListener("activate", (event) =>
        event.waitUntil(self.clients.claim())
    );

    self.addEventListener("message", (ev) => {
        if (!ev.data) return;
        if (ev.data.type === "deregister") {
            self.registration
                .unregister()
                .then(() => self.clients.matchAll())
                .then((clients) =>
                    clients.forEach((client) =>
                        client.navigate(client.url)
                    )
                );
        } else if (ev.data.type === "coepCredentialless") {
            coepCredentialless = ev.data.value;
        }
    });

    self.addEventListener("fetch", (event) => {
        const r = event.request;
        if (r.cache === "only-if-cached" && r.mode !== "same-origin") {
            return;
        }

        const request = (() => {
            if (coepCredentialless && r.mode === "no-cors") {
                return new Request(r, {
                    credentials: "omit",
                });
            }
            return r;
        })();

        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response.status === 0) {
                        return response;
                    }

                    const newHeaders = new Headers(response.headers);
                    newHeaders.set(
                        "Cross-Origin-Embedder-Policy",
                        coepCredentialless
                            ? "credentialless"
                            : "require-corp"
                    );
                    if (!coepCredentialless) {
                        newHeaders.set(
                            "Cross-Origin-Resource-Policy",
                            "same-origin"
                        );
                    }
                    newHeaders.set("Cross-Origin-Opener-Policy", "same-origin");

                    const blob = response.blob();
                    return blob.then((body) => {
                        return new Response(body, {
                            status: response.status,
                            statusText: response.statusText,
                            headers: newHeaders,
                        });
                    });
                })
                .catch((e) => console.error(e))
        );
    });
} else {
    (() => {
        const reloaded = sessionStorage.getItem("coi-reloaded");
        if (reloaded) {
            sessionStorage.removeItem("coi-reloaded");
            return;
        }

        // 检查是否已经有 cross-origin isolation
        const isCrossOriginIsolated =
            crossOriginIsolated ||
            self.crossOriginIsolated ||
            window.crossOriginIsolated;

        const hasCOEP = !!(
            window.crossOriginIsolated ||
            self.crossOriginIsolated
        );

        if (!isCrossOriginIsolated) {
            sessionStorage.setItem("coi-reloaded", "1");
            registerSW();
        }
    })();

    function registerSW() {
        if (!window.isSecureContext) {
            console.warn(
                "COI Service Worker 需要 HTTPS 或 localhost 环境"
            );
            return;
        }
        navigator.serviceWorker
            .register(window.currentScript?.src || "coi-serviceworker.js")
            .then(
                (registration) =>
                    registration.addEventListener("updatefound", () =>
                        location.reload()
                    ),
                (err) => console.error("COI SW 注册失败:", err)
            );
    }
}
