import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { autoUpdater } from 'electron-updater'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: true,
    fullscreen: true,
    frame: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: true,
      webviewTag: true, // izinkan penggunaan webview
      webSecurity: false,
    }
  })

  // Atur Content Security Policy
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https: http:;",
          "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: http:;",
          "frame-src 'self' https: http:;",
          "img-src 'self' data: https: http:;",
          "style-src 'self' 'unsafe-inline' https: http:;"
        ].join(' ')
      }
    })
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  // Buka URL eksternal di browser default
  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // Load URL renderer (development) atau file lokal (production)
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }

  // --- Integrasi electron-updater ---
  // Mulai update FE (electron-updater) ketika renderer mengirim pesan
  ipcMain.on('start-fe-update', async () => {
    try {
      const result = await autoUpdater.checkForUpdates()
      // Misal, jika update tersedia:
      const updateAvailable = result.updateInfo && result.updateInfo.version !== app.getVersion()
      mainWindow.webContents.send('fe-update-status', {
        updateAvailable,
        version: result.updateInfo.version
      })
    } catch (error) {
      mainWindow.webContents.send('fe-update-status', {
        updateAvailable: false,
        error: error.message
      })
    }
  })

  // Kirim progress download FE ke renderer
  autoUpdater.on('download-progress', (progressObj) => {
    mainWindow.webContents.send('fe-update-progress', progressObj)
  })

  // Setelah update FE selesai didownload, kirim notifikasi ke renderer
  autoUpdater.on('update-downloaded', () => {
    mainWindow.webContents.send('fe-update-downloaded')
    // Jangan langsung quit; tunggu BE update selesai
  })

  // Ketika renderer mengirim pesan untuk quit dan install update FE
  ipcMain.on('quit-and-install', () => {
    autoUpdater.quitAndInstall()
  })
}

app.whenReady().then(() => {
  // Set App User Model ID (untuk Windows)
  electronApp.setAppUserModelId('com.electron')

  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
