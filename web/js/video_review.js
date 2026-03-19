import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "RTXVideoSuite.ReviewConfirmNode",

    setup() {
        // Intercept ComfyUI's global "Cancel Prompt" button
        const original_api_interrupt = api.interrupt;
        api.interrupt = function () {
            // Send cancel signal to all waiting review nodes
            fetch("/rtx_review/cancel/all", { method: "POST" }).catch(() => {});
            original_api_interrupt.apply(this, arguments);
        };

        // Listen for the Python signal to display the video
        api.addEventListener("rtx_review_show_video", (event) => {
            const { node_id } = event.detail;
            const node = app.graph.getNodeById(node_id);

            if (node) {
                console.log(`[RTX Review] Adding DOM video player for node ${node_id}`);

                // CLEANUP: Remove existing video widget if it exists (prevents stacking)
                if (node.videoWidget) {
                    node.videoWidget.element.remove();
                    const widgetIndex = node.widgets.indexOf(node.videoWidget);
                    if (widgetIndex > -1) {
                        node.widgets.splice(widgetIndex, 1);
                    }
                }

                // Create the video container
                const videoContainer = document.createElement("div");
                videoContainer.style.width = "100%";
                videoContainer.style.marginTop = "8px";
                videoContainer.style.backgroundColor = "#000";

                // Create the HTML5 video element
                const video = document.createElement("video");
                video.src = `/rtx_review/video/${node_id}?t=${Date.now()}`;
                video.controls = true;
                video.autoplay = true;
                video.muted = true; // Keep muted for reliable autoplay in modern browsers
                video.style.width = "100%";
                video.style.maxHeight = "350px";
                video.style.borderRadius = "4px";

                videoContainer.appendChild(video);

                // Attach as a DOM Widget (The cleanest, official ComfyUI method)
                node.videoWidget = node.addDOMWidget("video_player", "video_player", videoContainer, {
                    getValue: () => video.src,
                    setValue: () => {}
                });

                // Auto-resize the node based on video aspect ratio
                video.addEventListener("loadedmetadata", () => {
                    const extraHeight = 160 + (node.widgets ? node.widgets.length * 20 : 0);
                    const calculatedHeight = extraHeight + (video.videoHeight / video.videoWidth) * node.size[0];
                    node.setSize([node.size[0], Math.max(node.size[1], calculatedHeight)]);
                    app.graph.setDirtyCanvas(true, true);
                });

                video.play().catch(e => console.warn("[RTX Review] Autoplay blocked by browser:", e));
            }
        });
    },

    nodeCreated(node) {
        // Ensure this string matches your Python class name exactly!
        if (node.comfyClass === "VideoReviewAndConfirm") {
            
            // Helper function to remove the video player after a decision is made
            const cleanupUI = () => {
                if (node.videoWidget) {
                    // Remove from DOM
                    node.videoWidget.element.remove();
                    // Remove from ComfyUI widget list
                    const widgetIndex = node.widgets.indexOf(node.videoWidget);
                    if (widgetIndex > -1) {
                        node.widgets.splice(widgetIndex, 1);
                    }
                    node.videoWidget = null;
                    
                    // Shrink node back to default size
                    node.setSize([node.size[0], 120]);
                    app.graph.setDirtyCanvas(true, true);
                }
            };

            // Add Control Buttons
            node.addWidget("button", "▶️ UPSCALING → GO", "continue_btn", () => {
                api.fetchApi(`/rtx_review/continue/${node.id}`, { method: "POST" });
                cleanupUI();
            });

            node.addWidget("button", "❌ CANCEL WORKFLOW", "cancel_btn", () => {
                api.fetchApi(`/rtx_review/cancel/${node.id}`, { method: "POST" });
                cleanupUI();
            });

            // Clean up resources if the user deletes the node from the canvas
            node.onRemoved = function() {
                cleanupUI();
            };
        }
    }
});
