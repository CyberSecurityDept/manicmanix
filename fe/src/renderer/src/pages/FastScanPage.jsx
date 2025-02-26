import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import modalBackground from '../assets/border/bawah-scanning.svg'
import ArrowPattern from '../components/ArrowPattern'
import CancelModal from '../components/modal/Cancel'
import ReconnectModel from '../components/modal/Reconnect'
import bgImage from '../assets/bg-darkmode.png'
import plusSign from '../assets/plus-sign.svg'
import buttonViewMore from '../assets/border/view-more.svg'
import buttonCancel from '../assets/border/cancel.svg'

// Fungsi helper untuk memformat datetime
const formatDate = (datetimeString) => {
  if (!datetimeString || !datetimeString.includes(' ')) {
    return 'Unknown'
  }
  const [datePart] = datetimeString.split(' ')
  const [year, month, day] = datePart.split('-')
  return `${day}/${month}/${year}`
}

const formatTime = (datetimeString) => {
  if (!datetimeString || !datetimeString.includes(' ')) {
    return 'Unknown'
  }
  const [, timePart] = datetimeString.split(' ')
  const [hours, minutes] = timePart.split(':')
  return `${hours}:${minutes}`
}

// Mengambil BASE_URL dari environment variables
const BASE_URL = import.meta.env.VITE_BASE_URL

