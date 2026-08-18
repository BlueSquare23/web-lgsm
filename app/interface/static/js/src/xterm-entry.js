// Bundle entry point for xterm.js + addon-fit.
//
// Exposes the same globals (`Terminal`, `FitAddon.FitAddon`) that the old
// UMD builds served straight out of node_modules provided, so
// update-xterm.js doesn't need to change.
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';

window.Terminal = Terminal;
window.FitAddon = { FitAddon };
