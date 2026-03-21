import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "RTXVideoSuite.VideoPlayerNode",

    setup() {
        api.addEventListener("rtx_play_video", (event) => {
            const { node_id, video_url, autoplay, loop, mute, info } = event.detail;
            const node = app.graph.getNodeById(node_id);

            if (node) {
                console.log(`[RTX Player] Rendering video for node ${node_id}`);

                // 1. Czyszczenie poprzedniego wideo (żeby się nie duplikowały przy re-runie)
                if (node.videoWidget) {
                    node.videoWidget.element.remove();
                    const widgetIndex = node.widgets.indexOf(node.videoWidget);
                    if (widgetIndex > -1) {
                        node.widgets.splice(widgetIndex, 1);
                    }
                }
                
                if (node.infoWidget) {
                    node.infoWidget.value = info;
                }

                // 2. Budowa kontenera
                const videoContainer = document.createElement("div");
                videoContainer.style.width = "100%";
                videoContainer.style.marginTop = "8px";
                videoContainer.style.backgroundColor = "#111";
                videoContainer.style.border = "1px solid #333";
                videoContainer.style.borderRadius = "6px";
                videoContainer.style.overflow = "hidden";

                // 3. Odtwarzacz Wideo HTML5
                const video = document.createElement("video");
                video.src = `${video_url}&t=${Date.now()}`; // Cache buster
                video.controls = true;
                video.autoplay = autoplay;
                video.loop = loop;
                video.muted = mute;
                video.style.width = "100%";
                video.style.maxHeight = "400px";
                video.style.display = "block"; // Usuwa margines na dole elementu inline

                videoContainer.appendChild(video);

                // 4. Dołączenie Widgetu DOM do ComfyUI
                node.videoWidget = node.addDOMWidget("video_viewer", "video_viewer", videoContainer, {
                    getValue: () => video.src,
                    setValue: () => {}
                });

                // 5. Autodopasowanie rozmiaru noda do formatu wideo
                video.addEventListener("loadedmetadata", () => {
                    // Obliczamy wysokość na podstawie proporcji wideo + margines na UI noda
                    const extraHeight = 100 + (node.widgets ? node.widgets.length * 22 : 0);
                    const calculatedHeight = extraHeight + (video.videoHeight / video.videoWidth) * node.size[0];
                    node.setSize([node.size[0], Math.max(node.size[1], calculatedHeight)]);
                    app.graph.setDirtyCanvas(true, true);
                });

                // Obsługa błędu odtwarzania (np. format, którego przeglądarka nie trawi - np. surowe AVI)
                video.addEventListener("error", () => {
                    console.warn("[RTX Player] Browser cannot play this video format format.");
                    if (node.infoWidget) {
                        node.infoWidget.value = "⚠️ Format not supported by browser";
                    }
                });
            }
        });
    },

    nodeCreated(node) {
        if (node.comfyClass === "RTXVideoPlayer") {
            // Dodajemy pole tekstowe z informacją o pliku
            node.infoWidget = node.addWidget("text", "File Info", "Waiting for video...", () => {});
            // Blokujemy edycję pola tekstowego przez użytkownika
            node.infoWidget.inputEl.readOnly = true;
            node.infoWidget.inputEl.style.opacity = "0.7";
            node.infoWidget.inputEl.style.textAlign = "center";
            
            node.setSize([350, 150]); // Domyślny rozmiar
        }
    }
});
