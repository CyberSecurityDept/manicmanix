const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electron', {
  ipcRenderer: {
    send: (channel, data) => ipcRenderer.send(channel, data),
    on: (channel, func) => ipcRenderer.on(channel, func),
    once: (channel, func) => ipcRenderer.once(channel, func),
    removeListener: (channel, func) => ipcRenderer.removeListener(channel, func)
  }
})
