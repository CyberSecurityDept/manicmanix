import React from 'react'
import { HashRouter as Router, Route, Routes } from 'react-router-dom'
import SearchDevicePage from './pages/SearchDevicePage'
import DeviceInfoPage from './pages/DeviceInfoPage'
import ADBPage from './pages/ADBPage'
import FastScanPage from './pages/FastScanPage'
import UnderMaintenance from './pages/UnderMaintenance'
import ResultFastPage from './pages/ResultFastPage'
import FullScanPage from './pages/FullScanPage'
import ResultFullScanPage from './pages/ResultFullScanPage'
import OTA from './pages/OtaPage'
import InformationPage from './pages/InformationPage'
import HistoryPage from './pages/HistoryPage'
import HistoryDetailFullScanPage from './pages/HistoryDetailFulllScanPage'
import HistoryDetailFastScanPage from './pages/HistoryDetailFastScanPage'

function App() {
  // Pastikan ipcHandle hanya dipanggil jika window.electron ada
  const ipcHandle = () => {
    if (window.electron) {
      window.electron.ipcRenderer.send('ping')
    } else {
      console.error('IPC Renderer not found. Make sure preload.js is properly configured.')
    }
  }

  return (
    <Router>
      <Routes>
        {/* Route untuk halaman SearchDevicePage */}
        <Route path="/" element={<SearchDevicePage />} />

        {/* Route untuk halaman ADBPage */}
        <Route path="/adb-device" element={<ADBPage />} />

        {/* Route untuk maintenance*/}
        <Route path="/maintenance" element={<UnderMaintenance />} />

        {/* Route untuk halaman DeviceInfoPage */}
        <Route path="/device-info" element={<DeviceInfoPage />} />

        {/* Route untuk halaman FastScanPage */}
        <Route path="/fast-scan" element={<FastScanPage />} />

        {/* Route untuk halaman ResultFastPage */}
        <Route path="/result-fast" element={<ResultFastPage />} />

        {/* Route untuk halaman FullScanPage */}
        <Route path="/full-scan" element={<FullScanPage />} />

        {/* Route untuk halaman ResultFullScanPage */}
        <Route path="/result-full-scan" element={<ResultFullScanPage />} />

        {/* Route untuk halaman HistoryPage */}
        <Route path="/history" element={<HistoryPage />} />

        {/* Route untuk halaman HistoryDetailPage */}
        <Route
          path="/history-detail/full-scan/:serialNumber/:timeStamp"
          element={<HistoryDetailFullScanPage />}
        />
        <Route
          path="/history-detail/fast-scan/:serialNumber/:timeStamp"
          element={<HistoryDetailFastScanPage />}
        />

        {/* Route untuk halaman OTA */}
        <Route path="/ota" element={<OTA />} />

        {/* Route untuk halaman Information */}
        <Route path="/info" element={<InformationPage />} />
      </Routes>
    </Router>
  )
}

export default App
