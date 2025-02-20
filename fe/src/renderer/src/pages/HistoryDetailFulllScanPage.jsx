import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import '../styles/Checkbox.css'
import bgImage from '../assets/bg-darkmode.png'
import deviceImage from '../assets/samsung galaxy s24 ultra 5g sm s928 0.jpg'
import overview from '../assets/border/overview-section.svg'
import viewSection from '../assets/border/view-section.svg'
import bgModel from '../assets/border/percentage-section.svg'
import bgBorder from '../assets/border/overview-border.svg'
import bgGood from '../assets/border/percentage-good.svg'
import bgAverage from '../assets/border/percentage-average.svg'
import bgBad from '../assets/border/percentage-bad.svg'
import plusSign from '../assets/plus-sign.svg'
import backIcon from '../assets/back-Icon.svg'

const BASE_URL = import.meta.env.VITE_BASE_URL

const HistoryDetailFullScanPage = () => {
  const navigate = useNavigate()
  const { serialNumber, timeStamp } = useParams()

  // State untuk data detail endpoint
  const [detailData, setDetailData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // State untuk daftar threats
  const [threats, setThreats] = useState([])
  const [threatSortConfig, setThreatSortConfig] = useState({
    key: null,
    direction: 'ascending'
  })

  // State untuk toggle tampilan overview vs. list threat
  const [selectedView, setSelectedView] = useState(null)
  const [showView, setShowView] = useState(false)
  const [beforePercentage, setBeforePercentage] = useState(null)
  const [isRiskModalOpen, setIsRiskModalOpen] = useState(false)
  const [selectedRiskData, setSelectedRiskData] = useState(null)

  // Fungsi untuk menutup modal risiko (jika diperlukan)
  const closeRiskModal = () => {
    setIsRiskModalOpen(false)
    setSelectedRiskData(null)
  }

  // Fungsi untuk menentukan style berdasarkan persentase
  const getPercentageStyle = (percentage) => {
    if (percentage >= 90 && percentage <= 98) {
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

  // Fetch data detail full-scan
  useEffect(() => {
    const fetchDetail = async () => {
      setIsLoading(true)
      try {
        const endpoint = `${BASE_URL}/v1/history-fullscan-detail/full-scan/${serialNumber}/${timeStamp}`
        const response = await fetch(endpoint)
        const data = await response.json()
        setDetailData(data)
        if (data && data.threats) {
          setThreats(data.threats)
        }
      } catch (error) {
        console.error('Error fetching detail data:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchDetail()
  }, [serialNumber, timeStamp])

  // Konversi nilai persentase (misalnya "50.00%") menjadi angka
  const scanPercentage = detailData
    ? parseFloat(detailData.security_percentage.replace('%', ''))
    : 0
  const lastScanPercentage = detailData
    ? parseFloat(detailData.last_scan_percentage.replace('%', ''))
    : 0

  const percentageStyle = getPercentageStyle(scanPercentage)
  const lastPercentageStyle = getPercentageStyle(lastScanPercentage)

  // Fungsi toggle tampilan overview vs. daftar threat
  const handleViewClick = (viewType) => {
    if (selectedView === viewType) {
      setSelectedView(null)
      setShowView(false)
    } else {
      setSelectedView(viewType)
      setShowView(true)
    }
  }

  // Fungsi sorting untuk daftar threats
  const handleThreatSort = (key) => {
    let direction = 'ascending'
    if (threatSortConfig.key === key && threatSortConfig.direction === 'ascending') {
      direction = 'descending'
    }
    setThreatSortConfig({ key, direction })
    const sorted = [...threats].sort((a, b) => {
      // Jika key adalah "date", gunakan properti "date_time"
      const field = key === 'date' ? 'date_time' : key
      if (a[field] < b[field]) return direction === 'ascending' ? -1 : 1
      if (a[field] > b[field]) return direction === 'ascending' ? 1 : -1
      return 0
    })
    setThreats(sorted)
  }

  if (isLoading) {
    return (
      <div
        className="h-screen w-screen flex justify-center items-center text-white font-aldrich"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <p>Loading...</p>
      </div>
    )
  }

  if (!detailData) {
    return (
      <div
        className="h-screen w-screen flex justify-center items-center text-white font-aldrich"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <p>Data tidak ditemukan</p>
      </div>
    )
  }

  return (
    <div
      className="h-screen w-screen flex flex-col justify-center items-center relative font-aldrich"
      style={{
        backgroundImage: `url(${bgImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Tombol Back */}
      <button
        className="absolute top-6 left-6 flex items-center justify-center focus:outline-none group transition-all duration-300"
        onClick={() => navigate('/history')}
        style={{
          width: '68px',
          height: '68px',
          backgroundColor: 'transparent'
        }}
      >
        <img src={backIcon} alt="Back Icon" className="w-10 h-10" />
      </button>

      {/* Security Percentage Section */}
      <div className="flex flex-col items-center justify-center space-y-2 mt-2 relative">
        <div>
          <h2 className="text-4xl font-bold text-white">Security Percentage</h2>
        </div>
        <div
          className="relative flex items-center justify-center"
          style={{
            color: percentageStyle.color,
            width: '300px',
            height: '180px',
            backgroundImage: percentageStyle.backgroundImage,
            backgroundSize: 'contain',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <div className="flex flex-col items-center justify-center">
            <h2 className="text-[52px] leading-none">
              {detailData.security_percentage}
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

      {/* Security Patch, Phone Model, Last Scan Percentage Card */}
      <div
        className="relative w-[1001px] h-[89px] bg-opacity-90 shadow-inner text-center mb-1 p-6"
        style={{ backgroundImage: `url(${bgModel})` }}
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

        <div className="grid grid-cols-3 gap-4 text-white">
          <div>
            <p className="font-semibold text-gray-400">Security Patch</p>
            <p className="text-gray-100 mt-1">{detailData.security_patch}</p>
          </div>
          <div>
            <p className="font-semibold text-gray-400">Phone Model</p>
            <p className="text-gray-100 mt-1">{detailData.model}</p>
          </div>
          <div>
            <p className="font-semibold text-gray-400">Last Scan Percentage</p>
            <p
              className="text-green-400 mt-1 font-bold"
              style={{ color: lastPercentageStyle.color }}
            >
              {detailData.last_scan_percentage} {lastPercentageStyle.label}
            </p>
          </div>
        </div>
      </div>

      {/* Tampilan Overview / Detail Threat */}
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

          <h3 className="text-2xl font-semibold text-gray-100 mb-6 text-center">
            Overview
          </h3>

          <div className="grid grid-cols-7">
            <div className="col-span-3 flex justify-center items-center">
              <img
                src={deviceImage}
                alt="Phone Model"
                className="w-[259px] h-auto"
              />
            </div>

            <div className="col-span-4 space-y-4 p-6">
              <div className="grid grid-cols-3 gap-4 items-center">
                <span className="font-medium text-[#E6FFFD]">Application</span>
                <span className="text-gray-100">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-gray-100">
                    {detailData.scan_overview.applications.threats}/
                    {detailData.scan_overview.applications.scanned}
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
                <span className="text-gray-100">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-gray-100">
                    {detailData.scan_overview.documents.threats}/
                    {detailData.scan_overview.documents.scanned}
                  </span>
                  <button
                    className="text-teal-400 underline"
                    onClick={() => handleViewClick('Documents')}
                  >
                    View
                  </button>
                </div>
              </div>

              {/* Label "Media" sebagai pengganti "Accessibility" */}
              <div className="grid grid-cols-3 gap-4 items-center">
                <span className="font-medium text-[#E6FFFD]">Media</span>
                <span className="text-gray-100">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-gray-100">
                    {detailData.scan_overview.media.threats}/
                    {detailData.scan_overview.media.scanned}
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
                <span className="text-gray-100">:</span>
                <div className="flex items-center justify-between">
                  <span className="text-gray-100">
                    {detailData.scan_overview.installer.threats}/
                    {detailData.scan_overview.installer.scanned}
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
                <span className="text-red-500 font-bold ">
                  {detailData.total_threats} Threat
                </span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Tampilan list Threat (View) ketika tombol View ditekan
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
                  <span className="text-gray-100">
                    {detailData.scan_overview.applications.threats}/
                    {detailData.scan_overview.applications.scanned}
                  </span>
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
                  <span className="text-gray-100">
                    {detailData.scan_overview.documents.threats}/
                    {detailData.scan_overview.documents.scanned}
                  </span>
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
                  <span className="text-gray-100">
                    {detailData.scan_overview.media.threats}/
                    {detailData.scan_overview.media.scanned}
                  </span>
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
                  <span className="text-gray-100">
                    {detailData.scan_overview.installer.threats}/
                    {detailData.scan_overview.installer.scanned}
                  </span>
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
                <span className="text-gray-100">{detailData.total_threats}</span>
              </div>
            </div>
          </div>

          {/* Right Side: Tabel Threats */}
          <div
            className="w-[630px] h-[450px] p-4 bg-gray-800 text-white relative"
            style={{
              backgroundImage: `url(${viewSection})`,
              backgroundSize: 'contain',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat'
            }}
          >
            <h3 className="text-2xl font-semibold mb-4">
              {selectedView ? selectedView : 'Threats'}
            </h3>
            <div className="w-full bg-[#00B3A2] grid grid-cols-12 p-2 items-center text-sm text-black">
              <div
                className="col-span-5 flex items-center gap-1 cursor-pointer"
                onClick={() => handleThreatSort('date')}
              >
                Date Time <span>↓</span>
              </div>
              <div
                className="col-span-5 flex items-center gap-1 cursor-pointer"
                onClick={() => handleThreatSort('name')}
              >
                Name <span>↓</span>
              </div>
            </div>
            <div className="space-y-1 mt-2">
              {threats.length > 0 ? (
                threats.map((threat, index) => (
                  <div
                    key={index}
                    className="grid grid-cols-3 border-b border-[#EAECF0] p-2 text-white"
                  >
                    <span>{new Date(threat.date_time).toLocaleString()}</span>
                    <div className="flex justify-center items-center">
                      <span>{threat.name}</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-center">No threat data available.</p>
              )}
            </div>
            <div className="border-b border-gray-400 mt-7 mb-5"></div>
          </div>
        </div>
      )}
    </div>
  )
}

export default HistoryDetailFullScanPage
