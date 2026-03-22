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

                // Aktualizacja tekstu informacyjnego
                if (node.infoWidget) {
                    node.infoWidget.value = info;
                }

                // TWORZYMY WIDGET TYLKO RAZ (jeśli go nie ma)
                if (!node.videoWidget) {
                    const videoContainer = document.createElement("div");
                    videoContainer.style.width = "100%";
                    videoContainer.style.marginTop = "8px";
                    videoContainer.style.backgroundColor = "#111";
                    videoContainer.style.border = "1px solid #333";
                    videoContainer.style.borderRadius = "6px";
                    videoContainer.style.overflow = "hidden";
                    videoContainer.style.display = "flex";
                    videoContainer.style.justifyContent = "center";

                    const video = document.createElement("video");
                    video.controls = true;
                    video.style.width = "100%";
                    video.style.maxHeight = "500px";
                    video.style.display = "block";

                    videoContainer.appendChild(video);

                    // Rejestrujemy element wideo w obiekcie node, aby mieć do niego szybki dostęp
                    node.videoElement = video;

                    // Dodajemy widget DOM do ComfyUI tylko ten jeden raz
                    node.videoWidget = node.addDOMWidget("video_viewer", "video_viewer", videoContainer, {
                        getValue: () => video.src,
                        setValue: () => {}
                    });

                    // Nasłuchujemy zmiany metadanych, żeby dostosować rozmiar noda
                    video.addEventListener("loadedmetadata", () => {
                        // Stały margines dla widgetów i UI (około 80-100px)
                        const extraHeight = 85; 
                        const calculatedHeight = extraHeight + (video.videoHeight / video.videoWidth) * node.size[0];
                        
                        // Ustawiamy DOKŁADNĄ wysokość (usuwamy Math.max, żeby węzeł mógł też zmaleć)
                        node.setSize([node.size[0], calculatedHeight]);
                        app.graph.setDirtyCanvas(true, true);
                    });

                    video.addEventListener("error", () => {
                        console.warn("[RTX Player] Browser cannot play this video format.");
                        if (node.infoWidget) {
                            node.infoWidget.value = "⚠️ Format not supported by browser";
                        }
                    });
                }

                // -------------------------------------------------------------
                // AKTUALIZACJA WIDEO (zawsze wykonywana, bez niszczenia DOM)
                // -------------------------------------------------------------
                node.videoElement.autoplay = autoplay;
                node.videoElement.loop = loop;
                node.videoElement.muted = mute;
                // Dodajemy Date.now() aby obejść cache przeglądarki
                node.videoElement.src = `${video_url}&t=${Date.now()}`; 
            }
        });
    },

    nodeCreated(node) {
        if (node.comfyClass === "RTXVideoPlayer") {
            // Dodajemy pole tekstowe z informacją o pliku
            node.infoWidget = node.addWidget("text", "File Info", "Waiting for video...", () => {});
            node.infoWidget.inputEl.readOnly = true;
            node.infoWidget.inputEl.style.opacity = "0.7";
            node.infoWidget.inputEl.style.textAlign = "center";
            
            node.setSize([350, 150]); // Domyślny rozmiar początkowy
        }
    }
});
