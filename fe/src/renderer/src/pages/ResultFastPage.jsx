import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'
import bgImage from '../assets/bg-darkmode.png'
import plusSign from '../assets/plus-sign.svg'
import RemoveModal from '../components/modal/Delete'
import CompleteModal from '../components/modal/Complete'
import DeleteProgressModal from '../components/modal/DeleteProgress'
import AfterCompleteModal from '../components/modal/AfterComplete'
import removeButtonImage from '../assets/border/remove-button.svg'
import bgGood from '../assets/border/percentage-good.svg'
import bgAverage from '../assets/border/percentage-average.svg'
import bgBad from '../assets/border/percentage-bad.svg'
import completeScanButton from '../assets/border/complete-scan.svg'
import noMalwareImage from '../assets/no-malware3.jpg'

// Mengambil BASE_URL dari environment variables
const BASE_URL = import.meta.env.VITE_BASE_URL
const RESULT_FASTSCAN_ENDPOINT = '/v1/result-fastscan'

const ResultFastPage = () => {
  // State untuk modals
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false)
  const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false)
  const [isAfterCompleteModalOpen, setIsAfterCompleteModalOpen] = useState(false)
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false)

  // State untuk security percentage
  const [securityPercentage, setSecurityPercentage] = useState(0)
  const [lastScanPercentage, setLastScanPercentage] = useState(null)
  const [beforePercentage, setBeforePercentage] = useState(null)

  // State untuk list threats (yang akan di-render di grid)
  const [filteredThreats, setFilteredThreats] = useState([])
  const [selectAll, setSelectAll] = useState(false)
  const [checkedItems, setCheckedItems] = useState({})
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

  // State untuk data device dan hasil scan
  const [serialNumber, setSerialNumber] = useState(null)
  const [detectedThreats, setDetectedThreats] = useState([])
  const [deleteProgress, setDeleteProgress] = useState(0)

  // State untuk device info (menggunakan phone_model dan security_patch_date sebagai OS Version)
  const [deviceInfo, setDeviceInfo] = useState({ phone_model: '', os_version: '' })

  // State untuk loading
  const [loading, setLoading] = useState(true)

  const navigate = useNavigate()

  // Fungsi untuk menandai progress delete selesai
  const handleProgressComplete = () => {
    setIsProgressModalOpen(false)
    setBeforePercentage(lastScanPercentage)
  }

  // Ambil serial number dari localStorage
  useEffect(() => {
    const savedSerialNumber = localStorage.getItem('serial_number')
    if (savedSerialNumber) {
      setSerialNumber(savedSerialNumber)
    } else {
      console.error('Serial number not found in localStorage.')
      navigate('/')
    }
  }, [navigate])

  // Fetch data fast-scan jika serialNumber sudah tersedia
  useEffect(() => {
    if (serialNumber) {
      fetchFastScanResult()
    }
  }, [serialNumber])

  const fetchFastScanResult = async () => {
    try {
      const response = await fetch(
        `${BASE_URL}${RESULT_FASTSCAN_ENDPOINT}?serial_number=${serialNumber}`
      )
      const data = await response.json()
      console.log('Full response:', data)
      if (data.status === 'success') {
        const result = data.data
        console.log('Result:', result)
        setDeviceInfo({
          phone_model: result.phone_model || 'Unknown Model',
          os_version: result.security_patch_date || 'Unknown OS'
        })
        setSecurityPercentage(parseFloat(result.security_percentage) || 0)
        setLastScanPercentage(result.last_scan_percentage || null)
        setDetectedThreats(result.threats || [])
        setFilteredThreats(result.threats || [])
      } else {
        console.error('Failed to fetch fast-scan result:', data.message)
        setDetectedThreats([])
        setFilteredThreats([])
      }
    } catch (error) {
      console.error('Error fetching fast-scan result:', error)
      setDetectedThreats([])
      setFilteredThreats([])
    } finally {
      setLoading(false)
    }
  }

  // Modal open functions
  const openRemoveModal = () => setIsRemoveModalOpen(true)
  const openCompleteModal = () => setIsCompleteModalOpen(true)
  const handleCompleteConfirm = () => {
    setIsCompleteModalOpen(false)
    setIsAfterCompleteModalOpen(true)
  }

  // Fungsi untuk menutup AfterCompleteModal
  const closeAfterCompleteModal = () => {
    setIsAfterCompleteModalOpen(false)
  }

  // Fungsi untuk menangani penghapusan paket
  const handleRemoveScanning = async () => {
    // Tutup modal remove dan buka modal progress
    setIsRemoveModalOpen(false)
    setIsProgressModalOpen(true)

    // Lakukan delete dan update data
    await handleDeleteChecked()
    await fetchFastScanResult()

    // Tutup modal progress setelah proses selesai
    setIsProgressModalOpen(false)
  }

  // Handle delete confirmation
  const handleDeleteChecked = async () => {
    const packagesToDelete = Object.keys(checkedItems).filter((pkgName) => checkedItems[pkgName])
    if (packagesToDelete.length === 0) {
      alert('No package selected for deletion.')
      return
    }
    const total = packagesToDelete.length
    let completed = 0
    for (const packageName of packagesToDelete) {
      const url = `${BASE_URL}/v1/delete-package-fastscan/${encodeURIComponent(packageName)}`
      try {
        const response = await fetch(url, {
          method: 'DELETE',
          headers: { accept: 'application/json' }
        })
        if (!response.ok) {
          console.error(`Failed to delete ${packageName}: Status ${response.status}`)
        } else {
          console.log(`Package ${packageName} successfully deleted.`)
        }
      } catch (error) {
        console.error(`Error deleting package ${packageName}:`, error)
      }
      completed++
      setDeleteProgress(Math.floor((completed / total) * 100))
    }
    // Reset state checkbox agar tidak tersisa untuk delete berikutnya
    setCheckedItems({})
    setSelectAll(false)
    // Reset progress setelah beberapa saat (misalnya 1 detik)
    setTimeout(() => {
      setDeleteProgress(0)
    }, 1000)
  }

  // Fungsi sorting untuk grid view
  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })

    const sorted = [...filteredThreats].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'asc' ? -1 : 1
      if (a[key] > b[key]) return direction === 'asc' ? 1 : -1
      return 0
    })
    setFilteredThreats(sorted)
  }

  // Fungsi checkbox untuk threat individual
  const handleCheckboxChange = (packageName) => {
    setCheckedItems((prev) => {
      const newChecked = { ...prev, [packageName]: !prev[packageName] }
      if (
        filteredThreats.length > 0 &&
        filteredThreats.every((threat) => newChecked[threat.package_name])
      ) {
        setSelectAll(true)
      } else {
        setSelectAll(false)
      }
      return newChecked
    })
  }

  // Fungsi untuk select all threat secara global
  const handleSelectAllChange = () => {
    const allSelected = filteredThreats.every((threat) => checkedItems[threat.package_name])
    const updatedCheckedItems = { ...checkedItems }
    filteredThreats.forEach((threat) => {
      updatedCheckedItems[threat.package_name] = !allSelected
    })
    setCheckedItems(updatedCheckedItems)
    setSelectAll(!allSelected)
  }

  // Fungsi untuk menentukan style percentage berdasarkan nilai
  const getPercentageStyle = (percentage) => {
    if (percentage >= 90 && percentage <= 100) {
      return {
        backgroundImage: `url(${bgGood})`,
        color: '#0DDF80',
        label: '(Good)'
      }
    } else if (percentage >= 80 && percentage <= 89) {
      return {
        backgroundImage: `url(${bgAverage})`,
        color: '#F3DA00',
        label: '(Average)'
      }
    } else {
      return {
        backgroundImage: `url(${bgBad})`,
        color: '#D3351D',
        label: '(Bad)'
      }
    }
  }

  const percentageStyle = getPercentageStyle(securityPercentage || 0)
  const lastPercentageStyle =
    lastScanPercentage !== null ? getPercentageStyle(lastScanPercentage) : {}

  return (
    <div
      className="h-screen w-screen flex flex-col items-center justify-center relative font-aldrich"
      style={{ backgroundImage: `url(${bgImage})`, backgroundSize: 'cover' }}
    >
      {/* Security Percentage Section */}
      <div className="flex flex-col items-center justify-center space-y-2 relative">
        <h2 className="text-4xl font-bold text-white">Security Percentage</h2>
        <div
          className="relative flex items-center justify-center"
          style={{
            color: percentageStyle.color,
            width: '300px',
            height: '180px',
            backgroundImage: percentageStyle.backgroundImage,
            backgroundSize: 'contain',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div className="flex flex-col items-center justify-center">
            <h2 className="text-[52px] leading-none">
              {loading || securityPercentage === null ? (
                <Skeleton width={150} height={52} baseColor="#c0c0c0" highlightColor="#e0e0e0" />
              ) : (
                `${Math.round(securityPercentage)}%`
              )}
            </h2>
            <p className="text-[18px]" style={{ color: percentageStyle.color }}>
              {percentageStyle.label}
            </p>
            {beforePercentage !== null && (
              <p className="text-[16px]" style={{ color: percentageStyle.color }}>
                Before: {beforePercentage}%
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Card Container */}
      <div className="relative w-[1001px] mb-4">
        {/* Device Info Card */}
        <div className="relative h-[89px] text-center p-6 border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612]">
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute top-[-13px] left-[-13px] w-6 h-6"
          />
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute bottom-[-12px] right-[-13px] w-6 h-6"
          />
          <div className="grid grid-cols-3 gap-4 text-white">
            <div>
              <p className="font-semibold text-white">Security Patch</p>
              <p className="text-gray-100 mt-1">
                {loading ? <Skeleton width={100} /> : deviceInfo.os_version}
              </p>
            </div>
            <div>
              <p className="font-semibold text-white">Phone Model</p>
              <p className="text-gray-100 mt-1">
                {loading ? <Skeleton width={150} /> : deviceInfo.phone_model || 'Unknown Model'}
              </p>
            </div>
            <div>
              <p className="font-semibold text-white">Last Scan Percentage</p>
              {lastScanPercentage !== null ? (
                <p className="mt-1 font-bold" style={{ color: percentageStyle.color }}>
                  {parseFloat(lastScanPercentage).toFixed(0)}% {percentageStyle.label}
                </p>
              ) : (
                <p className="text-white mt-1 font-bold">-</p>
              )}
            </div>
          </div>
        </div>

        {/* View Section */}
        <div className="w-full h-[350px] p-4 border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] text-white relative mt-4">
          {loading ? (
            <div className="space-y-1">
              {[...Array(5)].map((_, index) => (
                <div
                  key={index}
                  className="grid grid-cols-12 p-2 items-center border-b border-[#EAECF0]"
                >
                  <Skeleton width={100} className="col-span-5" />
                  <Skeleton width={150} className="col-span-5" />
                  <Skeleton width={20} className="col-span-2" />
                </div>
              ))}
            </div>
          ) : filteredThreats.length > 0 ? (
            <>
              {/* Header Grid */}
              <div className="w-full bg-[#00B3A2] grid grid-cols-12 p-2 items-center text-sm text-black">
                <div
                  className="col-span-5 flex items-center gap-1 cursor-pointer"
                  onClick={() => handleSort('date_time')}
                >
                  Date Time{' '}
                  <span>
                    {sortConfig.key === 'date_time'
                      ? sortConfig.direction === 'asc'
                        ? '↓'
                        : '↑'
                      : '↓'}
                  </span>
                </div>
                <div
                  className="col-span-5 flex items-center gap-1 cursor-pointer"
                  onClick={() => handleSort('package_name')}
                >
                  Package Name{' '}
                  <span>
                    {sortConfig.key === 'package_name'
                      ? sortConfig.direction === 'asc'
                        ? '↓'
                        : '↑'
                      : '↓'}
                  </span>
                </div>
                <div className="col-span-2 flex justify-end">
                  <label className="checkbox-container">
                    <input
                      type="checkbox"
                      className="custom-checkbox select-all"
                      checked={selectAll}
                      onChange={handleSelectAllChange}
                    />
                    <span className="checkmark"></span>
                  </label>
                </div>
              </div>

              {/* List Data */}
              <div className="space-y-[1px] max-h-56 overflow-y-auto">
                {filteredThreats.map((threat, index) => (
                  <div
                    key={index}
                    className="w-full grid grid-cols-12 p-2 items-center border-b border-[#1A1A1A] text-white"
                  >
                    <div className="col-span-5">
                      {threat.date_time ? new Date(threat.date_time).toLocaleString() : '-'}
                    </div>
                    <div className="flex items-center col-span-7 justify-between">
                      <div className="flex items-center gap-4">
                        <span>{threat.package_name}</span>
                      </div>
                      <label className="checkbox-container">
                        <input
                          type="checkbox"
                          className="custom-checkbox"
                          checked={checkedItems[threat.package_name] || false}
                          onChange={() => handleCheckboxChange(threat.package_name)}
                        />
                        <span className="checkmark"></span>
                      </label>
                    </div>
                    <div className="col-span-2"></div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            // Jika tidak ada data, tampilkan gambar No Malware Detected
            <div className="relative flex justify-center items-center h-full">
              <img src={noMalwareImage} alt="No Malware" className="h-[300px]" />
              <div className="absolute inset-0 bg-black opacity-85"></div>
              <p className="absolute text-center text-[#00FFE7] font-bold text-2xl">
                No Malware Detected
              </p>
            </div>
          )}

          {filteredThreats.length > 0 && <div className="border-b border-gray-400 mt-7 mb-5"></div>}

          {/* Tombol Remove */}
          {filteredThreats.length > 0 && (
            <div className="text-right mb-3">
              <button
                className="w-[267px] h-[43px] bg-transparent text-white font-bold relative overflow-hidden"
                style={{
                  backgroundImage: `url(${removeButtonImage})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
                onClick={openRemoveModal}
              >
                <span className="relative z-10">Remove</span>
                <div className="absolute inset-0 bg-red-900 opacity-0 hover:opacity-30 transition-opacity"></div>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Complete Scan Button */}
      <div className="mt-4">
        <button
          className="w-[389px] h-[64px] bg-transparent text-white font-bold"
          style={{
            backgroundImage: `url(${completeScanButton})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
          onClick={openCompleteModal}
        >
          COMPLETE SCAN
        </button>
      </div>

      {/* Modals */}
      {isProgressModalOpen && (
        <DeleteProgressModal
          progress={deleteProgress}
          onClose={() => setIsProgressModalOpen(false)}
          onProgressComplete={handleProgressComplete}
        />
      )}
      {isCompleteModalOpen && (
        <CompleteModal
          onClose={() => setIsCompleteModalOpen(false)}
          onConfirm={handleCompleteConfirm}
        />
      )}
      {isAfterCompleteModalOpen && <AfterCompleteModal onClose={closeAfterCompleteModal} />}
      {isRemoveModalOpen && (
        <RemoveModal onClose={() => setIsRemoveModalOpen(false)} onConfirm={handleRemoveScanning} />
      )}
    </div>
  )
}

export default ResultFastPage
