import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import '../styles/Checkbox.css'
import Skeleton from 'react-loading-skeleton'
import bgImage from '../assets/bg-darkmode.png'
import RemoveModal from '../components/modal/Delete'
import RiskModal from '../components/modal/Risk'
import CompleteModal from '../components/modal/Complete'
import AfterCompleteModal from '../components/modal/AfterComplete'
import DeleteProgressModal from '../components/modal/DeleteProgress'
import overview from '../assets/border/overview-section.svg'
import viewSection from '../assets/border/view-section.svg'
import bgModel from '../assets/border/percentage-section.svg'
import bgBorder from '../assets/border/overview-border.svg'
import bgGood from '../assets/border/percentage-good.svg'
import bgAverage from '../assets/border/percentage-average.svg'
import bgBad from '../assets/border/percentage-bad.svg'
import removeButtonImage from '../assets/border/remove-button.svg'
import completeScanButton from '../assets/border/complete-scan.svg'
import plusSign from '../assets/plus-sign.svg'

const ResultFullScanPage = () => {
  // Mengambil BASE_URL dari environment variables
  const BASE_URL = import.meta.env.VITE_BASE_URL
  const RESULT_URL = '/v1/result-fullscan'
  const DEVICE_IMAGE = '/v1/device-overview'
  const navigate = useNavigate()

  // State untuk modal
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false)
  const [isRiskModalOpen, setIsRiskModalOpen] = useState(false)
  const [selectedRiskData, setSelectedRiskData] = useState(null)
  const [isCompleteModalOpen, setIsCompleteModalOpen] = useState(false)
  const [isAfterCompleteModalOpen, setIsAfterCompleteModalOpen] = useState(false)
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false)

  // State untuk tampilan dan data
  const [selectedView, setSelectedView] = useState(null)
  const [showView, setShowView] = useState(false)
  const [selectAll, setSelectAll] = useState(false)
  // Gunakan objek untuk menyimpan status checkbox secara global (kunci: threat.name)
  const [checkedItems, setCheckedItems] = useState({})
  const [beforePercentage, setBeforePercentage] = useState(null)
  const [serialNumber, setSerialNumber] = useState(null)
  const [deviceInfo, setDeviceInfo] = useState({ phone_model: '', security_patch: '' })
  const [resultData, setResultData] = useState(null)
  const [securityPercentage, setSecurityPercentage] = useState(0)
  const [lastScanPercentage, setLastScanPercentage] = useState(null)
  const [deviceImageData, setDeviceImageData] = useState(null)
  const [deleteProgress, setDeleteProgress] = useState(0)

  // State untuk loading
  const [loading, setLoading] = useState(true)

  // Ambil serial_number dari localStorage
  useEffect(() => {
    const savedSerialNumber = localStorage.getItem('serial_number')
    if (savedSerialNumber) {
      setSerialNumber(savedSerialNumber)
    } else {
      console.error('Serial number not found in localStorage.')
      navigate('/')
    }
  }, [navigate])

  // Fetch data full scan dan device overview saat serialNumber tersedia
  useEffect(() => {
    if (serialNumber) {
      fetchResultData()
      fetchDeviceOverview()
    }
  }, [serialNumber])

  const fetchResultData = async () => {
    try {
      // Menyertakan query parameter serial_number dan scan_type sesuai contoh cURL
      const queryParams = new URLSearchParams({
        serial_number: serialNumber,
        scan_type: 'full-scan'
      })
      const url = `${BASE_URL}${RESULT_URL}?${queryParams.toString()}`
      const response = await fetch(url, {
        method: 'GET',
        headers: { accept: 'application/json' }
      })

      if (!response.ok) {
        throw new Error(`Network response was not ok. Status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Result data:', data)

      if (data.status === 'success') {
        const res = data.data
        setResultData(res)

        // Update securityPercentage (konversi ke number)
        if (res.security_percentage) {
          setSecurityPercentage(parseFloat(res.security_percentage))
        }
        // Update lastScanPercentage
        if (res.last_scan_percentage) {
          setLastScanPercentage(res.last_scan_percentage)
        }
        // Update deviceInfo
        setDeviceInfo({
          phone_model: res.phone_model,
          security_patch: res.security_patch_date
        })
      } else {
        console.error('Failed to fetch result data.')
      }
    } catch (error) {
      console.error('Error fetching result data:', error)
    }
  }

  const fetchDeviceOverview = async () => {
    try {
      // Jika diperlukan, tambahkan query parameter (misal: serial_number)
      const url = `${BASE_URL}${DEVICE_IMAGE}`
      const response = await fetch(url, {
        method: 'GET',
        headers: { accept: 'application/json' }
      })

      if (!response.ok) {
        throw new Error(`Network response was not ok. Status: ${response.status}`)
      }
      const data = await response.json()
      console.log('Device Overview Data:', data)
      if (data.status === 200) {
        setDeviceImageData(data.data) // data.data.image berisi URL image
      } else {
        console.error('Failed to fetch device overview.')
      }
    } catch (error) {
      console.error('Error fetching device overview:', error)
    }
  }

  // Filter threats sesuai dengan selectedView
  const filteredThreats =
    resultData?.threats?.filter(
      (threat) => selectedView && threat.type.toLowerCase() === selectedView.toLowerCase()
    ) || []

  // Fungsi untuk sorting (misal, untuk threats)
  const [sortConfig, setSortConfig] = useState({
    key: null,
    direction: 'ascending'
  })

  const handleSort = (key) => {
    let direction = 'ascending'
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending'
    }
    setSortConfig({ key, direction })

    const sortedThreats = [...(resultData?.threats || [])].sort((a, b) => {
      let aValue = a[key]
      let bValue = b[key]

      if (key === 'date_time') {
        aValue = new Date(aValue)
        bValue = new Date(bValue)
        return direction === 'ascending' ? aValue - bValue : bValue - aValue
      } else {
        return direction === 'ascending'
          ? aValue.toString().localeCompare(bValue.toString())
          : bValue.toString().localeCompare(aValue.toString())
      }
    })

    setResultData({ ...resultData, threats: sortedThreats })
  }

  // Handlers untuk modal Delete & Risk
  const openRemoveModal = () => setIsRemoveModalOpen(true)
  const closeRemoveModal = () => setIsRemoveModalOpen(false)

  // const openRiskModal = (risk) => {
  //   const riskData = {
  //     risk: risk,
  //     maliciousCount: 5,
  //     commonCount: 16,
  //     details: [
  //       {
  //         title: 'Android.permission.INTERNET',
  //         description:
  //           'Malware can send your personal data to external servers without your knowledge.'
  //       }
  //     ]
  //   }
  //   setSelectedRiskData(riskData)
  //   setIsRiskModalOpen(true)
  // }

  const closeRiskModal = () => {
    setIsRiskModalOpen(false)
    setSelectedRiskData(null)
  }

  // Fungsi untuk modal Complete
  const openCompleteModal = () => setIsCompleteModalOpen(true)
  const handleCompleteConfirm = () => {
    setIsCompleteModalOpen(false)
    setIsAfterCompleteModalOpen(true)
  }
  const closeAfterCompleteModal = () => setIsAfterCompleteModalOpen(false)

  // Fungsi style persentase
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

  const handleViewClick = (viewType) => {
    if (selectedView === viewType) {
      setSelectedView(null)
      setShowView(false)
    } else {
      setSelectedView(viewType)
      setShowView(true)
    }
  }

  // Fungsi untuk checkbox individual
  const handleCheckboxChange = (packageName) => {
    setCheckedItems((prev) => {
      const newChecked = { ...prev, [packageName]: !prev[packageName] }
      // Jika semua item dalam filteredThreats sudah tercentang, set selectAll ke true, jika tidak false
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

  // Fungsi untuk select all secara global (untuk seluruh threat)
  const handleSelectAllChange = () => {
    // Gunakan data yang ditampilkan (filteredThreats)
    const allSelected = filteredThreats.every((threat) => checkedItems[threat.package_name])
    const updatedCheckedItems = { ...checkedItems }
    filteredThreats.forEach((threat) => {
      updatedCheckedItems[threat.package_name] = !allSelected
    })
    setCheckedItems(updatedCheckedItems)
    setSelectAll(!allSelected)
  }

  // Fungsi untuk delete package berdasarkan threat yang dicentang
  const handleDeleteChecked = async () => {
    const packagesToDelete = Object.keys(checkedItems).filter((pkgName) => checkedItems[pkgName])
    if (packagesToDelete.length === 0) {
      alert('No package selected for deletion.')
      return
    }
    if (!window.confirm('Are you sure you want to delete the selected packages?')) {
      return
    }

    // Jika tipe yang dipilih adalah installer, document/documents, atau application/applications
    if (selectedView && ['installer', 'documents', 'media'].includes(selectedView.toLowerCase())) {
      const sourceDataToDelete = selectedThreats.map((threat) => threat.source_path)
      const url = `${BASE_URL}/v1/delete-files`
      try {
        const response = await fetch(url, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json'
          },
          body: JSON.stringify({ source_data: sourceDataToDelete })
        })
        if (!response.ok) {
          console.error(`Failed to delete files: Status ${response.status}`)
        } else {
          console.log(`Files successfully deleted.`)
        }
        // Set progress delete ke 100% setelah request selesai
        setDeleteProgress(100)
      } catch (error) {
        console.error('Error deleting files:', error)
      }
    } else {
      // Jika bukan salah satu dari tipe di atas, lakukan delete per package
      const total = packagesToDelete.length
      let completed = 0
      for (const packageName of packagesToDelete) {
        const url = `${BASE_URL}/v1/delete-package/${encodeURIComponent(packageName)}`
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
    }
  }

  // Fungsi untuk menangani proses delete (dipanggil ketika modal delete dikonfirmasi)
  const handleRemoveScanning = async () => {
    setIsRemoveModalOpen(false)
    setIsProgressModalOpen(true)
    await handleDeleteChecked()
    await fetchResultData()
  }

  // Fungsi untuk menandai progress delete selesai
  const handleProgressComplete = () => {
    setIsProgressModalOpen(false)
    setBeforePercentage(lastScanPercentage)
  }

  useEffect(() => {
    if (beforePercentage !== null) {
      console.log('Before percentage updated:', beforePercentage)
    }
  }, [beforePercentage])

  return (
    <div
      className={`h-screen w-screen flex flex-col items-center relative font-aldrich`}
      style={{
        backgroundImage: `url(${bgImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Security Percentage Section */}
      <div className="flex flex-col items-center justify-center space-y-2 mt-8 relative">
        <h2 className="text-4xl font-bold text-white">Security Percentage</h2>
        <div
          className="relative flex items-center justify-center"
          style={{
            color: percentageStyle.color,
            width: '300px',
            height: '150px',
            backgroundImage: percentageStyle.backgroundImage,
            backgroundSize: 'contain',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          }}
        >
          <div className="flex flex-col items-center justify-center">
            <h2 className="text-[52px] leading-none">
            {Math.round(securityPercentage) || '-'}%
            </h2>
            <p className="text-[18px]" style={{ color: percentageStyle.color }}>
              {percentageStyle.label}
            </p>
            {beforePercentage !== null && (
              <p className="text-[16px]" style={{ color: percentageStyle.color }}>
                Before: {beforePercentage}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Device Info Section */}
      <div
        className="relative w-[1001px] h-[89px] bg-opacity-90 shadow-inner text-center mb-1 p-6"
        style={{ backgroundImage: `url(${bgModel})` }}
      >
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-12px] left-[-12px] w-6 h-6" />
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-12px] right-[-12px] w-6 h-6"
        />
        <div className="grid grid-cols-3 gap-4 text-white">
          <div>
            <p className="font-semibold text-white">Security Patch</p>
            <p className="text-[#E6FFFD] mt-1">{deviceInfo.security_patch}</p>
          </div>
          <div>
            <p className="font-semibold text-white">Phone Model</p>
            <p className="text-[#E6FFFD] mt-1">{deviceInfo.phone_model}</p>
          </div>
          <div>
            <p className="font-semibold text-white">Last Scan Percentage</p>
            {lastScanPercentage !== null ? (
              <p
                className="text-green-400 mt-1 font-bold"
                style={{ color: percentageStyle.color }}
              >
                {parseFloat(lastScanPercentage).toFixed(0)}% {percentageStyle.label}
              </p>
            ) : (
              <p className="text-white mt-1 font-bold">-</p>
            )}
          </div>
        </div>
      </div>

      {/* Tampilan Utama */}
      {!showView ? (
        <div
          className="w-[1000px] h-[450px] p-6 mt-4 shadow-lg text-white bg-opacity-90 relative"
          style={{ backgroundImage: `url(${bgBorder})` }}
        >
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute top-[-12px] left-[-12px] w-6 h-6"
          />
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute bottom-[-12px] right-[-12px] w-6 h-6"
          />
          <h3 className="text-2xl font-semibold text-[#E6FFFD] mb-4 text-center">Overview</h3>
          <div className="grid grid-cols-7">
            <div className="col-span-3 flex justify-center items-center">
              {deviceImageData ? (
                <img
                  src={deviceImageData.image}
                  alt={deviceImageData.name}
                  className="w-[200px] h-auto p-2"
                />
              ) : (
                <p className="text-white">Loading image...</p>
              )}
            </div>
            <div className="col-span-4 space-y-6 p-6">
              <div className="grid grid-cols-3 gap-4 items-center">
                <span className="font-medium text-[#E6FFFD]">Application</span>
                <span className="text-[#E6FFFD]">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-[#E6FFFD]">
                    <span className="text-[#D3351D]">
                      {resultData?.scan_overview.applications.threats || 0}
                    </span>{' '}
                    /{' '}
                    <span className="text-[#E6FFFD]">
                      {resultData?.scan_overview.applications.scanned || 0}
                    </span>
                  </span>
                  <button
                    className="text-teal-400 underline"
                    onClick={() => handleViewClick('Application')}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 items-center">
                <span className="font-medium text-[#E6FFFD]">Document</span>
                <span className="text-[#E6FFFD]">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-[#E6FFFD]">
                    <span className="text-[#D3351D]">
                      {resultData?.scan_overview.documents.threats || 0}
                    </span>{' '}
                    /{' '}
                    <span className="text-[#E6FFFD]">
                      {resultData?.scan_overview.documents.scanned || 0}
                    </span>
                  </span>
                  <button
                    className="text-teal-400 underline"
                    onClick={() => handleViewClick('Documents')}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 items-center">
                <span className="font-medium text-[#E6FFFD]">Media</span>
                <span className="text-[#E6FFFD]">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-[#E6FFFD]">
                    <span className="text-[#D3351D]">
                      {resultData?.scan_overview.media.threats || 0}
                    </span>{' '}
                    /{' '}
                    <span className="text-[#E6FFFD]">
                      {resultData?.scan_overview.media.scanned || 0}
                    </span>
                  </span>
                  <button
                    className="text-teal-400 underline"
                    onClick={() => handleViewClick('Media')}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 items-center">
                <span className="font-medium text-[#E6FFFD]">Installer</span>
                <span className="text-[#E6FFFD]">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-[#E6FFFD]">
                    {resultData?.scan_overview.installer.threats || 0}
                  </span>
                  <button
                    className="text-teal-400 underline"
                    onClick={() => handleViewClick('Installer')}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="border-b border-gray-400 my-4"></div>
              <div className="flex justify-between items-center">
                <span className="font-medium text-[#E6FFFD]">Threat</span>
                <span className="text-[#D3351D] font-bold animate-blink bg-slate-600">
                  {resultData?.total_threats || 0} Threat
                </span>
              </div>
            </div>
          </div>
          <div className="mt-6 text-center">
            <p className="text-[#E6FFFD]">
              Previous scan history found on this device. Would you like to view{' '}
              <Link to="/history" className="text-teal-400 underline">
                History
              </Link>
              ?
            </p>
          </div>
        </div>
      ) : (
        <div className="flex space-x-6 mt-4 w-[1001px]">
          <div
            className="w-[347px] h-[450px] p-4 text-white"
            style={{
              backgroundImage: `url(${overview})`,
              backgroundSize: 'contain',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat'
            }}
          >
            <h3 className="text-2xl font-semibold mb-10">Overview</h3>
            <div className="space-y-10">
              <div className="flex justify-between items-center">
                <span className="text-[#E6FFFD]">Application :</span>
                <div className="flex items-center">
                  <span className="text-[#E6FFFD]">
                    {resultData?.scan_overview?.applications?.threats || 0}/
                    {resultData?.scan_overview?.applications?.scanned || 0}
                  </span>{' '}
                  <button
                    className="ml-4 text-teal-400 underline"
                    onClick={() => handleViewClick('Application')}
                    style={{
                      color: selectedView === 'Application' ? '#05564F' : '#4FD1C5'
                    }}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#E6FFFD]">Document :</span>
                <div className="flex items-center">
                  <span className="text-[#E6FFFD]">
                    {resultData?.scan_overview?.documents?.threats || 0}/
                    {resultData?.scan_overview?.documents?.scanned || 0}
                  </span>{' '}
                  <button
                    className="ml-4 text-teal-400 underline"
                    onClick={() => handleViewClick('Documents')}
                    style={{
                      color: selectedView === 'Documents' ? '#05564F' : '#4FD1C5'
                    }}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#E6FFFD]">Media :</span>
                <div className="flex items-center">
                  <span className="text-[#E6FFFD]">
                    {resultData?.scan_overview?.media?.threats || 0}/
                    {resultData?.scan_overview?.media?.scanned || 0}
                  </span>{' '}
                  <button
                    className="ml-4 text-teal-400 underline"
                    onClick={() => handleViewClick('Media')}
                    style={{
                      color: selectedView === 'Media' ? '#05564F' : '#4FD1C5'
                    }}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#E6FFFD]">Installer :</span>
                <div className="flex items-center">
                  <span className="text-[#E6FFFD]">
                    {resultData?.scan_overview?.installer?.threats || 0}/
                    {resultData?.scan_overview?.installer?.scanned || 0}
                  </span>{' '}
                  <button
                    className="ml-4 text-teal-400 underline"
                    onClick={() => handleViewClick('Installer')}
                    style={{
                      color: selectedView === 'Installer' ? '#05564F' : '#4FD1C5'
                    }}
                  >
                    View
                  </button>
                </div>
              </div>
              <div className="flex justify-between items-center mt-4 border-t border-gray-700 pt-4">
                <span className="text-[#E6FFFD]">Threat :</span>
                <span className="text-[#E6FFFD]">{resultData?.total_threats || 0}</span>
              </div>
            </div>
          </div>

          {/* Right Side: View */}
          <div
            className="w-[630px] h-[450px] p-4 bg-gray-800 text-white relative"
            style={{
              backgroundImage: `url(${viewSection})`,
              backgroundSize: 'contain',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat'
            }}
          >
            <h3 className="text-2xl font-semibold mb-4">{selectedView || 'View'}</h3>
            <div className="w-full bg-[#00B3A2] grid grid-cols-12 p-2 items-center text-sm text-black">
              <div
                className="col-span-5 flex items-center gap-1 cursor-pointer"
                onClick={() => handleSort('date_time')}
              >
                Date Time <span>↓</span>
              </div>
              <div
                className="col-span-5 flex items-center gap-1 cursor-pointer"
                onClick={() => handleSort('name')}
              >
                Name <span>↓</span>
              </div>
              <div className="col-span-2 flex justify-end">
                {/* Checkbox for select all secara global */}
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
            <div className="space-y-[1px] max-h-[250px] overflow-y-auto">
              {filteredThreats.length > 0 ? (
                filteredThreats.map((threat, index) => (
                  <div
                    key={index}
                    className="w-full grid grid-cols-12 p-2 items-center border-b border-[#1A1A1A] text-white"
                  >
                    <div className="col-span-5">
                      {threat.date_time ? new Date(threat.date_time).toLocaleString() : '-'}
                    </div>
                    <div className="flex items-center  col-span-7 justify-between">
                      <div
                        className="flex items-center gap-4 overflow-hidden whitespace-nowrap text-ellipsis"
                        style={{ maxWidth: '200px' }}
                      >
                        <span>{threat.name}</span>
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
                ))
              ) : (
                <p className="text-white text-center mt-4">No threats found.</p>
              )}
            </div>
            <div className="border-b border-gray-400 mt-7 mb-5"></div>
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
                <span className="relative z-10">DELETE</span>
                <div className="absolute inset-0 bg-red-900 opacity-0 hover:opacity-30 transition-opacity"></div>
              </button>
            </div>
            {/* Remove Modal */}
            {isRemoveModalOpen && (
              <RemoveModal
                onClose={closeRemoveModal}
                onConfirm={handleRemoveScanning}
                onProgressComplete={handleProgressComplete}
              />
            )}
            {/* Delete Progress Modal */}
            {isProgressModalOpen && (
              <DeleteProgressModal
                progress={deleteProgress}
                onClose={() => setIsProgressModalOpen(false)}
                onProgressComplete={handleProgressComplete}
              />
            )}

            {/* Risk Modal */}
            <RiskModal
              isOpen={isRiskModalOpen}
              onClose={closeRiskModal}
              riskData={selectedRiskData}
            />
          </div>
        </div>
      )}

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

        {isCompleteModalOpen && (
          <CompleteModal
            onClose={() => setIsCompleteModalOpen(false)}
            onConfirm={handleCompleteConfirm}
          />
        )}

        {isAfterCompleteModalOpen && <AfterCompleteModal onClose={closeAfterCompleteModal} />}
      </div>
    </div>
  )
}

export default ResultFullScanPage