const FastScanPage = () => {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [progress, setProgress] = useState(0)
  const [logData, setLogData] = useState([])
  const [scanComplete, setScanComplete] = useState(false)
  const [showAllLogs, setShowAllLogs] = useState(false)
  const [serialNumber, setSerialNumber] = useState(null)
  // State untuk modal reconnect
  const [showReconnectModal, setShowReconnectModal] = useState(false)
  const [reconnectTriggered, setReconnectTriggered] = useState(false)

  const openModal = () => setIsModalOpen(true)
  const closeModal = () => setIsModalOpen(false)

  const handleCancelScanning = () => {
    setIsModalOpen(false)
    navigate('/')
  }

  // Ambil serial_number dari localStorage sekali
  useEffect(() => {
    const savedSerialNumber = localStorage.getItem('serial_number')
    if (savedSerialNumber) {
      setSerialNumber(savedSerialNumber)
    } else {
      console.error('Serial number not found in localStorage.')
      navigate('/') // Pindah ke halaman lain jika serial_number tidak ada
    }
  }, [navigate])

  // Interval untuk cek progress fast scan
  useEffect(() => {
    let interval // Simpan reference interval

    const fetchScanProgress = async () => {
      if (!serialNumber) return // Tunggu sampai serialNumber tersedia
      try {
        const response = await fetch(`${BASE_URL}/v1/fastscan-progress/${serialNumber}`)
        const data = await response.json()

        if (data.status === 200) {
          setProgress(parseInt(data.data.scan_percentage))
          setScanComplete(data.data.scan_complete)
          setLogData(data.data.log_process)

          // Jika terdapat error reconnect dan belum pernah dipicu, tampilkan modal reconnect
          if (
            !reconnectTriggered &&
            data.data.log_process.some(
              (entry) =>
                entry.log.includes(
                  'Unable to connect to the device over USB. Try to unplug, plug the device and start again.'
                ) || entry.log.includes('No device found. Make sure it is connected and unlocked.')
            )
          ) {
            setReconnectTriggered(true)
            setShowReconnectModal(true)
            // Setelah 5 detik, tutup modal reconnect dan navigasikan ke halaman device-info
            setTimeout(() => {
              setShowReconnectModal(false)
              navigate('/device-info')
            }, 5000)
          }

          // Jika progress sudah 100%, hentikan interval
          if (data.data.scan_percentage === 100) {
            clearInterval(interval)
          }
        } else {
          console.error('Failed to fetch scan progress')
        }
      } catch (error) {
        console.error('Error fetching scan progress:', error)
      }
    }

    // Mulai interval jika serialNumber sudah ada
    if (serialNumber) {
      const delay = setTimeout(() => {
        interval = setInterval(fetchScanProgress, 3000) // Panggil API setiap 3 detik
      }, 2000) // Delay 2 detik sebelum memulai fetch API

      return () => {
        clearInterval(interval)
        clearTimeout(delay)
      }
    }
  }, [serialNumber, reconnectTriggered, navigate])

  // Pindah ke halaman hasil fast scan jika progress 100%
  useEffect(() => {
    if (progress === 100) {
      const delayTimeout = setTimeout(() => {
        navigate('/result-fast')
      }, 1000)
      return () => clearTimeout(delayTimeout)
    }
  }, [progress, navigate])

  return (
    <div
      className="h-screen w-screen flex flex-col justify-center items-center relative text-white font-aldrich"
      style={{
        backgroundColor: '#000',
        backgroundImage: `url(${bgImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      {/* Modal Reconnect */}
      {showReconnectModal && <ReconnectModel onClose={() => setShowReconnectModal(false)} />}

      <div className="text-center">
        <h1 className="text-2xl font-bold">
          Please do not unplug your device. This process will take a little time.
        </h1>
      </div>

      <div className="pt-4 flex flex-col items-center w-[1022px]">
        <h2 className="text-3xl font-bold mb-2" style={{ color: '#00FFE7' }}>
          {progress}% {scanComplete && ' - Scan Complete!'}
        </h2>
        <div className="border-2 border-teal-500 p-2 shadow-lg bg-black w-full">
          <ArrowPattern progress={progress} />
        </div>
      </div>

      <div className="w-[1022px]">
        <div
          className="relative mt-8 p-6"
          style={{
            backgroundImage: `url(${modalBackground})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            minHeight: '385px'
          }}
        >
          <img src={plusSign} alt="Plus Sign" className="absolute top-[0px] left-[-13px] w-6 h-6" />
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute bottom-[0px] right-[-13px] w-6 h-6"
          />

          <div className="flex flex-col items-center justify-center">
            <div
              className={`relative text-center p-4 bg-[#091310] w-full min-h-[200px] ${
                showAllLogs ? 'max-h-96 overflow-y-auto' : 'max-h-60 overflow-hidden'
              }`}
              style={{
                transition: 'max-height 0.1s ease-in-out',
                overflowY: 'auto',
                overflowX: 'hidden'
              }}
            >
              {logData.length === 0 ? (
                <p className="text-center text-gray-500">No log data available</p>
              ) : (
                <div className="space-y-2 w-full">
                  {logData
                    .slice()
                    .reverse()
                    .map((log, i) => {
                      const dateFormatted = formatDate(log.datetime)
                      const timeFormatted = formatTime(log.datetime)
                      return (
                        <div key={i} className="flex py-2 px-4">
                          {/* Kolom Date */}
                          <span className="w-[120px] text-left">{dateFormatted}</span>
                          {/* Kolom Time */}
                          <span className="w-[60px] text-center whitespace-nowrap">
                            {timeFormatted}
                          </span>
                          {/* Kolom Log */}
                          <span className="flex-1 text-right whitespace-normal break-words">
                            {log.log}
                          </span>
                        </div>
                      )
                    })}
                </div>
              )}
            </div>

            <div className="flex justify-center mt-5">
              <button
                className="w-[223px] h-[43px] text-xl font-bold bg-transparent shadow-lg flex items-center justify-center relative"
                style={{
                  backgroundImage: `url(${buttonViewMore})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
                onClick={() => setShowAllLogs(!showAllLogs)}
              >
                {showAllLogs ? 'VIEW LESS' : 'VIEW MORE'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-center mt-6">
        <button
          className="w-[389px] h-[51px] text-xl font-bold bg-transparent shadow-lg flex items-center justify-center relative"
          style={{
            backgroundImage: `url(${buttonCancel})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
          onClick={openModal}
        >
          CANCEL SCANNING
        </button>
      </div>

      {isModalOpen && <CancelModal onClose={closeModal} onConfirm={handleCancelScanning} />}
    </div>
  )
}

export default FastScanPage
