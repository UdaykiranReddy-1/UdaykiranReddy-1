import { bootstrapMorningCommandCenter } from "./shell/bootstrap.js";

const root = document.getElementById("command-center-root");
if (root) {
  bootstrapMorningCommandCenter({
    storageKey: "command-center",
    timezone: "Asia/Calcutta",
    slotRoot: root,
  });
}
