import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "RTXVideoSuite.VideoReviewGo",

    setup() {
        // Obsługa przerwania globalnego
        const original_api_interrupt = api.interrupt;
        api.interrupt = function () {
            fetch("/rtx_review/cancel/all", { method: "POST" }).catch(() => {});
            original_api_interrupt.apply(this, arguments);
        };

        // Nasłuchiwanie sygnału z Pythona
        api.addEventListener("rtx_show_review_player", (event) => {
            const { node_id } = event.detail;
            const node = app.graph.getNodeById(node_id);

            if (node) {
                // Czyszczenie starego wideo
                if (node.videoWidget) {
                    node.videoWidget.element.remove();
                    const widgetIndex = node.widgets.indexOf(node.videoWidget);
                    if (widgetIndex > -1) node.widgets.splice(widgetIndex, 1);
                }

                const videoContainer = document.createElement("div");
                videoContainer.style.width = "100%";
                videoContainer.style.marginTop = "8px";

                const video = document.createElement("video");
                video.src = `/rtx_review/video/${node_id}?t=${Date.now()}`;
                video.controls = true;
                video.autoplay = true;
                video.muted = true;
                video.style.width = "100%";
                video.style.maxHeight = "350px";
                video.style.borderRadius = "4px";

                videoContainer.appendChild(video);

                node.videoWidget = node.addDOMWidget("video_player", "video_player", videoContainer, {
                    getValue: () => video.src,
                    setValue: () => {}
                });

                video.addEventListener("loadedmetadata", () => {
                    const extraHeight = 160 + (node.widgets ? node.widgets.length * 20 : 0);
                    const calculatedHeight = extraHeight + (video.videoHeight / video.videoWidth) * node.size[0];
                    node.setSize([node.size[0], Math.max(node.size[1], calculatedHeight)]);
                    app.graph.setDirtyCanvas(true, true);
                });
            }
        });
    },

    nodeCreated(node) {
        if (node.comfyClass === "RTXVideoReviewGo") {
            
            const cleanupUI = () => {
                if (node.videoWidget) {
                    node.videoWidget.element.remove();
                    const widgetIndex = node.widgets.indexOf(node.videoWidget);
                    if (widgetIndex > -1) node.widgets.splice(widgetIndex, 1);
                    node.videoWidget = null;
                    node.setSize([node.size[0], 120]);
                    app.graph.setDirtyCanvas(true, true);
                }
            };

            node.addWidget("button", "▶️ VIDEO OK → GO", "continue_btn", () => {
                api.fetchApi(`/rtx_review/continue/${node.id}`, { method: "POST" });
                cleanupUI();
            });

            node.addWidget("button", "❌ CANCEL WORKFLOW", "cancel_btn", () => {
                api.fetchApi(`/rtx_review/cancel/${node.id}`, { method: "POST" });
                cleanupUI();
            });

            node.onRemoved = () => cleanupUI();
        }
    }
});
