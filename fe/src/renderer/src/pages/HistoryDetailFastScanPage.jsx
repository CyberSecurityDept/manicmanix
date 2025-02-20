import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'
import bgImage from '../assets/bg-darkmode.png'
import plusSign from '../assets/plus-sign.svg'
import bgGood from '../assets/border/percentage-good.svg'
import bgAverage from '../assets/border/percentage-average.svg'
import bgBad from '../assets/border/percentage-bad.svg'
import backIcon from '../assets/back-Icon.svg'

// Mengambil BASE_URL dari environment variables
const BASE_URL = import.meta.env.VITE_BASE_URL

const HistoryDetailFastScanPage = () => {
  const { serialNumber, timeStamp } = useParams()
  const navigate = useNavigate()

  // State untuk loading data
  const [loading, setLoading] = useState(false)

  // State untuk security percentage dan related
  const [securityPercentage, setSecurityPercentage] = useState(0)
  const [lastScanPercentage, setLastScanPercentage] = useState(null)
  const [beforePercentage, setBeforePercentage] = useState(null)

  // State untuk threat list (jika ada) dan checkbox (jika nanti diperlukan)
  const [filteredThreats, setFilteredThreats] = useState([])
  const [selectAll, setSelectAll] = useState(false)
  const [checkedItems, setCheckedItems] = useState({})
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

  // State untuk device info
  const [deviceInfo, setDeviceInfo] = useState({ phone_model: '', os_version: '' })

  // Fungsi untuk menentukan style percentage berdasarkan nilai
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

  const percentageStyle = getPercentageStyle(securityPercentage || 0)
  const lastPercentageStyle =
    lastScanPercentage !== null ? getPercentageStyle(lastScanPercentage) : {}

  // Fungsi sorting untuk grid view (jika threat list tersedia)
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

  const handleSelectAllChange = (e) => {
    const isChecked = e.target.checked
    setSelectAll(isChecked)
    const newCheckedItems = {}
    filteredThreats.forEach((threat) => {
      newCheckedItems[threat.package_name] = isChecked
    })
    setCheckedItems(newCheckedItems)
  }

  const handleCheckboxChange = (packageName) => {
    setCheckedItems((prev) => ({
      ...prev,
      [packageName]: !prev[packageName]
    }))
  }

  // Fetch data dari endpoint fast-scan
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Sesuaikan endpoint dengan yang Anda gunakan.
        const response = await fetch(
          `${BASE_URL}/v1/history_fast_scan/${serialNumber}/${timeStamp}`
        )
        const data = await response.json()
        // Update security percentage (menghapus '%' dan mengkonversinya ke angka)
        const secPercent = parseFloat(data.security_percentage.replace('%', ''))
        setSecurityPercentage(secPercent)
        // Jika last_scan_percentage tersedia, update nilainya; jika tidak, biarkan null
        if (data.last_scan_percentage) {
          const lastPercent = parseFloat(data.last_scan_percentage.replace('%', ''))
          setLastScanPercentage(lastPercent)
        } else {
          setLastScanPercentage(null)
        }
        // Update device info berdasarkan data
        setDeviceInfo({
          phone_model: data.model,
          os_version: data.security_patch
        })
        // Jika endpoint fast-scan tidak menyediakan daftar threat, set filteredThreats ke array kosong.
        setFilteredThreats([])
        setBeforePercentage(null)
      } catch (error) {
        console.error('Error fetching fast-scan detail:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [serialNumber, timeStamp])

  return (
    <div
      className="h-screen w-screen flex flex-col justify-center items-center relative font-aldrich"
      style={{ backgroundImage: `url(${bgImage})`, backgroundSize: 'cover' }}
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
            <h2 className="text-[52px] leading-none">{Math.round(securityPercentage) || 0}%</h2>
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
                <p className="mt-1 font-bold" style={{ color: lastPercentageStyle.color }}>
                  {lastScanPercentage}% {lastPercentageStyle.label}
                </p>
              ) : (
                <p className="text-white mt-1 font-bold">-</p>
              )}
            </div>
          </div>
        </div>

        {/* View Section */}
        <div className="w-full h-[450px] p-4 border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] text-white relative mt-4">
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
              <div className="space-y-[1px]">
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
            <p className="text-center">No threat data available.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default HistoryDetailFastScanPage
